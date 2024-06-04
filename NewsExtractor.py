import logging
from robocorp.tasks import task
from robocorp import browser
import time
from Utils import Utils
from DateUtils import DateUtils
from FileUtils import FileUtils
from Locators import Locators as loc

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
            page = self.browser.page()
            page.goto(self.base_url, timeout=60000)
            self.logger.info("Opened the news site")
        except Exception as e:
            self.logger.exception("Failed to open the news site: %s", e)

    def click_on_search_button(self):
        """Click on search button to open search bar"""
        try:
            page = self.browser.page()
            page.click(loc.search_button_xpath)
            self.logger.info("Clicked on search button")
        except Exception as e:
            self.logger.exception("Failed to click on search button: %s", e)

    def enter_search_phrase(self):
        """Enter the search phrase"""
        try:
            page = self.browser.page()
            page.fill(loc.searchbar_xpath, self.search_phrase)
            page.press(loc.searchbar_xpath, key="Enter")
            self.logger.info("Entered search phrase")
        except Exception as e:
            self.logger.exception("Failed to enter search phrase: %s", e)

    def filter_newest(self):
        """Filter only the most recent articles"""
        try:
            page = self.browser.page()
            page.select_option(loc.dropdown_xpath, index=[1])
            self.logger.info("Filtered newest articles")
        except Exception as e:
            self.logger.warning("Option not available: %s", e)

    def click_on_news_category(self):
        """Choose the news category to filter articles"""
        try:
            page = self.browser.page()
            category_checkbox_xpath = f'//label/span[contains(text(), "{self.news_category}")]'
            page.set_checked(category_checkbox_xpath, checked=True)
            self.logger.info("Clicked on news category")
        except Exception as e:
            self.logger.warning("Unable to click on checkbox: %s", e)

    def click_on_next_page(self):
        """Access next page of resultsd"""
        try:
            page = self.browser.page()
            page.click(loc.next_results_xpath)
            self.logger.info("Clicked on next page")
        except Exception as e:
            self.logger.warning("Unable to click on next page: %s", e)

    def extract_articles_data(self):
        """Extract data from news articles"""
        page = self.browser.page()
        articles = page.locator(loc.articles_xpath).element_handles()
        valid_date = False

        for article in articles:
            raw_date = article.query_selector(
                loc.article_date_xpath).text_content()
            date = DateUtils.date_formatter(date=raw_date)
            valid_date = DateUtils.date_checker(date_to_check=date, months=self.months)

            if (valid_date):
                title = article.query_selector(
                    loc.article_title_xpath).text_content()
                description = article.query_selector(
                    loc.article_description_xpath).text_content()
                picture_filename = Utils.picture_extraction(
                    self.local, article=article)

                count_search_phrases = Utils.search_phrase_counter(self.search_phrase, title, description)
                monetary_amount = Utils.contains_monetary_amount(title) or Utils.contains_monetary_amount(description)

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
            if goto_next_page:
                self.click_on_next_page()
                page = browser.page()
                page.wait_for_selector(loc.articles_xpath, state="visible", timeout=10000)
        self.logger.info(f"Extracted data from {self.results_count} articles")

    def run(self):
        """Runs full extraction process"""
        self.open_site()
        self.click_on_search_button()
        self.enter_search_phrase()
        self.filter_newest()
        self.click_on_news_category()
        time.sleep(5)
        self.paging_for_extraction()
        FileUtils.save_to_excel(results=self.results, local=self.local)
