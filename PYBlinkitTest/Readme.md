# BlinkIt Subcategory Scraper

This project scrapes BlinkIt product data for various categories and locations using their public API.

## 📁 Folder Structure
- `data/`: Contains input category and location CSVs
- `output/`: Stores the scraped product data in CSV format
- `src/`: Contains the Python script
- `requirements.txt`: Lists required Python packages

## 🛠️ How to Run

1. Install dependencies: 
pip install -r requirements.txt

2. Run the scraper:
python src/blinkit_scraper.py

3. Output will be saved in:
output/blinkit_scraped_data.csv