import subprocess
import sys
import re
import logging

# List of libraries to check and install if not available
libraries = ['selenium', 'beautifulsoup4', 'webdriver-manager', 'pandas', 'openpyxl']

print("Checking and installing required libraries...")

for lib in libraries:
    try:
        __import__(lib)
    except ImportError:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', lib])

# After installing required libraries, import them
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from bs4 import BeautifulSoup
    from webdriver_manager.chrome import ChromeDriverManager
    import pandas as pd
except ImportError as e:
    print(f"Error importing necessary libraries: {e}")
    sys.exit(1)

# Chrome options to ignore SSL errors
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--ignore-ssl-errors=yes')
chrome_options.add_argument('--ignore-certificate-errors')

# Initialize WebDriver with Chrome options
print("Starting Driver...")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

make = input("Make of Car: ").lower()
model = input("Model of Car: ").lower()
zip_code = input("Zip Code: ").lower()
radius = input("Area to search: ").lower()

url = f"https://www.autotempest.com/results?make={make}&model={model}&zip={zip_code}&radius={radius}"

Listings = []
Listings.append(["Model", "Year", "Mileage", "Price", "Location"])

# Load the page
driver.get(url)
print("Collecting Data...")

try:
    # Wait for the results container to be present
    wait = WebDriverWait(driver, 20)
    results_container = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "results-target")))

    if results_container:
        print("Results container found.")
    else:
        print("Results container not found.")

    # Get the page source after waiting
    page_source = driver.page_source

    # Parse the page source with BeautifulSoup
    soup = BeautifulSoup(page_source, 'html.parser')

    # Find all car listings by getting result list item class
    car_listings = soup.find_all('li', class_='result-list-item')

    if not car_listings:
        print("No car listings found.")
    else:
        print(f"Found {len(car_listings)} car listings.")

        # Extract details from each listing list item
        for listing in car_listings:
            description_wrap = listing.find('div', class_='description-wrap')
            if description_wrap:
                title_tag = description_wrap.find('a', class_='listing-link source-link')
                title = title_tag.get_text(strip=True) if title_tag else 'N/A'
                
                # Extract price from the description badg classes
                price_wrap = listing.find('div', class_='price-wrap')
                if price_wrap:
                    description_badges = price_wrap.find('div', class_='description-badges')
                    if description_badges:
                        price_badge = description_badges.find('div', class_='description-badges__price_badge badge')
                        if price_badge:
                            badge_labels = price_badge.find('div', class_='badge__labels')
                            if badge_labels:
                                price_tag = badge_labels.find('div', class_='badge__label label--price')
                                price = price_tag.get_text(strip=True) if price_tag else 'N/A'
                            else:
                                price = 'N/A'
                        else:
                            price = 'N/A'
                    else:
                        price = 'N/A'
                else:
                    price = 'N/A'
                
                # Extracting mileage from mileage tag
                mileage_tag = description_wrap.find('span', class_='mileage')
                mileage = mileage_tag.get_text(strip=True) if mileage_tag else 'N/A'
                mileage = mileage.replace(" mi.", "")
                mileage = int(mileage.replace(",", ""))
                
                # Extract location from location class
                location_tag = description_wrap.find('div', class_='location')
                location = location_tag.get_text(strip=True) if location_tag else 'N/A'
                
                # Print extracted details
                year = title[0:4]
                
                if(price != "Inquire"):
                    Listings.append([title[5:], int(year), mileage, price, location])
            else:
                print("Description wrap not found for a listing.")
finally:
    # Quit the driver
    driver.quit()

print("Scraping Done!")
print("Creating excel file...")

try: 
    #Produce excel file using pandas data frame
    file_name = f"listings_{model}.xlsx"

    df = pd.DataFrame(Listings)
    df.to_excel(file_name, index=False)

    print(f"Data saved successfully to {file_name}!")

except:
    print("Error: Could not produce excel file.")
