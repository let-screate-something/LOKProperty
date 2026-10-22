"""
validators.py - small checks for data sent by the websites.

Never trust data coming from a browser, so every route cleans and checks
its input here before saving it.
"""
import re

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def is_valid_email(email):
    return bool(email) and bool(EMAIL_PATTERN.match(email))


def to_number(value):
    """Turn a value into a float, or return None if it is not a number."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def to_int(value):
    """Turn a value into an int, or return None (empty values give None)."""
    if value in (None, ""):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def clean_property(data):
    """
    Check the fields of a property sent by the admin site.
    Returns (clean_data, error_message). If error_message is not None, reject the request.
    """
    title = (data.get("title") or "").strip()
    city = (data.get("city") or "").strip()
    ptype = data.get("type")
    price = to_number(data.get("price"))

    if not title:
        return None, "Title is required"
    if ptype not in ("plot", "house"):
        return None, "Type must be 'plot' or 'house'"
    if price is None or price <= 0:
        return None, "Price must be a positive number"
    if not city:
        return None, "City is required"

    clean = {
        "title": title,
        "type": ptype,
        "price": price,
        "area_sqft": to_int(data.get("area_sqft")),
        "city": city,
        "address": (data.get("address") or "").strip(),
        # bedrooms only make sense for houses
        "bedrooms": to_int(data.get("bedrooms")) if ptype == "house" else None,
        "description": (data.get("description") or "").strip(),
    }
    # Photo links: a list of URLs (empty lines are ignored)
    images = data.get("images") or []
    clean["images"] = [u.strip() for u in images if isinstance(u, str) and u.strip()]
    return clean, None
