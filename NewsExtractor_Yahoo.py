import time

from robocorp.tasks import task
# from robocorp import browser
from RPA.Browser.Selenium import Selenium
from datetime import datetime, timedelta
import openpyxl

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
        self.base_url = "https://news.yahoo.com/"
        self.results = []
        # Configure logging
        # logging.basicConfig(filename='news_extractor.log', level=logging.INFO)

    def extract_news_data(self):
        find_element_by_xpath = lambda xpath: driver.find_element(By.XPATH, xpath)
        find_elements_by_xpath = lambda xpath: driver.find_elements(By.XPATH, xpath)
        find_element_by_id = lambda id: driver.find_element(By.ID, id)
        
        # Open the news site
        driver = self.driver
        driver.get(self.base_url)

        # Enter the search phrase
        searchbar_xpath = '//*[@id="Page-header-trending-zephr"]/div[1]/div[3]/bsp-search-overlay/div/form/label/input'
        searchbar = find_element_by_xpath(searchbar_xpath)
        searchbar.send_keys(self.search_phrase)
        searchbar.send_keys(Keys.RETURN)
        # page.fill("input[name='q']", self.search_phrase)
        # page.press("input[name='q']", "Enter")
        
        # If possible, select a news category or section
        # This step may require specific logic based on the site's structure
        
        # Choose the latest news and process data
        # This will involve iterating through search results and filtering based on date

        # Click on search button to open search bar
        # search_button_selector = "button.SearchOverlay-search-button"
        search_button_xpath = '//*[@id="Page-header-menu"]/bsp-header/div/div[3]/bsp-search-overlay/button'
        search_button_svg_xpath = '//*[@id="Page-header-menu"]/bsp-header/div/div[3]/bsp-search-overlay'
        search_button = None # Initialize search_button to None
        # search_button = find_element_by__xpath(search_button_xpath)
        # search_button = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, search_button_selector)))
        close_popup_xpath = '//*[@id="bx-element-2475153-3lqb4uR"]/button'
        if (find_element_by_xpath(close_popup_xpath).accessible_name):
            close_popup_button = find_element_by_xpath(close_popup_xpath)
            close_popup_button.click()
        # search_button_by_class_name = driver.find_element_by_class_name('SearchOverlay-search-button')
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
                driver.execute_script("document.getElementsByClassName('SearchOverlay-search-button')[0].click()")
            except Exception as e:
                print(f"Failed to click the search button using JavaScript: {e}")
        # search_button.click()
        # self.browser.wait_until_element_is_visible(search_button_selector, timeout=40)
        # self.browser.click_element(search_button_selector)
        
        # Enter the search phrase
        searchbar_xpath = '//*[@id="Page-header-trending-zephr"]/div[1]/div[3]/bsp-search-overlay/div/form/label/input'
        searchbar = find_element_by_xpath(searchbar_xpath)
        searchbar.send_keys(self.search_phrase)
        searchbar.send_keys(Keys.RETURN)
        # page.fill("input[name='q']", self.search_phrase)
        # page.press("input[name='q']", "Enter")
        
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
