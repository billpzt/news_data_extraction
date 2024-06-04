import os
import re
import requests
import openpyxl
from robocorp import storage
from Locators import Locators as loc
from FileUtils import FileUtils

class Utils:

    @staticmethod
    def search_phrase_counter(search_phrase, title, description):
        return (title.count(search_phrase) + description.count(search_phrase))

    @staticmethod
    def contains_monetary_amount(text):
        """Check if the text contains any monetary amount."""
        pattern = r"\$?\d+(\.\d{2})? dollars?|USD|euro|€"
        return bool(re.search(pattern, text))
    
    @staticmethod
    def picture_extraction(local, article):
        """Extract picture URL from an article and download the picture."""
        try:
            e_img = article.query_selector(
                loc.article_image_xpath).as_element()
            picture_url = e_img.get_attribute("src")
        except Exception:
            picture_url = ''
            picture_filename = ''
        else:
            picture_filename = FileUtils.download_picture(picture_url, local)
        return picture_filename
