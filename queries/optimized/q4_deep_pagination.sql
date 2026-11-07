-- Q4 (optimized): keyset (seek) pagination on index (order_date, order_id)
-- :last_date, :last_id = values from the last row of the previous page
SELECT order_id, order_date, status
FROM orders
WHERE (order_date, order_id) < (:last_date, :last_id)
ORDER BY order_date DESC, order_id DESC
LIMIT 20;
