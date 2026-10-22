-- schema_postgres.sql - PostgreSQL version for Vercel + Neon/Supabase
-- Run this SQL in your Neon or Supabase SQL editor before deploying.

CREATE TABLE IF NOT EXISTS admins (
    id            SERIAL PRIMARY KEY,
    username      TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS properties (
    id          SERIAL PRIMARY KEY,
    title       TEXT NOT NULL,
    type        TEXT NOT NULL CHECK (type IN ('plot', 'house')),
    price       REAL NOT NULL,
    area_sqft   INTEGER,
    city        TEXT NOT NULL,
    address     TEXT,
    bedrooms    INTEGER,
    description TEXT,
    status      TEXT NOT NULL DEFAULT 'available' CHECK (status IN ('available', 'sold')),
    created_at  TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS property_images (
    id          SERIAL PRIMARY KEY,
    property_id INTEGER NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
    image_url   TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS enquiries (
    id          SERIAL PRIMARY KEY,
    property_id INTEGER REFERENCES properties(id) ON DELETE CASCADE,
    name        TEXT NOT NULL,
    email       TEXT NOT NULL,
    message     TEXT,
    created_at  TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS sales (
    id           SERIAL PRIMARY KEY,
    property_id  INTEGER NOT NULL UNIQUE REFERENCES properties(id),
    buyer_name   TEXT NOT NULL,
    buyer_email  TEXT,
    buyer_phone  TEXT,
    sale_price   REAL,
    sold_on      DATE NOT NULL DEFAULT CURRENT_DATE
);

CREATE INDEX IF NOT EXISTS idx_properties_status ON properties(status);
CREATE INDEX IF NOT EXISTS idx_properties_type   ON properties(type);
CREATE INDEX IF NOT EXISTS idx_images_property   ON property_images(property_id);
CREATE INDEX IF NOT EXISTS idx_enquiries_created ON enquiries(created_at);