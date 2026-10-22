"""
routes/public.py - routes for normal visitors (NO login needed).

Visitors can only READ properties and SEND an enquiry.
They can never add, change or delete anything.

  GET  /api/properties        list properties (with optional filters)
  GET  /api/properties/<id>   one property with all its photos
  POST /api/enquiries         visitor sends name + email + message
"""
from flask import Blueprint, request, jsonify

import db
import mailer
from validators import is_valid_email, to_number

public_bp = Blueprint("public", __name__, url_prefix="/api")


@public_bp.get("/properties")
def list_properties():
    """
    Optional filters in the URL, e.g.
      /api/properties?type=plot&city=Kolkata&max_price=5000000&status=available
    """
    sql = """
        SELECT p.*,
               (SELECT image_url FROM property_images
                 WHERE property_id = p.id ORDER BY id LIMIT 1) AS cover_image
        FROM properties p
        WHERE 1 = 1
    """
    params = []

    # Each filter adds one condition only if the visitor chose it
    ptype = request.args.get("type")
    if ptype in ("plot", "house"):
        sql += " AND p.type = ?"
        params.append(ptype)

    status = request.args.get("status")
    if status in ("available", "sold"):
        sql += " AND p.status = ?"
        params.append(status)

    city = (request.args.get("city") or "").strip()
    if city:
        sql += " AND LOWER(p.city) LIKE ?"
        params.append(f"%{city.lower()}%")

    min_price = to_number(request.args.get("min_price"))
    if min_price is not None:
        sql += " AND p.price >= ?"
        params.append(min_price)

    max_price = to_number(request.args.get("max_price"))
    if max_price is not None:
        sql += " AND p.price <= ?"
        params.append(max_price)

    # Sorting: only allow known choices (never put user text straight into SQL)
    sort_options = {
        "newest": "p.id DESC",
        "price_low": "p.price ASC",
        "price_high": "p.price DESC",
    }
    order = sort_options.get(request.args.get("sort"), "p.id DESC")
    # Available properties first, then sold ones
    sql += f" ORDER BY (p.status = 'sold') ASC, {order}"

    return jsonify(db.query_all(sql, params))


@public_bp.get("/properties/<int:property_id>")
def get_property(property_id):
    """Return one property together with the list of its photo URLs."""
    prop = db.query_one("SELECT * FROM properties WHERE id = ?", (property_id,))
    if prop is None:
        return jsonify(error="Property not found"), 404

    images = db.query_all(
        "SELECT image_url FROM property_images WHERE property_id = ? ORDER BY id",
        (property_id,),
    )
    prop["images"] = [row["image_url"] for row in images]
    return jsonify(prop)


@public_bp.post("/enquiries")
def create_enquiry():
    """A visitor sends an enquiry. Only name, email and message are needed."""
    data = request.get_json(silent=True) or {}

    # Hidden "honeypot" field: real people never fill it, spam bots do.
    # We pretend it worked so the bot does not learn it was blocked.
    if data.get("website"):
        return jsonify(message="Thank you! We will contact you soon."), 201

    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip()
    message = (data.get("message") or "").strip()
    property_id = data.get("property_id")

    if not name:
        return jsonify(error="Please enter your name"), 400
    if not is_valid_email(email):
        return jsonify(error="Please enter a valid email"), 400
    if len(message) > 2000:
        return jsonify(error="Message is too long"), 400

    # If a property id was sent, make sure that property really exists
    if property_id is not None:
        if not db.query_one("SELECT id FROM properties WHERE id = ?", (property_id,)):
            return jsonify(error="Property not found"), 404

    db.execute(
        "INSERT INTO enquiries (property_id, name, email, message) VALUES (?, ?, ?, ?)",
        (property_id, name, email, message),
    )
    # Send email notification (best effort - never blocks the visitor)
    prop_title = None
    if property_id is not None:
        prop = db.query_one("SELECT title FROM properties WHERE id = ?", (property_id,))
        if prop:
            prop_title = prop["title"]
    mailer.send_enquiry_email(name, email, message, prop_title)
    return jsonify(message="Thank you! We will contact you soon."), 201
