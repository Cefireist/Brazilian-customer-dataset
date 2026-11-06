import pandas as pd
import duckdb as dd
import os

db_path = "DB/"

master_table_olist = dd.query("""
    SELECT 
        o.order_id,
        o.order_purchase_timestamp,
        c.customer_city,
        oi.freight_value,
        oi.Price AS item_price,
        pct.product_category_name_english AS product_category,
        pay.payment_type,
        r.review_score
    FROM orders AS o
    INNER JOIN customers AS c
        ON o.customer_id = c.customer_id
    INNER JOIN order_items AS oi
        ON o.order_id = oi.order_id
    INNER JOIN products AS p
        ON oi.product_id = p.product_id
    INNER JOIN product_category_name_translation AS pct
        ON p.product_category_name = pct.product_category_name
    INNER JOIN order_payments AS pay
        ON o.order_id = pay.order_id
    INNER JOIN order_reviews AS r
        ON o.order_id = r.order_id
    """).to_df()
master_table_olist.to_csv(os.path.join(db_path, "master_table_olist.csv"), index=False)