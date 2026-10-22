"""
routes/admin.py - routes used ONLY by the admin website.

Every route here (except login) is protected by @admin_required,
so a visitor without a valid token gets "401 Login required".

  POST   /api/admin/login                    log in, get a token
  GET    /api/admin/stats                    numbers for the dashboard
  GET    /api/admin/properties               all properties (available + sold)
  GET    /api/admin/properties/<id>          one property (for the edit form)
  POST   /api/admin/properties               add a property
  PUT    /api/admin/properties/<id>          edit a property
  DELETE /api/admin/properties/<id>          delete a property
  PATCH  /api/admin/properties/<id>/status   mark available / sold (saves buyer record)
  GET    /api/admin/enquiries                enquiries from visitors
  DELETE /api/admin/enquiries/<id>           delete an enquiry
  GET    /api/admin/sales                    buy records
"""
import time

from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash

import db
from auth import create_token, admin_required
from validators import clean_property, is_valid_email, to_number

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")

# ---------------------------------------------------------------------------
# Login (with a small limit on wrong passwords)
# ---------------------------------------------------------------------------
MAX_FAILED_LOGINS = 5          # wrong attempts allowed ...
LOCK_SECONDS = 300             # ... within this many seconds
failed_logins = {}             # ip address -> list of times of wrong attempts


def too_many_attempts(ip):
    """True if this address failed to log in too many times recently."""
    now = time.time()
    recent = [t for t in failed_logins.get(ip, []) if now - t < LOCK_SECONDS]
    failed_logins[ip] = recent
    return len(recent) >= MAX_FAILED_LOGINS


@admin_bp.post("/login")
def login():
    ip = request.remote_addr or "unknown"
    if too_many_attempts(ip):
        return jsonify(error="Too many attempts. Try again in a few minutes."), 429

    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    admin = db.query_one("SELECT * FROM admins WHERE username = ?", (username,))
    # Same message for "no such user" and "wrong password" (does not help attackers)
    if admin is None or not check_password_hash(admin["password_hash"], password):
        failed_logins.setdefault(ip, []).append(time.time())
        return jsonify(error="Wrong username or password"), 401

    failed_logins.pop(ip, None)
    return jsonify(token=create_token(admin["id"], admin["username"]),
                   username=admin["username"])


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------
@admin_bp.get("/stats")
@admin_required
def stats():
    """The four numbers shown on the dashboard."""
    row = db.query_one("""
        SELECT COUNT(*)                                          AS total,
               COALESCE(SUM(status = 'available'), 0)            AS available,
               COALESCE(SUM(status = 'sold'), 0)                 AS sold
        FROM properties
    """)
    row["enquiries"] = db.query_one("SELECT COUNT(*) AS n FROM enquiries")["n"]
    row["sales_total"] = db.query_one(
        "SELECT COALESCE(SUM(sale_price), 0) AS s FROM sales")["s"]
    return jsonify(row)


# ---------------------------------------------------------------------------
# Properties: list, view, add, edit, delete
# ---------------------------------------------------------------------------
def save_images(property_id, image_urls):
    """Replace all photo links of a property with the given list."""
    conn = db.get_db()
    conn.execute("DELETE FROM property_images WHERE property_id = ?", (property_id,))
    for url in image_urls:
        conn.execute(
            "INSERT INTO property_images (property_id, image_url) VALUES (?, ?)",
            (property_id, url),
        )
    conn.commit()


@admin_bp.get("/properties")
@admin_required
def list_properties():
    rows = db.query_all("""
        SELECT p.*,
               (SELECT image_url FROM property_images
                 WHERE property_id = p.id ORDER BY id LIMIT 1) AS cover_image
        FROM properties p
        ORDER BY p.id DESC
    """)
    return jsonify(rows)


@admin_bp.get("/properties/<int:property_id>")
@admin_required
def get_property(property_id):
    prop = db.query_one("SELECT * FROM properties WHERE id = ?", (property_id,))
    if prop is None:
        return jsonify(error="Property not found"), 404
    images = db.query_all(
        "SELECT image_url FROM property_images WHERE property_id = ? ORDER BY id",
        (property_id,))
    prop["images"] = [row["image_url"] for row in images]
    return jsonify(prop)


@admin_bp.post("/properties")
@admin_required
def add_property():
    clean, error = clean_property(request.get_json(silent=True) or {})
    if error:
        return jsonify(error=error), 400

    new_id = db.execute(
        """INSERT INTO properties
           (title, type, price, area_sqft, city, address, bedrooms, description)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (clean["title"], clean["type"], clean["price"], clean["area_sqft"],
         clean["city"], clean["address"], clean["bedrooms"], clean["description"]),
    )
    save_images(new_id, clean["images"])
    return jsonify(id=new_id, message="Property added"), 201


@admin_bp.put("/properties/<int:property_id>")
@admin_required
def edit_property(property_id):
    if not db.query_one("SELECT id FROM properties WHERE id = ?", (property_id,)):
        return jsonify(error="Property not found"), 404

    clean, error = clean_property(request.get_json(silent=True) or {})
    if error:
        return jsonify(error=error), 400

    db.execute(
        """UPDATE properties
           SET title = ?, type = ?, price = ?, area_sqft = ?, city = ?,
               address = ?, bedrooms = ?, description = ?
           WHERE id = ?""",
        (clean["title"], clean["type"], clean["price"], clean["area_sqft"],
         clean["city"], clean["address"], clean["bedrooms"], clean["description"],
         property_id),
    )
    save_images(property_id, clean["images"])
    return jsonify(message="Property updated")


@admin_bp.delete("/properties/<int:property_id>")
@admin_required
def delete_property(property_id):
    """
    Properties that were SOLD cannot be deleted, because the buy record
    must be kept. (Mark it available again first if it was a mistake.)
    """
    if db.query_one("SELECT id FROM sales WHERE property_id = ?", (property_id,)):
        return jsonify(error="This property has a sale record, so it cannot be deleted"), 409
    db.execute("DELETE FROM properties WHERE id = ?", (property_id,))
    return jsonify(message="Property deleted")


# ---------------------------------------------------------------------------
# Status change: available <-> sold (this also creates / removes the buy record)
# ---------------------------------------------------------------------------
@admin_bp.patch("/properties/<int:property_id>/status")
@admin_required
def change_status(property_id):
    prop = db.query_one("SELECT * FROM properties WHERE id = ?", (property_id,))
    if prop is None:
        return jsonify(error="Property not found"), 404

    data = request.get_json(silent=True) or {}
    new_status = data.get("status")
    conn = db.get_db()

    if new_status == "sold":
        if prop["status"] == "sold":
            return jsonify(error="Property is already sold"), 409

        buyer_name = (data.get("buyer_name") or "").strip()
        buyer_email = (data.get("buyer_email") or "").strip()
        if not buyer_name:
            return jsonify(error="Buyer name is required"), 400
        if buyer_email and not is_valid_email(buyer_email):
            return jsonify(error="Buyer email is not valid"), 400
        # If no sale price is typed, use the listing price
        sale_price = to_number(data.get("sale_price"))
        if sale_price is None:
            sale_price = prop["price"]

        # Two changes that must succeed together: save the sale + update the status
        conn.execute(
            """INSERT INTO sales (property_id, buyer_name, buyer_email, buyer_phone, sale_price)
               VALUES (?, ?, ?, ?, ?)""",
            (property_id, buyer_name, buyer_email,
             (data.get("buyer_phone") or "").strip(), sale_price),
        )
        conn.execute("UPDATE properties SET status = 'sold' WHERE id = ?", (property_id,))
        conn.commit()
        return jsonify(message="Marked as sold and sale recorded")

    if new_status == "available":
        # Used to undo a mistake: the sale record is removed too
        conn.execute("DELETE FROM sales WHERE property_id = ?", (property_id,))
        conn.execute("UPDATE properties SET status = 'available' WHERE id = ?", (property_id,))
        conn.commit()
        return jsonify(message="Marked as available again")

    return jsonify(error="Status must be 'available' or 'sold'"), 400


# ---------------------------------------------------------------------------
# Enquiries and sales records
# ---------------------------------------------------------------------------
@admin_bp.get("/enquiries")
@admin_required
def list_enquiries():
    rows = db.query_all("""
        SELECT e.*, p.title AS property_title
        FROM enquiries e
        LEFT JOIN properties p ON p.id = e.property_id
        ORDER BY e.id DESC
    """)
    return jsonify(rows)


@admin_bp.delete("/enquiries/<int:enquiry_id>")
@admin_required
def delete_enquiry(enquiry_id):
    db.execute("DELETE FROM enquiries WHERE id = ?", (enquiry_id,))
    return jsonify(message="Enquiry deleted")


@admin_bp.get("/sales")
@admin_required
def list_sales():
    rows = db.query_all("""
        SELECT s.*, p.title AS property_title, p.type AS property_type,
               p.city AS property_city, p.price AS listed_price
        FROM sales s
        JOIN properties p ON p.id = s.property_id
        ORDER BY s.id DESC
    """)
    return jsonify(rows)
