import time
import logging
import openpyxl

from Utils import Utils
from Locators import Locators as loc

from RPA.Browser.Selenium import By, Selenium
from robocorp.tasks import task
from robocorp import browser

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# from loguru import logger as loguru_logger

class NewsExtractor:
    def __init__(self, search_phrase,  months=None, news_category=None, local=True):
        self.search_phrase = search_phrase
        self.months = months
        self.news_category = news_category
        self.browser = browser
        self.base_url = "https://www.latimes.com/"
        self.results = []
        self.results_count = 0
        # Configure logging
        self.logger = logging.getLogger('NewsExtractor')
        self.logger.setLevel(logging.INFO)
        handler = logging.FileHandler('news_extractor.log')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.local = local

    def open_site(self):
        """Open the news site"""
        page = browser.page()
        # Increase the timeout to 60 seconds (60000 milliseconds)
        page.goto(self.base_url, timeout=60000)
        self.logger.info("Opened the news site")         

    def click_on_search_button(self):
        """Click on search button to open search bar"""                
        # Wait for the search button to be present in the DOM and interactable
        page = browser.page()
        try:
            page.click(loc.search_button_xpath)
        except Exception as e:
            self.logger.exception(e)
                
    def enter_search_phrase(self):
        """Enter the search phrase"""
        page = browser.page()
        try:
            page.fill(loc.searchbar_xpath, self.search_phrase)
            page.press(loc.searchbar_xpath, key="Enter")
        except Exception as e:
            self.logger.exception(e)

    def filter_newest(self):
        """Filter only the most recent articles"""
        page = browser.page()
        try:
            page.select_option(loc.dropdown_xpath, index=[1])
        except Exception as error:
            self.logger.warning(f"Option not available - {str(error)}")
    
    def click_on_news_category(self):
        """Choose the news category to filter articles"""
        page = browser.page()
        try:
            category_text = self.news_category
            category_checkbox_xpath = f'//label/span[contains(text(), "{category_text}")]'
            page.set_checked(category_checkbox_xpath, checked=True)
        except Exception as error:
            self.logger.warning(f"Unable to click on checkbox - {str(error)}")

    def click_on_next_page(self):
        """Access next page of resultsd"""
        page = browser.page()
        try:
            page.click(loc.next_results_xpath)
        except Exception as e:
            self.logger.warning(f"Unable to click on next page - {str(e)}")
        
    def extract_articles_data(self):
        """Extract data from news articles"""
        page = browser.page()
        articles = page.locator(loc.articles_xpath).element_handles()
        
        for article in articles:
            # Capture and convert date string to datetime object
            raw_date = article.query_selector(loc.article_date_xpath).text_content()
            date = Utils.date_formatter(date=raw_date)
            months = self.months
            valid_date = Utils.date_checker(date_to_check=date, months=months)

            if (valid_date):
                title = article.query_selector(loc.article_title_xpath).text_content()
                description = article.query_selector(loc.article_description_xpath).text_content()

                picture_filename = Utils.picture_extraction(self.local, article=article)

                # Count search phrase occurrences in title and description
                count_search_phrases = (title.count(self.search_phrase) + description.count(self.search_phrase))

                # Check if title or description contains any amount of money
                monetary_amount = Utils.contains_monetary_amount(title) or Utils.contains_monetary_amount(description)

                # Store extracted data in a dictionary
                article_data = {
                    "title": title,
                    "date": date,
                    "description": description,
                    "picture_filename": picture_filename,
                    "count_search_phrases": count_search_phrases,
                    "monetary_amount": monetary_amount
                }
                
                self.results.append(article_data)
                self.results_count += 1
            else:
                break
        return valid_date
    
    def paging_for_extraction(self, goto_next_page=True):
        while (goto_next_page):
            goto_next_page = self.extract_articles_data()
            self.click_on_next_page()
        print(f"Extracted data from {self.results_count} articles")

    def run(self):
        # Execute the entire news extraction process
        self.open_site()
        self.click_on_search_button()
        self.enter_search_phrase()
        self.click_on_news_category()
        self.filter_newest()
        self.paging_for_extraction()
        if self.local:
            Utils.LOCAL_save_to_excel(self.results)
        else:
            Utils.save_to_excel(self.results)
