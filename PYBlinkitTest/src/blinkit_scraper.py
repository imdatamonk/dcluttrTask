import pandas as pd
import requests
import os
from datetime import datetime

category_df = pd.read_csv('../Data/blinkit_categories.csv')
location_df = pd.read_csv('../Data/blinkit_locations.csv')

all_products = []

for _, loc in location_df.iterrows():
    lat, lng = loc['latitude'], loc['longitude']
    for _, row in category_df.iterrows():
        l1 = row['l1_category']
        l2 = row['l2_category']
        cat_id_1 = row['l1_category_id']
        cat_id_2 = row['l2_category_id']

        url = f"https://blinkit.com/v1/layout/listing_widgets?l0_cat={cat_id_1}&l2_cat={cat_id_2}?lat={lat}&lng={lng}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                products = data.get("data", {}).get("products", [])

                for p in products:
                    all_products.append({
                        "timestamp": datetime.now().isoformat(),
                        "l1_category": l1,
                        "l2_category": l2,
                        "product_name": p.get("display_name"),
                        "price": p.get("price"),
                        "mrp": p.get("mrp"),
                        "quantity": p.get("pack_size"),
                        "latitude": lat,
                        "longitude": lng
                    })
            else:
                print(f"Failed to fetch data for category {l2} at location ({lat}, {lng})")
        except Exception as e:
            print(f"Error fetching {l2} at ({lat}, {lng}): {e}")

output_path = '../output/blinkit_scraped_data.csv'
os.makedirs(os.path.dirname(output_path), exist_ok=True)
pd.DataFrame(all_products).to_csv(output_path, index=False)
print(f"Data saved to {output_path}")
