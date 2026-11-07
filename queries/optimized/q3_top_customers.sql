-- Q3 (optimized): integer key + stored order totals + covering index
SELECT customer_id, SUM(total_amount) AS s
FROM orders
GROUP BY customer_id
ORDER BY s DESC
LIMIT 10;
