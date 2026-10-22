"""
db.py - connects to the database and gives small helper functions.

Works with both SQLite (local development) and PostgreSQL (Vercel / Neon / Supabase).
Every request gets its own connection (stored in Flask's `g`),
and it is closed automatically when the request ends.
"""
import os
from flask import g

import config


def _convert_placeholders(sql, is_postgres):
    """Convert ? placeholders to %s for PostgreSQL/psycopg2."""
    if is_postgres:
        return sql.replace("?", "%s")
    return sql


def get_db():
    """Return the connection for the current request (create it if needed).

    Uses PostgreSQL (DATABASE_URL) when available, otherwise falls back to SQLite (DB_PATH).
    """
    if "db" not in g:
        database_url = os.environ.get("DATABASE_URL") or config.DATABASE_URL
        if database_url:
            # PostgreSQL via psycopg2
            import psycopg2
            from psycopg2.extras import RealDictCursor
            g.db = psycopg2.connect(database_url, cursor_factory=RealDictCursor)
            g.db_is_postgres = True
        else:
            # SQLite fallback (local development only)
            import sqlite3
            g.db = sqlite3.connect(config.DB_PATH)
            g.db.row_factory = sqlite3.Row            # rows behave like dictionaries
            g.db.execute("PRAGMA foreign_keys = ON")  # enforce links between tables
            g.db_is_postgres = False
    return g.db


def close_db(error=None):
    """Close the connection at the end of the request."""
    db = g.pop("db", None)
    if db is not None:
        db.close()
    g.pop("db_is_postgres", None)


def _is_postgres(db):
    return getattr(db, "db_is_postgres", False)


def query_all(sql, params=()):
    """Run a SELECT and return a list of dictionaries."""
    db = get_db()
    postgres = _is_postgres(db)
    sql = _convert_placeholders(sql, postgres)
    if postgres:
        with db.cursor() as cur:
            cur.execute(sql, params)
            return [dict(row) for row in cur.fetchall()]
    else:
        import sqlite3
        rows = db.execute(sql, params).fetchall()
        return [dict(row) for row in rows]


def query_one(sql, params=()):
    """Run a SELECT and return one dictionary (or None if nothing found)."""
    db = get_db()
    postgres = _is_postgres(db)
    sql = _convert_placeholders(sql, postgres)
    if postgres:
        with db.cursor() as cur:
            cur.execute(sql, params)
            row = cur.fetchone()
            return dict(row) if row else None
    else:
        import sqlite3
        row = db.execute(sql, params).fetchone()
        return dict(row) if row else None


def execute(sql, params=()):
    """Run an INSERT / UPDATE / DELETE, save it, and return the new row id.

    For INSERT statements on PostgreSQL, append RETURNING id so we get the new id back.
    """
    db = get_db()
    postgres = _is_postgres(db)
    sql = _convert_placeholders(sql, postgres)

    if postgres:
        with db.cursor() as cur:
            # For INSERTs, add RETURNING id to get the new primary key
            stripped = sql.lstrip().upper()
            if stripped.startswith("INSERT") and "RETURNING" not in stripped:
                sql = sql.rstrip().rstrip(";") + " RETURNING id"
            cur.execute(sql, params)
            db.commit()
            try:
                row = cur.fetchone()
                if row:
                    return row[0]
                return cur.rowcount if cur.rowcount > 0 else None
            except (TypeError, ValueError):
                return None
    else:
        import sqlite3
        cursor = db.execute(sql, params)
        db.commit()
        return cursor.lastrowid


def create_tables():
    """Create all tables. On PostgreSQL this is a no-op - run schema_postgres.sql manually."""
    pass


def init_app(app):
    """Hook the database into the Flask app."""
    app.teardown_appcontext(close_db)
