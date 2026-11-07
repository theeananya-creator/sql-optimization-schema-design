-- Q4 (original): OFFSET sorts everything, then discards 50,000 rows
SELECT *
FROM orders_flat
ORDER BY order_date DESC, row_id DESC
LIMIT 20 OFFSET 50000;
