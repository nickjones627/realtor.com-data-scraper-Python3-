# Realtor.com Property Scraper

This Python script scrapes property listings from Realtor.com based on user-inputted city and filters. It retrieves information such as price, address, number of bedrooms, bathrooms, and additional property details, then saves the results into a CSV file.

## Features

- **User Input**: Accepts a city and state from the user to customize the search.
- **User Input**: formatted as such "gun barrel city tx", "san francisco ca", etc
- **Flexible Filters**: Allows the user to apply various filters such as sorting by price, number of bedrooms, bathrooms, and whether the property is for rent.
- **Pagination**: Automatically handles multiple pages of listings.
- **Property Details**: Scrapes detailed information about each property, including price, address, number of bedrooms, and bathrooms.
- **CSV Output**: Saves the scraped data into a CSV file for easy access and analysis.

## Reminders

Do not forget to insert you browsers user agent string in the "headers" dictionary on ln 14

Try not to get impatient, logging has been set up so you can track the status. It will take
roughly 5 minutes per 250 listings.

## Requirements

Create a folder "output" in the same directory to properly output the .csv file

Ensure you have the requirements installed using the following command:

```bash
pip install -r requirements.txt

