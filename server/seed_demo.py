"""
seed_demo.py - seed the database with demo properties.

Safe to run multiple times: it only inserts properties that do not already
exist (matched by title), and sale records only for properties marked sold.

Usage:
    python seed_demo.py
"""
import app
import db


def seed():
    """Insert demo properties and sale records if they are not already present."""
    properties = [
        {
            "title": "Green Valley Plot - 1200 sq ft",
            "type": "plot",
            "price": 2500000,
            "area_sqft": 1200,
            "city": "Kolkata",
            "address": "Salt Lake Sector V, Kolkata",
            "bedrooms": None,
            "description": "Corner plot in a gated community with 40 ft road access.",
            "images": [
                "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=800",
            ],
            "status": "available",
        },
        {
            "title": "Lake View Plot - 1500 sq ft",
            "type": "plot",
            "price": 3200000,
            "area_sqft": 1500,
            "city": "Kolkata",
            "address": "EM Bypass, Kolkata",
            "bedrooms": None,
            "description": "Plot with lake view, close to schools and hospitals.",
            "images": [
                "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=800",
            ],
            "status": "available",
        },
        {
            "title": "Siliguri Hillside Plot - 2000 sq ft",
            "type": "plot",
            "price": 1800000,
            "area_sqft": 2000,
            "city": "Siliguri",
            "address": "Hill Cart Road, Siliguri",
            "bedrooms": None,
            "description": "Hillside plot with mountain views, perfect for a cottage.",
            "images": [
                "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=800",
            ],
            "status": "available",
        },
        {
            "title": "3BHK Family House - Kolkata",
            "type": "house",
            "price": 4500000,
            "area_sqft": 1500,
            "city": "Kolkata",
            "address": "Park Street, Kolkata",
            "bedrooms": 3,
            "description": "Spacious 3BHK house with modular kitchen and parking.",
            "images": [
                "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=800",
            ],
            "status": "available",
        },
        {
            "title": "2BHK Apartment - Salt Lake",
            "type": "house",
            "price": 3800000,
            "area_sqft": 1100,
            "city": "Kolkata",
            "address": "Salt Lake City, Kolkata",
            "bedrooms": 2,
            "description": "Modern 2BHK apartment in a secure complex with gym.",
            "images": [
                "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=800",
            ],
            "status": "available",
        },
        {
            "title": "4BHK Villa - Rajarhat",
            "type": "house",
            "price": 8500000,
            "area_sqft": 2800,
            "city": "Kolkata",
            "address": "Rajarhat New Town, Kolkata",
            "bedrooms": 4,
            "description": "Luxury 4BHK villa with private garden and pool.",
            "images": [
                "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=800",
            ],
            "status": "available",
        },
        {
            "title": "Sold Plot - New Town",
            "type": "plot",
            "price": 2800000,
            "area_sqft": 1600,
            "city": "Kolkata",
            "address": "New Town, Kolkata",
            "bedrooms": None,
            "description": "Plot in New Town - recently sold.",
            "images": [
                "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=800",
            ],
            "status": "sold",
            "buyer_name": "Rajesh Sharma",
            "buyer_email": "rajesh@example.com",
            "buyer_phone": "9876543210",
            "sale_price": 2750000,
        },
        {
            "title": "Sold House - Ballygunge",
            "type": "house",
            "price": 5200000,
            "area_sqft": 1800,
            "city": "Kolkata",
            "address": "Ballygunge, Kolkata",
            "bedrooms": 3,
            "description": "3BHK house in Ballygunge - recently sold.",
            "images": [
                "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=800",
            ],
            "status": "sold",
            "buyer_name": "Priya Patel",
            "buyer_email": "priya@example.com",
            "buyer_phone": "9123456789",
            "sale_price": 5000000,
        },
    ]

    for prop in properties:
        existing = db.query_one(
            "SELECT id FROM properties WHERE title = ?", (prop["title"],)
        )
        if existing:
            continue

        prop_id = db.execute(
            """INSERT INTO properties
               (title, type, price, area_sqft, city, address, bedrooms, description, status)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                prop["title"], prop["type"], prop["price"],
                prop["area_sqft"], prop["city"], prop["address"],
                prop["bedrooms"], prop["description"], prop["status"],
            ),
        )

        for img_url in prop.get("images", []):
            db.execute(
                "INSERT INTO property_images (property_id, image_url) VALUES (?, ?)",
                (prop_id, img_url),
            )

        if prop.get("status") == "sold":
            db.execute(
                """INSERT INTO sales
                   (property_id, buyer_name, buyer_email, buyer_phone, sale_price)
                   VALUES (?, ?, ?, ?, ?)""",
                (
                    prop_id,
                    prop["buyer_name"],
                    prop["buyer_email"],
                    prop["buyer_phone"],
                    prop["sale_price"],
                ),
            )

    print("Demo data seeded successfully.")


if __name__ == "__main__":
    with app.app.app_context():
        db.create_tables()
        seed()