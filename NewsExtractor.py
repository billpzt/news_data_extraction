import os
import re

from robocorp.tasks import task
from robocorp import browser

from RPA.HTTP import HTTP
from RPA.Excel.Files import Files
from RPA.PDF import PDF

from selenium.webdriver.common.by import By

from datetime import datetime

class NewsExtractor:
    def __init__(self, search_phrase,  months=None, news_category=None):
        self.search_phrase = search_phrase
        self.months = months
        self.news_category = news_category
        self.browser = browser
        self.base_url = "https://apnews.com/"
        self.results = []
        # Configure logging
        # logging.basicConfig(filename='news_extractor.log', level=logging.INFO)

    def open_site(self):
        """Navigates to the given URL"""
        self.browser.goto(self.base_url)

    def search_news(self):
        """Find the search bar and enter the search phrase"""
        page = self.browser.page()
        search_icon_locator = '#Page-header-menu > bsp-header > div > div.Page-header-end > bsp-search-overlay > button'
        page.click(search_icon_locator)
        search_bar_locator = '//*[@id="Page-header-menu"]/bsp-header/div/div[3]/bsp-search-overlay/div/form/label/input'
        page.fill(search_bar_locator, self.search_phrase)
        page.press(search_bar_locator, 'Enter')

    def set_latest_news(self):
        """Set latest news using dropdown option"""
        page = self.browser.page()
        dropdown_menu_locator = "/html/body/div[3]/bsp-search-results-module/form/div[2]/div/bsp-search-filters/div/main/div[1]/div/div/div/label/select"
        page.click(dropdown_menu_locator)
        newest_option_locator = "/html/body/div[3]/bsp-search-results-module/form/div[2]/div/bsp-search-filters/div/main/div[1]/div/div/div/label/select/option[2]"
        page.click(newest_option_locator)

    def extract_data(self):
        """Extract data from news articles"""
        # page = self.browser.page()

        articles = self.browser.find_elements(By.CSS_SELECTOR, ".article-selector") # Update CSS selector as needed

        for article in articles:
            title = article.find_element(By.CSS_SELECTOR, ".title-selector").text
            date = article.find_element(By.CSS_SELECTOR, ".date-selector").text
            description = article.find_element(By.CSS_SELECTOR, ".description-selector").text
            
            # Convert date string to datetime object
            date = datetime.strptime(date, "%Y-%m-%d")

            # Download picture if available and extract the filename
            picture_url = article.find_element(By.CSS_SELECTOR, ".picture-selector").get_attribute("src")
            picture_filename = self.download_picture(picture_url)
            
            # Count search phrase occurrences in title and description
            count_search_phrases = (title.count(self.search_phrase) + description.count(self.search_phrase))
            
            # Check if title or description contains any amount of money
            monetary_amount = self.contains_monetary_amount(title) or self.contains_monetary_amount(description)
            
            # Store extracted data in a dictionary
            article_data = {
                "title": title,
                "date": date.strftime("%Y-%m-%d"),
                "description": description,
                "picture_filename": picture_filename,
                "count_search_phrases": count_search_phrases,
                "monetary_amount": monetary_amount
            }
            
            self.results.append(article_data)

    def download_picture(self, picture_url):
        # Download picture from the given URL and save it locally
        picture_filename = os.path.join("images", os.path.basename(picture_url))
        self.browser.download(picture_url, picture_filename)
        return picture_filename
    
    def contains_monetary_amount(self, text):
        # Check if the text contains any monetary amount (e.g. $11.1, 11 dollars, etc.)
        pattern = r"\$?\d+(\.\d{2})? dollars?|USD|euro|€"
        return bool(re.search(pattern, text))
    
    def save_to_excel(self):
        lib = Files()
        lib.create_workbook()
        lib.save_workbook("results.xlsx")

        # Write the header row
        headers = ["Title", "Date", "Description", "Picture Filename", "Count of Search Phrases", "Monetary Amount"]
        lib.append_rows_to_worksheet(headers)
        
        # Write the data rows
        for result in self.results:
            row = [
                result["title"],
                result["date"],
                result["description"],
                result["picture_filename"],
                result["count_search_phrases"],
                result["monetary_amount"]
            ]
            lib.append_rows_to_worksheet(row)

        lib.save_workbook()

    def close_site(self):
        # Close the browser
        self.browser.close_all_browsers()

    def run(self):
        # Execute the entire news extraction process
        self.open_site()
        self.search_news()
        self.set_latest_news()
        self.extract_data()
        self.save_to_excel()
        self.close_site()