-- Q2 (original): function on the column makes the predicate non-sargable
SELECT COUNT(*), SUM(unit_price * quantity)
FROM orders_flat
WHERE strftime('%Y', order_date) = '2024';
