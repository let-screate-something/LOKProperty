-- schema.sql - database tables for LOK Property Solutions (SQLite)
-- Safe to run many times: tables are only created if missing.

-- Admin accounts (passwords are stored hashed, never as plain text)
CREATE TABLE IF NOT EXISTS admins (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL
);

-- Every plot or house we list
CREATE TABLE IF NOT EXISTS properties (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    title       TEXT NOT NULL,
    type        TEXT NOT NULL CHECK (type IN ('plot', 'house')),
    price       REAL NOT NULL,
    area_sqft   INTEGER,
    city        TEXT NOT NULL,
    address     TEXT,
    bedrooms    INTEGER,                      -- only used for houses
    description TEXT,
    status      TEXT NOT NULL DEFAULT 'available'
                CHECK (status IN ('available', 'sold')),
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Photo links (one row per photo, photos themselves are hosted elsewhere)
CREATE TABLE IF NOT EXISTS property_images (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    property_id INTEGER NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
    image_url   TEXT NOT NULL
);

-- Messages sent by visitors (name + email only, no accounts)
CREATE TABLE IF NOT EXISTS enquiries (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    property_id INTEGER REFERENCES properties(id) ON DELETE CASCADE,
    name        TEXT NOT NULL,
    email       TEXT NOT NULL,
    message     TEXT,
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Buy records: one row is created when the admin marks a property as sold
CREATE TABLE IF NOT EXISTS sales (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    property_id  INTEGER NOT NULL UNIQUE REFERENCES properties(id),
    buyer_name   TEXT NOT NULL,
    buyer_email  TEXT,
    buyer_phone  TEXT,
    sale_price   REAL,
    sold_on      TEXT NOT NULL DEFAULT (date('now'))
);

-- Indexes make filtering faster as the data grows
CREATE INDEX IF NOT EXISTS idx_properties_status ON properties(status);
CREATE INDEX IF NOT EXISTS idx_properties_type   ON properties(type);
CREATE INDEX IF NOT EXISTS idx_images_property   ON property_images(property_id);
CREATE INDEX IF NOT EXISTS idx_enquiries_created ON enquiries(created_at);
