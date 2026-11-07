-- Q2 (optimized): half-open range + covering index (order_date, total_amount)
SELECT COUNT(*), SUM(total_amount)
FROM orders
WHERE order_date >= '2024-01-01'
  AND order_date <  '2025-01-01';
