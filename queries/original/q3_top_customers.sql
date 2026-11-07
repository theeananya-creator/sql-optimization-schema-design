-- Q3 (original): groups 300k lines by a wide text key, two temp B-trees
SELECT customer_email, SUM(unit_price * quantity) AS s
FROM orders_flat
GROUP BY customer_email
ORDER BY s DESC
LIMIT 10;
