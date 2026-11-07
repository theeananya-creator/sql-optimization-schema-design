-- Q1 (optimized): unique index on email + indexed FK join, only needed columns
SELECT o.order_id, o.order_date, o.status, o.total_amount
FROM customers c
JOIN orders o ON o.customer_id = c.customer_id
WHERE c.email = :email;
