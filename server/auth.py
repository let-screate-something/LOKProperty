"""
auth.py - admin login helpers.

Flow:
  1. Admin sends username + password to POST /api/admin/login
  2. If correct, the server returns a signed token (JWT)
  3. The admin site sends that token with every admin request in the header:
         Authorization: Bearer <token>
  4. `admin_required` checks the token before an admin route runs.
"""
import datetime
from functools import wraps

import jwt
from flask import request, jsonify

import config


def create_token(admin_id, username):
    """Make a signed token that expires after config.TOKEN_HOURS."""
    payload = {
        "admin_id": admin_id,
        "username": username,
        "exp": datetime.datetime.now(datetime.timezone.utc)
        + datetime.timedelta(hours=config.TOKEN_HOURS),
    }
    return jwt.encode(payload, config.SECRET_KEY, algorithm="HS256")


def admin_required(route_function):
    """Decorator: put it above an admin route to block people who are not logged in."""

    @wraps(route_function)
    def wrapper(*args, **kwargs):
        header = request.headers.get("Authorization", "")
        if not header.startswith("Bearer "):
            return jsonify(error="Login required"), 401
        token = header[len("Bearer "):]
        try:
            jwt.decode(token, config.SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify(error="Session expired, please log in again"), 401
        except jwt.InvalidTokenError:
            return jsonify(error="Invalid token"), 401
        return route_function(*args, **kwargs)

    return wrapper
