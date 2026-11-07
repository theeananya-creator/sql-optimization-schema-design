-- Revised schema (3NF). SQLite syntax; use DATE / DECIMAL(12,2) in PostgreSQL/MySQL.
PRAGMA foreign_keys = ON;

CREATE TABLE categories (
  category_id INTEGER PRIMARY KEY,
  name        TEXT NOT NULL UNIQUE
);

CREATE TABLE customers (
  customer_id INTEGER PRIMARY KEY,
  full_name   TEXT NOT NULL,
  email       TEXT NOT NULL,
  phone       TEXT,
  city        TEXT
);

CREATE TABLE products (
  product_id  INTEGER PRIMARY KEY,
  name        TEXT NOT NULL,
  category_id INTEGER NOT NULL REFERENCES categories(category_id),
  unit_price  REAL NOT NULL
);

CREATE TABLE orders (
  order_id       INTEGER PRIMARY KEY,
  customer_id    INTEGER NOT NULL REFERENCES customers(customer_id),
  order_date     TEXT NOT NULL,            -- ISO-8601 'YYYY-MM-DD'
  status         TEXT NOT NULL,
  payment_method TEXT,
  total_amount   REAL NOT NULL DEFAULT 0   -- deliberate denormalization (summary)
);

CREATE TABLE order_items (
  order_item_id INTEGER PRIMARY KEY,
  order_id      INTEGER NOT NULL REFERENCES orders(order_id),
  product_id    INTEGER NOT NULL REFERENCES products(product_id),
  quantity      INTEGER NOT NULL,
  unit_price    REAL NOT NULL              -- price snapshot at time of sale
);
