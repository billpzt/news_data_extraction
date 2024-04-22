import os
import requests
import re
import time

from robocorp.tasks import task
# from robocorp import browser
# from RPA.Browser.Selenium import Selenium
from RPA.Excel.Files import Files
from datetime import datetime, timedelta
# import openpyxl

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

class NewsExtractor:
    def __init__(self, search_phrase,  months=None, news_category=None):
        self.search_phrase = search_phrase
        self.months = months
        self.news_category = news_category
        self.driver = webdriver.Chrome()
        self.base_url = "https://www.latimes.com/"
        self.page = self.driver.get(self.base_url)
        self.find_one_by_xpath = find_element_by_xpath = lambda xpath: self.driver.find_element(By.XPATH, xpath)
        self.find_many_by_xpath = find_elements_by_xpath = lambda xpath: self.driver.find_elements(By.XPATH, xpath)
        self.find_one_by_id = find_element_by_id = lambda id: self.driver.find_element(By.ID, id)
        self.results = []
        # Configure logging
        # logging.basicConfig(filename='news_extractor.log', level=logging.INFO)

        

    def open_site_and_search(self):
        # find_element_by_xpath = lambda xpath: driver.find_element(By.XPATH, xpath)
        # find_elements_by_xpath = lambda xpath: driver.find_elements(By.XPATH, xpath)
        # find_element_by_id = lambda id: driver.find_element(By.ID, id)
        
        # Open the news site
        driver = self.driver
        # driver.get(self.base_url)
        
        # Click on search button to open search bar
        search_button_xpath = '/html/body/ps-header/header/div[2]/button'
        search_button = None # Initialize search_button to None
        
        # Wait for the search button to be present in the DOM and interactable
        try:
            # Wait for the element to be visible and interactable
            search_button = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, search_button_xpath))
            )
            # Attempt to click the search button using Selenium's click method
            search_button.click()
        except Exception as e:
            print(f"Failed to click the search button using Selenium's click method: {e}")
            # If the standard click does not work, use JavaScript to click the element
            try:
                # Use JavaScript to click the element
                driver.execute_script("arguments[0].click();", search_button)
            except Exception as e:
                print(f"Failed to click the search button using JavaScript: {e}")
                
        # Enter the search phrase
        searchbar_xpath = '/html/body/ps-header/header/div[2]/div[2]/form/label/input'
        searchbar = self.find_one_by_xpath(searchbar_xpath)
        searchbar.send_keys(self.search_phrase)
        searchbar.send_keys(Keys.RETURN)
        
        # If possible, select a news category or section
        match self.news_category:
            case "World & Nation":
                category_xpath = '/html/body/div[2]/ps-search-results-module/form/div[2]/ps-search-filters/div/aside/div/div[3]/div[1]/ps-toggler/ps-toggler/div/ul/li[1]/div/div[1]/label/input'
            case "Politics":
                category_xpath = '/html/body/div[2]/ps-search-results-module/form/div[2]/ps-search-filters/div/aside/div/div[3]/div[1]/ps-toggler/ps-toggler/div/ul/li[2]/div/div[1]/label/input'
            case _:
                print("Not a valid option")
        category_checkbox = self.find_one_by_xpath(category_xpath)
        category_checkbox.click()

        # Choose the latest news and process data
        # This will involve iterating through search results and filtering based on date
        
    def extract_data(self):
        """Extract data from news articles"""
        # page = self.browser.page()

        articles = self.driver.find_elements(By.CSS_SELECTOR, "promo-wrapper")

        for article in articles:
            title = article.find_element(By.CSS_SELECTOR, "promo-title").text
            date = article.find_element(By.CSS_SELECTOR, "promo-timestamp").text
            description = article.find_element(By.CSS_SELECTOR, "promo-description").text

            # Convert date string to datetime object
            date = datetime.strptime(date, "%Y-%m-%d")

            # Download picture if available and extract the filename
            picture_url = article.find_element(By.CSS_SELECTOR, "image").get_attribute("src")
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

    # def download_picture(self, picture_url):
    #     # Prepare the local path for the picture
    #     picture_filename = os.path.join("output", "images", os.path.basename(picture_url))
        
    #     # Ensure the directory exists
    #     os.makedirs("output/images", exist_ok=True)
        
    #     # Download the picture
    #     response = requests.get(picture_url, stream=True)
    #     if response.status_code == 200:
    #         with open(picture_filename, 'wb') as file:
    #             for chunk in response.iter_content(chunk_size=1024):
    #                 if chunk:
    #                     file.write(chunk)
    #     else:
    #         print(f"Failed to download picture from {picture_url}")
        
    #     # self.browser.download(picture_url, picture_filename)
    #     return picture_filename
    def download_picture(self, picture_url):
        # Prepare the local path for the picture
        output_dir = os.path.join(os.getcwd(), "output", "images")  # Using current working directory
        os.makedirs(output_dir, exist_ok=True)  # Ensure the directory exists

        picture_filename = os.path.join(output_dir, os.path.basename(picture_url))

        try:
            # Download the picture
            response = requests.get(picture_url, stream=True)
            if response.status_code == 200:
                with open(picture_filename, 'wb') as file:
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            file.write(chunk)
                print(f"Picture downloaded successfully: {picture_filename}")
                return picture_filename
            else:
                print(f"Failed to download picture from {picture_url}. Status code: {response.status_code}")
        except Exception as e:
            print(f"Error downloading picture: {e}")

        return None


    def contains_monetary_amount(self, text):
        # Check if the text contains any monetary amount (e.g. $11.1, 11 dollars, etc.)
        pattern = r"\$?\d+(\.\d{2})? dollars?|USD|euro|€"
        return bool(re.search(pattern, text))

    def save_to_excel(self):
        lib = Files()
        file_path = r"C:\Users\billp\Documents\PIXELDU\news_data_extraction\output"
        lib.create_workbook(file_path)
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
        self.driver.close()

    def run(self):
        # Execute the entire news extraction process
        self.open_site_and_search()
        self.extract_data()
        self.save_to_excel()
        self.close_site()
