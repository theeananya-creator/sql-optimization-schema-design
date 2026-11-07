-- Q1 (original): full table scan + SELECT *
SELECT * FROM orders_flat WHERE customer_email = :email;
