# Task 1: SQL

*This task involves your understanding of writing complex SQL queries. Follow the steps outlined below:*

1. **Setup up a local SQL database**

Create a local SQL database and set up the tables using the raw files provided in the link: https://drive.google.com/drive/folders/13Ra1PQuOT5Nv5HVb2ygrW2QAKBsqv6uY?usp=sharing

If you’re unfamiliar with creating a SQL database locally, take this opportunity to figure it out. A big part of working at Dcluttr is getting comfortable with solving challenges you haven’t faced before. Think of this as your warm-up exercise.

Here is a brief description of the data in each base table:

- **`all_blinkit_category_scraping_stream`:** This table contains raw public data of various SKUs listed on BlinkIt, segmented by dark store and date.
- **`blinkit_categories`:** This table provides a list of category IDs and subcategory IDs, along with their respective names. These will be used when creating the final derived table.
- **`blinkit_city_map`:** This table maps each dark store to its corresponding city. A city can have multiple dark stores.

Here is a detailed schema explaining each and every column in the input tables: https://docs.google.com/spreadsheets/d/1SVW-iLQIadZ2yQs28Y4Krua36EhLrDwDOxNYVz7T3Rg/edit?usp=sharing

---

1. **Task Objective**

Write an SQL query to create a new table named `blinkit_city_insights`. Ensure your query integrates data meaningfully from all three base tables, aligning with the provided schema.

Here is a detailed schema explaining each and every column in the derived table: https://docs.google.com/spreadsheets/d/1SVW-iLQIadZ2yQs28Y4Krua36EhLrDwDOxNYVz7T3Rg/edit?gid=0#gid=0

Final derived table `blinkit_city_insights` contains a column named `est_qty_sold` . There is no predefined formula for this column - you are expected to determine the logic as part of the task. Below is a high-level direction you can take (though you are free to explore alternate approaches if they make more sense):

- The `all_blinkit_category_scraping_stream` table includes an `inventory` column. To estimate quantity sold for a product at a dark store for a date, you need to track inventory movement over time.
- To calculate inventory movement, compare the inventory values between two nearest time slots for a given SKU at a given store.
    - Case 1: Inventory Decreases in the Next Time Slot - This indicates that sales have occurred. The difference in inventory can be considered the estimated quantity sold during that interval.
        - For example: Say for an SKU “Haldiram Namkeen” at a Store Id “152”:
            - Inventory on 6th Mar, 6 pm: 10
            - Inventory on 7th Mar, 12 am: 6
        - This implies **4 units** were likely sold between those two time slots.
    - Case 2: Inventory Increases in the Next Time Slot - This suggests a restock event. In such cases, you'll need to design an estimation logic for quantity sold. One approach could be to calculate the average quantity sold in the previous "X" time slots.
        - For example, let’s say for an SKU “Haldiram Namkeen” at a Store Id “152”:
            - Inventory on 6th Mar, 6 pm: 10
            - Inventory on 7th Mar, 12 am: 16
        - This indicates that new stock was added. Use historical sales data from previous time slots to estimate the likely sales during this interval.

Note:

For some `store_id`s in the **`all_blinkit_category_scraping_stream`** table, there may not be a corresponding city entry in the **`blinkit_city_map`** table. In such cases, exclude those stores from the analysis. Make sure to handle this appropriately in the SQL query.

1. **Deliverables**

Once your query is finalized:

1. Save the SQL query in a **.txt file**.
2. Execute the query and save the output in a **.csv file**.