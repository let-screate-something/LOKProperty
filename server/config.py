"""
config.py - all settings in one place.

Values can be overridden with environment variables, so the same code
works on your laptop and on the hosting service without editing files.
"""
import os

# Folder where this file lives (used to place the database file locally)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Secret used to sign admin login tokens.
# IMPORTANT: set a long random SECRET_KEY environment variable in production.
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me-before-going-online-0123456789")

# Database URL for PostgreSQL (Vercel / Neon / Supabase).
# On your laptop you can still use SQLite by setting DB_PATH instead.
DATABASE_URL = os.environ.get("DATABASE_URL", "")

# SQLite database file (fine for local use; see README for going online)
DB_PATH = os.environ.get("DB_PATH", os.path.join(BASE_DIR, "lok_property.db"))

# How long an admin stays logged in (hours)
TOKEN_HOURS = int(os.environ.get("TOKEN_HOURS", "8"))

# Which websites may call this API.
# "*" = any site (ok while developing). In production use your real
# addresses, for example: "https://lokproperty.com,https://admin.lokproperty.com"
CORS_ORIGINS = [o.strip() for o in os.environ.get("CORS_ORIGINS", "*").split(",")]
