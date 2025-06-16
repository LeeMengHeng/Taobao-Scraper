# Taobao Image Search Scraper (No Login Version)
# Description: Uploads client images to Taobao's search-by-image page, scrapes similar product listings.

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import csv

# Configurations
IMAGE_FOLDER = "images"
OUTPUT_FILE = "taobao_results.csv"
NUM_RESULTS = 10  # number of listings to scrape per image

# Setup Chrome WebDriver
chrome_options = Options()
chrome_options.add_argument('--headless')  # run in headless mode if needed
chrome_options.add_argument('--disable-gpu')
driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 15)

# Output storage
results = []

# Process each image in folder
for filename in os.listdir(IMAGE_FOLDER):
    if not filename.lower().endswith(('png', 'jpg', 'jpeg')):
        continue

    image_path = os.path.abspath(os.path.join(IMAGE_FOLDER, filename))
    print(f"\n🖼️ Uploading image: {filename}")

    # Step 1: Navigate to Taobao image search
    driver.get("https://s.taobao.com/search?type=image")
    time.sleep(3)

    # Step 2: Upload image using file input
    try:
        upload_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']")))
        upload_input.send_keys(image_path)
    except Exception as e:
        print(f"❌ Failed to upload image {filename}: {e}")
        continue

    # Step 3: Wait for results to appear
    try:
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".items .item")))
        time.sleep(3)
    except:
        print(f"❌ No search results found for {filename}")
        continue

    # Step 4: Scrape product listings
    items = driver.find_elements(By.CSS_SELECTOR, ".items .item")[:NUM_RESULTS]
    for item in items:
        try:
            title = item.find_element(By.CSS_SELECTOR, ".title").text
            price = item.find_element(By.CSS_SELECTOR, ".price").text
            link = item.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
            results.append({
                "image": filename,
                "title": title,
                "price": price,
                "link": link
            })
        except:
            continue

# Save results
with open(OUTPUT_FILE, "w", newline='', encoding="utf-8-sig") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=["image", "title", "price", "link"])
    writer.writeheader()
    writer.writerows(results)

print(f"\n✅ Done. Found {len(results)} results. Saved to: {OUTPUT_FILE}")
driver.quit()
