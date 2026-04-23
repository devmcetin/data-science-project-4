import psycopg2

## Bu değeri localinde çalışırken kendi passwordün yap. Ama kodu pushlarken 'postgres' olarak bırak.
password = 'postgres'

def connect_db():
    return psycopg2.connect(
        host="localhost",
        port=5432,
        database="postgres",
        user="postgres",
        password=password
    )

def create_view_completed_orders():
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
            CREATE OR REPLACE VIEW completed_orders AS(
                SELECT * FROM orders WHERE status = 'completed'
            );
            """)
            conn.commit()

def create_view_electronics_products():
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
            CREATE OR REPLACE VIEW electronic_products AS(
                SELECT * FROM products WHERE category = 'Electronics'
            );
            """)
            conn.commit()

def total_spending_per_customer():
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
            WITH spending AS (
                SELECT o.customer_id, SUM(o.quantity * p.price) AS total_spending
                FROM orders o
                INNER JOIN products p ON o.product_id = p.product_id
                GROUP BY o.customer_id
            )
            SELECT c.full_name, s.total_spending
            FROM spending s
            INNER JOIN customers c ON s.customer_id = c.customer_id
            ORDER BY s.total_spending DESC;
            """)
            return cur.fetchall()

def order_details_with_total():
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
            WITH product_details AS(
                SELECT *
                FROM orders o
                JOIN products p
                ON o.product_id = p.product_id
            )
                
            SELECT p.order_id, c.full_name, p.product_name, p.quantity * p.price AS total_price
            FROM product_details p
            JOIN customers c
            ON p.customer_id = c.customer_id;
            """)
            return cur.fetchall()

def get_customer_who_bought_most_expensive_product():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
    SELECT full_name
    FROM customers
    WHERE customer_id = (
        SELECT o.customer_id
        FROM orders o
        JOIN products p
        ON o.product_id = p.product_id
        ORDER BY price DESC
        LIMIT 1
    );
    """)
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result

# 2. Sipariş durumlarına göre açıklama
def get_order_status_descriptions():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
    SELECT order_id, status,
        CASE
            WHEN status = 'completed' THEN 'Tamamlandı'
            WHEN status = 'cancelled' THEN 'İptal Edildi'
            ELSE 'Diğer'
        END AS status_description
    FROM orders;
    """)
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result

# 3. Ortalama fiyatın üstündeki ürünler
def get_products_above_average_price():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
    SELECT product_name, price
    FROM products
    WHERE price > (
        SELECT AVG(price)
        FROM products
    );
    """)
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result

# 4. Müşteri kategorileri
def get_customer_categories():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
    WITH order_counts AS(
        SELECT c.customer_id, COUNT(*) AS order_count
        FROM customers c
        JOIN orders o
        ON c.customer_id = o.customer_id
        GROUP BY c.customer_id
    )

    SELECT c.full_name,
        CASE
            WHEN o.order_count > 5 THEN 'Sadık Müşteri'
            WHEN o.order_count > 2 THEN 'Orta Seviye'
            ELSE 'Yeni Müşteri'
        END AS customer_category
    FROM customers c
    JOIN order_counts o
    ON c.customer_id = o.customer_id;
    """)
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result

# 5. Son 30 gün içinde sipariş veren müşteriler
def get_recent_customers():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
    SELECT DISTINCT c.full_name
    FROM customers c
    INNER JOIN orders o ON c.customer_id = o.customer_id
    WHERE o.order_date >= CURRENT_DATE - INTERVAL '30 days';
    """)
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result

# 6. En çok sipariş verilen ürün
def get_most_ordered_product():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
    WITH most_ordered AS(
        SELECT p.product_id, SUM(o.quantity) order_count
        FROM products p
        JOIN orders o
        ON p.product_id = o.order_id
        GROUP BY p.product_id
        ORDER BY order_count DESC
        LIMIT 1
    )

    SELECT p.product_name, mo.order_count
    FROM products p
    JOIN most_ordered mo
    ON p.product_id = mo.product_id;
    """)
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result

# 7. Ürün fiyatlarına göre etiketleme
def get_product_price_categories():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
    SELECT product_name, price,
        CASE
            WHEN price > 1000 THEN 'Pahalı'
            WHEN price > 500 THEN 'Orta'
            ELSE 'Ucuz'
        END AS product_category
    FROM products;
    """)
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result