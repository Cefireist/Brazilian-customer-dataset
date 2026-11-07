import pandas as pd
import duckdb as dd
import os

db_path = "DB/"
customers = pd.read_csv(os.path.join(db_path,"olist_customers_dataset.csv"))
geolocations = pd.read_csv(os.path.join(db_path,"olist_geolocation_dataset.csv"))
order_items = pd.read_csv(os.path.join(db_path,"olist_order_items_dataset.csv"))
order_payments = pd.read_csv(os.path.join(db_path,"olist_order_payments_dataset.csv"))
order_reviews = pd.read_csv(os.path.join(db_path,"olist_order_reviews_dataset.csv"))
orders = pd.read_csv(os.path.join(db_path,"olist_orders_dataset.csv"))
products = pd.read_csv(os.path.join(db_path,"olist_products_dataset.csv"))
sellers = pd.read_csv(os.path.join(db_path,"olist_sellers_dataset.csv"))
product_category_name_translation = pd.read_csv(os.path.join(db_path,"product_category_name_translation.csv"))



master_table_olist = dd.query("""
    -- grouping payments and reviews by order_id to get aggregated values
    WITH grouped_payments AS (
        SELECT 
            order_id,
            SUM(payment_value) AS total_payment_value,
            COUNT(payment_type) AS total_payment_types,
        FROM order_payments
        GROUP BY order_id
    ),
    -- grouping reviews by order_id to get average review score
    grouped_reviews AS (
        SELECT 
            order_id,
            AVG(review_score) AS avg_review_score
        FROM order_reviews
        GROUP BY order_id
    )
    -- selecting the required columns from the orders, customers, order_items, products, and the grouped payments and reviews
    SELECT 
        o.order_id,
        o.order_status,
        o.order_purchase_timestamp,
        c.customer_city,
        c.customer_state,
        oi.order_item_id,
        oi.price AS item_price,
        oi.freight_value,
        COALESCE(pct.product_category_name_english, 'other') AS product_category,
        p.payment_type,
        r.avg_review_score AS review_score
    FROM orders AS o
    INNER JOIN customers AS c 
        ON o.customer_id = c.customer_id
    INNER JOIN order_items AS oi 
        ON o.order_id = oi.order_id
    LEFT JOIN products AS prod 
        ON oi.product_id = prod.product_id
    LEFT JOIN product_category_name_translation AS pct 
        ON prod.product_category_name = pct.product_category_name
    LEFT JOIN order_payments AS p 
        ON o.order_id = p.order_id
    LEFT JOIN grouped_reviews AS r 
        ON o.order_id = r.order_id
    WHERE o.order_status = 'delivered'
""").to_df()

master_table_olist.to_csv(os.path.join(db_path, "master_table_olist.csv"), index=False)