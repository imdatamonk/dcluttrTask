CREATE DATABASE IF NOT EXISTS dcluttrtest;
USE dcluttrtest;
CREATE TABLE IF NOT EXISTS all_blinkit_category_scraping_stream (
    created_at DATETIME,
    l1_category_id BIGINT,
    l2_category_id BIGINT,
    store_id BIGINT,
    sku_id BIGINT,
    sku_name TEXT,
    selling_price DECIMAL(10,2),
    mrp DECIMAL(10,2),
    inventory INT,
    image_url TEXT,
    brand_id BIGINT,
    brand TEXT,
    unit VARCHAR(100),
    PRIMARY KEY (created_at, sku_id, store_id)
);
CREATE TABLE IF NOT EXISTS blinkit_categories (
    l1_category VARCHAR(255),
    l1_category_id BIGINT,
    l2_category VARCHAR(255),
    l2_category_id BIGINT PRIMARY KEY
);
CREATE TABLE IF NOT EXISTS blinkit_city_map (
    store_id BIGINT PRIMARY KEY,
    city_name VARCHAR(255)
);
Show tables;
SET GLOBAL local_infile = 1;
LOAD DATA LOCAL INFILE '../data//all_blinkit_category_scraping_stream.csv'
INTO TABLE dcluttrtest.all_blinkit_category_scraping_stream
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES;
LOAD DATA LOCAL INFILE '../data/blinkit_categories.csv'
INTO TABLE dcluttrtest.blinkit_categories
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES;
LOAD DATA LOCAL INFILE '../data//blinkit_city_map.csvv'
INTO TABLE dcluttrtest.blinkit_city_map
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES;
# describe all_blinkit_category_scraping_stream;
# describe blinkit_categories;
# describe blinkit_city_map;
CREATE TABLE IF NOT EXISTS blinkit_city_insights (
    date DATETIME,
    brand_id INT,
    brand VARCHAR(255),
    image_url TEXT,
    city_name VARCHAR(255),
    sku_id BIGINT,
    sku_name VARCHAR(255),
    category_id INT,
    category_name VARCHAR(255),
    sub_category_id INT,
    sub_category_name VARCHAR(255),
    est_qty_sold INT,
    est_sales_sp DECIMAL(15, 2),
    est_sales_mrp DECIMAL(15, 2),
    listed_ds_count INT,
    ds_count INT,
    wt_osa DECIMAL(6, 4),
    wt_osa_ls DECIMAL(6, 4),
    mrp DECIMAL(10, 2),
    sp DECIMAL(10, 2),
    discount DECIMAL(6, 4),
    PRIMARY KEY (date, sku_id, city_name)
);
CREATE TEMPORARY TABLE dcluttrtest.sku_inventory_diff AS
WITH inventory_with_next AS (
    SELECT
        created_at,
        sku_id,
        store_id,
        inventory,
        LEAD(inventory) OVER (PARTITION BY sku_id, store_id ORDER BY created_at) AS next_inventory
    FROM dcluttrtest.all_blinkit_category_scraping_stream
)

SELECT
    created_at AS date,
    sku_id,
    store_id,
    CASE
        WHEN next_inventory IS NOT NULL AND next_inventory < inventory THEN (inventory - next_inventory)
        ELSE 0
    END AS est_qty_sold
FROM inventory_with_next;

INSERT IGNORE INTO blinkit_city_insights (
    date, brand_id, brand, image_url, city_name, sku_id, sku_name,
    category_id, category_name, sub_category_id, sub_category_name,
    est_qty_sold, est_sales_sp, est_sales_mrp, listed_ds_count, ds_count,
    wt_osa, wt_osa_ls, mrp, sp, discount
)
WITH store_count AS (
    SELECT COUNT(DISTINCT store_id) AS total_stores
    FROM all_blinkit_category_scraping_stream
),
price_mode AS (
    SELECT sku_id,
           FIRST_VALUE(mrp) OVER (PARTITION BY sku_id ORDER BY COUNT(*) DESC ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS mrp,
           FIRST_VALUE(selling_price) OVER (PARTITION BY sku_id ORDER BY COUNT(*) DESC ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS sp
    FROM all_blinkit_category_scraping_stream
    GROUP BY sku_id, mrp, selling_price
),
main AS (
    SELECT
        s.created_at AS date,
        s.brand_id,
        s.brand,
        s.image_url,
        cm.city_name,
        s.sku_id,
        s.sku_name,
        bc.l1_category_id AS category_id,
        bc.l1_category AS category_name,
        bc.l2_category_id AS sub_category_id,
        bc.l2_category AS sub_category_name,
        SUM(d.est_qty_sold) AS est_qty_sold,
        SUM(d.est_qty_sold * s.selling_price) AS est_sales_sp,
        SUM(d.est_qty_sold * s.mrp) AS est_sales_mrp,
        COUNT(DISTINCT CASE WHEN s.inventory IS NOT NULL THEN s.store_id END) AS listed_ds_count,
        SUM(CASE WHEN s.inventory > 0 THEN 1 ELSE 0 END) AS in_stock_count,
        COUNT(DISTINCT s.store_id) AS all_listed_stores
    FROM all_blinkit_category_scraping_stream s
    JOIN blinkit_categories bc ON s.l2_category_id = bc.l2_category_id
    JOIN blinkit_city_map cm ON s.store_id = cm.store_id
    LEFT JOIN sku_inventory_diff d ON s.sku_id = d.sku_id AND s.store_id = d.store_id AND s.created_at = d.date
    GROUP BY s.created_at,
        s.brand_id,
        s.brand,
        s.image_url,
        cm.city_name,
        s.sku_id,
        s.sku_name,
        bc.l1_category_id,
        bc.l1_category,
        bc.l2_category_id,
        bc.l2_category
)
SELECT
    m.date,
    m.brand_id,
    m.brand,
    m.image_url,
    m.city_name,
    m.sku_id,
    m.sku_name,
    m.category_id,
    m.category_name,
    m.sub_category_id,
    m.sub_category_name,
    m.est_qty_sold,
    m.est_sales_sp,
    m.est_sales_mrp,
    m.listed_ds_count,
    sc.total_stores AS ds_count,
    ROUND(m.in_stock_count / sc.total_stores, 4) AS wt_osa,
    ROUND(m.in_stock_count / NULLIF(m.all_listed_stores, 0), 4) AS wt_osa_ls,
    pm.mrp,
    pm.sp,
    ROUND((pm.mrp - pm.sp) / NULLIF(pm.mrp, 0), 4) AS discount
FROM main m
JOIN store_count sc ON 1=1
LEFT JOIN price_mode pm ON m.sku_id = pm.sku_id;
#SHOW VARIABLES LIKE 'secure_file_priv';
SELECT *
FROM blinkit_city_insights
# INTO OUTFILE '../data/blinkit_city_insights.csv' --locn to save
# FIELDS TERMINATED BY ','
# ENCLOSED BY '"'
# LINES TERMINATED BY '\n';