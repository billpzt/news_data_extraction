import time

from robocorp.tasks import task
# from robocorp import browser
from RPA.Browser.Selenium import Selenium
from datetime import datetime, timedelta
import openpyxl

# find_element_by__xpath = lambda xpath: driver.find_element(By.XPATH, xpath)
# find_elements_by_xpath = lambda xpath: driver.find_elements(By.XPATH, xpath)
# find_element_by_id = lambda id: driver.find_element(By.ID, id)

class NewsExtractor:
    def __init__(self, search_phrase,  months=None, news_category=None):
        self.search_phrase = search_phrase
        self.months = months
        self.news_category = news_category
        # self.browser = browser.configure(slowmo=100)
        self.browser = Selenium()
        self.base_url = "https://apnews.com/"
        self.results = []
        # Configure logging
        # logging.basicConfig(filename='news_extractor.log', level=logging.INFO)

    def extract_news_data(self):
        # Open the news site
        # page = self.browser.page()
        # page.goto(self.base_url)
        print('AAAAAAAAAAAAAAAAAAAAAAAA')
        self.browser.open_browser(self.base_url)
        print('BBBBBBBBBBBBBBBBBBBBBBBB')
        page = self.browser.page()
        print('CCCCCCCCCCCCCCCCCCCCCCCC')
        time.sleep(5)

        # Click on search button to open search bar
        search_button_selector = "button.SearchOverlay-search-button"
        
        self.browser.wait_until_element_is_visible(search_button_selector, timeout=40)
        self.browser.click_element(search_button_selector)
        # page.wait_until_element_is_visible(search_button_selector, timeout=30)
        # page.click_element(search_button_selector)
        
        # Enter the search phrase
        page.fill("input[name='q']", self.search_phrase)
        page.press("input[name='q']", "Enter")
        
        # If possible, select a news category or section
        # This step may require specific logic based on the site's structure
        
        # Choose the latest news and process data
        # This will involve iterating through search results and filtering based on date
        
    def save_to_excel(self):
        pass
        # Store data in an Excel file
        # This example assumes you have a workbook and worksheet already set up
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.append(["Title", "Date", "Description", "Picture Filename", "Count", "Contains Money"])
    
        # Example of appending a row to the Excel sheet
        # sheet.append([title, date, description, picture_filename, count, contains_money])
    
        # Save the workbook
        workbook.save(filename="news_data.xlsx")

    def close_site(self):
        pass

    def run(self):
        # Execute the entire news extraction process
        print('XXXXXXXXXXXXXXX')
        self.extract_news_data()
        print('YYYYYYYYYYYYYYY')
        # self.save_to_excel()
        # self.close_site()