-- Legacy design: one wide, denormalized table, no secondary indexes.
-- (scripts/benchmark.py generates this table from the normalized data,
--  so both designs hold identical information.)
CREATE TABLE orders_flat (
  row_id          INTEGER PRIMARY KEY,
  order_id        INTEGER,
  order_date      TEXT,
  customer_name   TEXT,
  customer_email  TEXT,
  customer_phone  TEXT,
  customer_city   TEXT,
  product_name    TEXT,
  category_name   TEXT,
  unit_price      REAL,
  quantity        INTEGER,
  order_status    TEXT,
  payment_method  TEXT
);
