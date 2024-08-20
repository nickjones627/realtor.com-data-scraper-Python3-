import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

#& Base URL of the website
base_url = "https://www.realtor.com/international/us/"

#! CHANGE the User Agent to match your browsers personal agent string
headers = {
    "User-Agent": "YOUR USER AGENT STRING HERE"
    }

# Whatever filter you wish to use, simply add it into the end of 'complete_url' function as "filters['Price L to H']" #!The order you add them is important
filters = {"Price L to H": "sort=price+asc",
           "Price H to L": "sort=price+desc",
           "New Listings": "sort=date+desc",
           "Min Beds": "minbed=2",
           "Bathrooms":"numbaths=1",
           "Max Price":"maxprice=300000",
           "For Rent": "rent"}

# User input URL
import_url = input('Use the following format `city state`(gun barrel city tx)\nPlease enter a city & state: ')
import_url = re.sub(r"\s+", '-', import_url)


#! IMPORTANT -
# For the first filter after "{import_url}" you must format it as such
#&                          {import_url}?{filters['filter']}
# For any filter following the first one, you must format it as follows
#&                          {import_url}?{filters['filter']}&{filters['filter']}
complete_url = f"{base_url}{import_url}"


# Start with the first page
page_number = 1
has_more_pages = True

# List to hold all property data
property_list = []

while has_more_pages:
    try:
        # Enter the full URL with desired filters #!Remember the format from above
        url = f"{complete_url}/p{page_number}"
        logging.info(f"Scraping page {page_number}: {url}")
        response = requests.get(url, headers=headers, timeout=5)  #! Add a timeout to prevent hanging/IP ban
        
        if response.status_code != 200:
            logging.warning(f"Failed to retrieve page {page_number}. Status code: {response.status_code}")
            break

        soup = BeautifulSoup(response.content, "html.parser")
        
        # Extract data from the page
        items = soup.find_all('div', class_='sc-1dun5hk-0 cOiOrj')
        
        if not items:
            logging.info("No more items found.")
            break
        
        for item in items:
            # Extract the URL to the property details page
            property_url = item.find('a')['href']
            
            # Full URL to the property details page
            full_property_url = f"https://www.realtor.com{property_url}"
            
            # Request the property details page
            try:
                property_response = requests.get(full_property_url)
                property_soup = BeautifulSoup(property_response.content, "html.parser")
                
                # Extract specific details from the property page
                price = property_soup.find('div', class_='sc-10v3xoh-0 kgiZMN property-price').get_text(strip=True) if property_soup.find('div', class_='sc-10v3xoh-0 kgiZMN property-price') else "N/A"
                address = property_soup.find('h1', class_='display-address').get_text(strip=True) if property_soup.find('h1', class_='display-address') else "N/A"
                
                # Beds/ Baths
                beds = "N/A"
                baths = "N/A"
                features = property_soup.find_all('div', class_='feature-item')
                
                for feature in features:
                    img = feature.find('img')
                    if img:
                        if img.get('alt') == 'bedrooms':
                            beds = feature.get_text(strip=True)
                        elif img.get('alt') == 'bathrooms':
                            baths = feature.get_text(strip=True)

                # Extract and format the basic information from the 'ant-col' elements
                columns = property_soup.find_all('div', class_='ant-col')
                basic_info_list = []
                for col in columns:
                    text = col.get_text(strip=True)
                    if text:
                        basic_info_list.append(text)
                
                basic_info = '\n'.join(basic_info_list)

                # Truncate basic_info at the word "Address"
                if "Address" in basic_info:
                    basic_info = basic_info.split("Address")[0].strip()

                # Add property details to the list
                property_list.append({
                    "Address": address,
                    "Price": price.replace('USD $', ''),
                    "Basic Information": basic_info,
                    "Bedrooms": beds,
                    "Bathrooms": baths,
                    "URL": full_property_url
                })
                
            except requests.exceptions.RequestException as e:
                logging.error(f"Failed to retrieve property details from {full_property_url}. Error: {e}")
                continue

        # Check if there is a next page (this will depend on the website's structure)
        next_button = soup.find('li', class_='ant-pagination-next')
        
        if next_button and 'disabled' not in next_button.get('class', []):
            page_number += 1
        else:
            logging.info("No more pages to scrape.")
            has_more_pages = False

        # Add a short delay to avoid being blocked
        time.sleep(1)

    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to retrieve page {page_number}. Error: {e}")
        break

# Convert the list of property details into a DataFrame
property_data_frame = pd.DataFrame(property_list)

# Save the DataFrame to a CSV file
property_data_frame.to_csv(f"output\\{import_url}.csv", index=False)

logging.info(f"Property data has been saved to '{import_url}.csv'")
