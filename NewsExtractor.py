import logging
from RPA.Browser.Selenium import By, Selenium
from datetime import timedelta
from robocorp.tasks import task
from robocorp import browser
import time

from Utils import Utils
from Locators import Locators as loc



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
        self.local = local
        self.logger = self.configure_logging()

    def configure_logging(self) -> logging.Logger:
        """Configure and return logger"""
        logger = logging.getLogger('NewsExtractor')
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler('news_extractor.log')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def open_site(self) -> None:
        """Open the news site"""
        try:
            page = browser.page()
            page.goto(self.base_url, timeout=60000)
            self.logger.info("Opened the news site")
        except Exception as e:
            self.logger.exception("Failed to open the news site: %s", e)

    def click_on_search_button(self):
        """Click on search button to open search bar"""
        # Wait for the search button to be present in the DOM and interactable
        page = browser.page()
        try:
            page.click(loc.search_button_xpath)
            self.logger.info("Clicked on search button")
        except Exception as e:
            self.logger.exception(e)

    def enter_search_phrase(self):
        """Enter the search phrase"""
        page = browser.page()
        try:
            page.fill(loc.searchbar_xpath, self.search_phrase)
            page.press(loc.searchbar_xpath, key="Enter")
            self.logger.info("Entered search phrase")
        except Exception as e:
            self.logger.exception(e)

    def filter_newest(self):
        """Filter only the most recent articles"""
        page = browser.page()
        try:
            page.select_option(loc.dropdown_xpath, index=[1])
            self.logger.info("Filtered newest articles")
        except Exception as error:
            self.logger.warning(f"Option not available - {str(error)}")

    def click_on_news_category(self):
        """Choose the news category to filter articles"""
        page = browser.page()
        try:
            category_text = self.news_category
            category_checkbox_xpath = f'//label/span[contains(text(), "{category_text}")]'
            page.set_checked(category_checkbox_xpath, checked=True)
            self.logger.info("Clicked on news category")
        except Exception as error:
            self.logger.warning(f"Unable to click on checkbox - {str(error)}")

    def click_on_next_page(self):
        """Access next page of resultsd"""
        page = browser.page()
        try:
            page.click(loc.next_results_xpath)
            self.logger.info("Clicked on next page")
        except Exception as e:
            self.logger.warning(f"Unable to click on next page - {str(e)}")

    def extract_articles_data(self):
        """Extract data from news articles"""
        page = browser.page()
        articles = page.locator(loc.articles_xpath).element_handles()
        months = self.months
        valid_date = False
        for article in articles:
            # Capture and convert date string to datetime object
            raw_date = article.query_selector(
                loc.article_date_xpath).text_content()
            date = Utils.date_formatter(date=raw_date)
            valid_date = Utils.date_checker(date_to_check=date, months=months)

            if (valid_date):
                title = article.query_selector(
                    loc.article_title_xpath).text_content()
                description = article.query_selector(
                    loc.article_description_xpath).text_content()
                picture_filename = Utils.picture_extraction(
                    self.local, article=article)

                # Count search phrase occurrences in title and description
                count_search_phrases = (title.count(
                    self.search_phrase) + description.count(self.search_phrase))

                # Check if title or description contains any amount of money
                monetary_amount = Utils.contains_monetary_amount(
                    title) or Utils.contains_monetary_amount(description)

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
                valid_date = False
                break
        return valid_date

    def paging_for_extraction(self):
        """Handles paging while date is valid"""
        goto_next_page = True
        while (goto_next_page):
            goto_next_page = self.extract_articles_data()
            self.click_on_next_page()
            # Wait for a specific element on the next page to ensure it has loaded
            browser.wait_until_page_contains_element(loc.articles_xpath, timeout=timedelta(seconds=10))
        print(f"Extracted data from {self.results_count} articles")

    def run(self):
        """Runs full extraction process"""
        # Execute the entire news extraction process
        self.open_site()
        self.click_on_search_button()
        self.enter_search_phrase()
        self.filter_newest()
        self.click_on_news_category()
        time.sleep(5)
        self.paging_for_extraction()
        if self.local:
            Utils.LOCAL_save_to_excel(self.results)
        else:
            Utils.save_to_excel(self.results)
