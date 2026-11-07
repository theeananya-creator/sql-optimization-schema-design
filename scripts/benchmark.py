import sqlite3, random, time, json, os
random.seed(42)
if os.path.exists('data/shop.db'): os.remove('data/shop.db')
db = sqlite3.connect('data/shop.db')
c = db.cursor()
N_CUST, N_PROD, N_ORD = 20000, 500, 100000
cities = ['Nagpur','Pune','Mumbai','Delhi','Bengaluru','Chennai','Hyderabad','Kolkata','Jaipur','Indore']
cats = ['Electronics','Books','Clothing','Home','Toys','Sports','Beauty','Grocery','Garden','Office']
statuses = ['PLACED','SHIPPED','DELIVERED','CANCELLED']
pay = ['UPI','CARD','COD','NETBANKING']

c.executescript("""
CREATE TABLE categories(category_id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE);
CREATE TABLE customers(customer_id INTEGER PRIMARY KEY, full_name TEXT NOT NULL, email TEXT NOT NULL, phone TEXT, city TEXT);
CREATE TABLE products(product_id INTEGER PRIMARY KEY, name TEXT NOT NULL, category_id INTEGER NOT NULL REFERENCES categories, unit_price REAL NOT NULL);
CREATE TABLE orders(order_id INTEGER PRIMARY KEY, customer_id INTEGER NOT NULL REFERENCES customers, order_date TEXT NOT NULL, status TEXT NOT NULL, payment_method TEXT, total_amount REAL NOT NULL DEFAULT 0);
CREATE TABLE order_items(order_item_id INTEGER PRIMARY KEY, order_id INTEGER NOT NULL REFERENCES orders, product_id INTEGER NOT NULL REFERENCES products, quantity INTEGER NOT NULL, unit_price REAL NOT NULL);
""")
c.executemany("INSERT INTO categories VALUES(?,?)", list(enumerate(cats,1)))
c.executemany("INSERT INTO customers VALUES(?,?,?,?,?)",
  [(i, f'Customer {i}', f'user{i}@example.com', f'9{random.randint(100000000,999999999)}', random.choice(cities)) for i in range(1,N_CUST+1)])
c.executemany("INSERT INTO products VALUES(?,?,?,?)",
  [(i, f'Product {i}', random.randint(1,10), round(random.uniform(50,5000),2)) for i in range(1,N_PROD+1)])
prices = dict(c.execute("select product_id, unit_price from products").fetchall())
orders=[]; items=[]; iid=1
from datetime import date, timedelta
start=date(2022,1,1)
for o in range(1,N_ORD+1):
    cust=random.randint(1,N_CUST)
    d=(start+timedelta(days=random.randint(0,1460))).isoformat()
    tot=0
    for _ in range(random.choice([1,2,3,4,5])):
        p=random.randint(1,N_PROD); q=random.randint(1,4)
        items.append((iid,o,p,q,prices[p])); tot+=q*prices[p]; iid+=1
    orders.append((o,cust,d,random.choice(statuses),random.choice(pay),round(tot,2)))
c.executemany("INSERT INTO orders VALUES(?,?,?,?,?,?)", orders)
c.executemany("INSERT INTO order_items VALUES(?,?,?,?,?)", items)
# flat legacy table, built from same data
c.execute("""CREATE TABLE orders_flat AS
SELECT oi.order_item_id AS row_id, o.order_id, o.order_date, cu.full_name AS customer_name, cu.email AS customer_email,
 cu.phone AS customer_phone, cu.city AS customer_city, p.name AS product_name, ca.name AS category_name,
 oi.unit_price, oi.quantity, o.status AS order_status, o.payment_method
FROM order_items oi JOIN orders o USING(order_id) JOIN customers cu USING(customer_id)
JOIN products p USING(product_id) JOIN categories ca USING(category_id)""")
db.commit()
n_flat = c.execute("select count(*) from orders_flat").fetchone()[0]
print("flat rows", n_flat, "items", len(items))

# indexes for optimized schema only
c.executescript("""
CREATE UNIQUE INDEX ux_customers_email ON customers(email);
CREATE INDEX ix_orders_customer ON orders(customer_id, total_amount);
CREATE INDEX ix_orders_date ON orders(order_date, order_id);
CREATE INDEX ix_orders_date_amt ON orders(order_date, total_amount);
CREATE INDEX ix_items_order ON order_items(order_id);
CREATE INDEX ix_items_product ON order_items(product_id);
""")
db.commit(); db.execute("ANALYZE"); db.commit()

email='user12345@example.com'
Q = [
 ("Q1 Look up one customer's orders",
  "SELECT * FROM orders_flat WHERE customer_email = ?",
  "SELECT o.order_id, o.order_date, o.status, o.total_amount FROM customers c JOIN orders o ON o.customer_id = c.customer_id WHERE c.email = ?",
  (email,)),
 ("Q2 Revenue for calendar year 2024",
  "SELECT COUNT(*), SUM(unit_price*quantity) FROM orders_flat WHERE strftime('%Y', order_date) = '2024'",
  "SELECT COUNT(*), SUM(total_amount) FROM orders WHERE order_date >= '2024-01-01' AND order_date < '2025-01-01'",
  ()),
 ("Q3 Top 10 customers by spend",
  "SELECT customer_email, SUM(unit_price*quantity) s FROM orders_flat GROUP BY customer_email ORDER BY s DESC LIMIT 10",
  "SELECT customer_id, SUM(total_amount) s FROM orders GROUP BY customer_id ORDER BY s DESC LIMIT 10",
  ()),
 ("Q4 Deep pagination (page 2,500)",
  "SELECT * FROM orders_flat ORDER BY order_date DESC, row_id DESC LIMIT 20 OFFSET 50000",
  "SELECT order_id, order_date, status FROM orders WHERE (order_date, order_id) < (?, ?) ORDER BY order_date DESC, order_id DESC LIMIT 20",
  None),
]
# keyset anchor = what row 100000 would be in orders
anchor = c.execute("SELECT order_date, order_id FROM orders ORDER BY order_date DESC, order_id DESC LIMIT 1 OFFSET 49999").fetchone()
res=[]
def timeit(sql, params, reps=7):
    ts=[]
    for _ in range(reps):
        t=time.perf_counter(); rows=c.execute(sql, params).fetchall(); ts.append((time.perf_counter()-t)*1000)
    return sorted(ts)[len(ts)//2], len(rows)
def plan(sql, params):
    return [r[3] for r in c.execute("EXPLAIN QUERY PLAN "+sql, params).fetchall()]
for name, bad, good, params in Q:
    pb = params if params is not None else ()
    pg = params if params is not None else anchor
    tb, nb = timeit(bad, pb); tg, ng = timeit(good, pg)
    res.append(dict(name=name, bad=bad, good=good, t_bad=round(tb,2), t_good=round(tg,3), rows_bad=nb, rows_good=ng,
                    plan_bad=plan(bad,pb), plan_good=plan(good,pg)))
    print(name, round(tb,2), round(tg,3), nb, ng)
    print("  BAD ", res[-1]['plan_bad']); print("  GOOD", res[-1]['plan_good'])
# bonus: Q1 on flat with its own index to show index-only effect
c.execute("CREATE INDEX tmp_flat_email ON orders_flat(customer_email)")
tb2,_ = timeit("SELECT * FROM orders_flat WHERE customer_email = ?", (email,))
print("Q1 flat + index", tb2)
c.execute("DROP INDEX tmp_flat_email")
# storage
sz_flat = c.execute("select sum(pgsize) from dbstat where name='orders_flat'").fetchone()[0]
sz_norm = c.execute("select sum(pgsize) from dbstat where name in ('orders','order_items','customers','products','categories')").fetchone()[0]
print("sizes MB", sz_flat/1e6, sz_norm/1e6)
json.dump(dict(queries=res, flat_rows=n_flat, n_cust=N_CUST, n_orders=N_ORD, q1_flat_index=round(tb2,3),
               size_flat_mb=round(sz_flat/1e6,1), size_norm_mb=round(sz_norm/1e6,1)), open('results/results.json','w'), indent=1)
