import os
import re
import time

from Article import Article

import openpyxl
import requests

from RPA.Excel.Files import Files
from datetime import datetime, timedelta

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
        # self.page = self.driver.get(self.base_url)
        self.find_one_by_xpath = find_element_by_xpath = lambda xpath: self.driver.find_element(By.XPATH, xpath)
        self.find_many_by_xpath = find_elements_by_xpath = lambda xpath: self.driver.find_elements(By.XPATH, xpath)
        self.find_one_by_id = find_element_by_id = lambda id: self.driver.find_element(By.ID, id)
        self.results = []
        # Configure logging
        # logging.basicConfig(filename='news_extractor.log', level=logging.INFO)

    def open_site(self):
        # Open the news site
        driver = self.driver
        driver.get(self.base_url)                
    
    def click_on_search_button(self):
        # Click on search button to open search bar
        search_button_xpath = "//button[contains(@data-element, 'search-button')]"
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
                self.driver.execute_script("arguments[0].click();", search_button)
            except Exception as e:
                print(f"Failed to click the search button using JavaScript: {e}")

    def enter_search_phrase(self):
        # Enter the search phrase
        searchbar_xpath = "//input[contains(@name, 'q')]"
        searchbar = self.find_one_by_xpath(searchbar_xpath)
        searchbar.send_keys(self.search_phrase)
        searchbar.send_keys(Keys.RETURN)
        
    def extract_articles_data(self):
        """Extract data from news articles"""
        # article_xpath = '//ul[@class="search-results-module-results-menu"]/li'
        # article_title_xpath = ".//h3[contains(@class, 'promo-title')]"
        # article_description_xpath = ".//p[contains(@class, 'promo-description')]"
        # article_image_xpath = ".//img[contains(@class, 'image')]"
        # article_date_xpath = ".//p[contains(@class, 'promo-timestamp')]"

        articles = self.driver.find_elements(By.XPATH, '//ul[@class="search-results-module-results-menu"]/li')

        for article in articles:
            title = article.find_element(By.XPATH, './/h3[@class="promo-title"]').text

            try:
                description = article.find_element(By.XPATH, './/p[@class="promo-description"]').text
            except:
                description = ''

            # Convert date string to datetime object
            date = article.find_element(By.XPATH, './/p[@class="promo-timestamp"]').text
            # try:
            #     date = datetime.strptime(date, '%B %d, %Y')
            # except:
            #     date = datetime.strptime(date, '%B. %d, %Y')

            # Download picture if available and extract the filename
            try:
                e_img = article.find_element(By.XPATH, './/img[@class="image"]')
            except:
                picture_url = ''
                picture_filename = ''
            else:
                picture_url = e_img.get_attribute("src")
                picture_filename = self.download_picture(picture_url)

            # Count search phrase occurrences in title and description
            count_search_phrases = (title.count(self.search_phrase) + description.count(self.search_phrase))

            # Check if title or description contains any amount of money
            monetary_amount = self.contains_monetary_amount(title) or self.contains_monetary_amount(description)

            # Store extracted data in a dictionary
            article_data = {
                "title": title,
                "date": date,#.strftime("%Y-%m-%d"),
                "description": description,
                "picture_filename": picture_filename,
                "count_search_phrases": count_search_phrases,
                "monetary_amount": monetary_amount
            }
            

            self.results.append(article_data)

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
        wb = openpyxl.Workbook()
        ws = wb.active

        headers = ["Title", "Date", "Description", "Picture Filename", "Count of Search Phrases", "Monetary Amount"]
        ws.append(headers)

        # Write the data rows
        for result in self.results:
            print(result)
            row = [
                result["title"],
                result["date"],
                result["description"],
                result["picture_filename"],
                result["count_search_phrases"],
                result["monetary_amount"]
            ]
            ws.append(row)
        wb.save('results2.xlsx')
        

    def close_site(self):
        # Close the browser
        self.driver.close()

    def run(self):
        # Execute the entire news extraction process
        self.open_site()
        self.click_on_search_button()
        self.enter_search_phrase()
        self.extract_articles_data()
        self.save_to_excel()
        self.close_site()
