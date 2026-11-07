CREATE UNIQUE INDEX ux_customers_email ON customers(email);
CREATE INDEX ix_orders_customer ON orders(customer_id, total_amount);
CREATE INDEX ix_orders_date     ON orders(order_date, order_id);
CREATE INDEX ix_orders_date_amt ON orders(order_date, total_amount);
CREATE INDEX ix_items_order     ON order_items(order_id);
CREATE INDEX ix_items_product   ON order_items(product_id);
ANALYZE;
