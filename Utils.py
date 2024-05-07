import os
import re
import logging
import requests
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class Utils:
    def __init__(self):
        self.logger = logging.getLogger('NewsExtractor')
        self.logger.setLevel(logging.INFO)
        handler = logging.FileHandler('news_extractor.log')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def date_formatter(date):
        try:
            date = datetime.strptime(date, '%B %d, %Y')
        except:
            try:
                date = datetime.strptime(date, '%b. %d, %Y')
            except:
                date = datetime.today() # Ex: 24/04/2024

        # Ensure only the date part is stored
        return date.date()
    
    def date_checker(date_to_check, months):
        number_of_months = months
        if (months == 0):
            number_of_months = 1
        # Calculate the date 'months' months ago from today
        cutoff_date = datetime.today().date() - relativedelta(months=number_of_months)
        # Check if the date_to_check is within the last 'months' months
        return date_to_check >= cutoff_date

    def download_picture(self, picture_url):
        # Prepare the local path for the picture
        output_dir = os.path.join(os.getcwd(), "output", "images")  # Using current working directory
        os.makedirs(output_dir, exist_ok=True)  # Ensure the directory exists

        sanitized_filename = re.sub(r'[\\/*?:"<>|]', "", os.path.basename(picture_url))
        filename_root, filename_ext = os.path.splitext(sanitized_filename)
        if filename_ext.lower() != '.jpg':
            sanitized_filename += ".jpg"
        picture_filename = os.path.join(output_dir, sanitized_filename)

        try:
            # Download the picture
            response = requests.get(picture_url, stream=True)
            if response.status_code == 200:
                with open(picture_filename, 'wb') as file:
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            file.write(chunk)
                return picture_filename
            else:
                self.logger.error(f"Failed to download picture from {picture_url}. Status code: {response.status_code}")
        except Exception as e:
            logging.exception(e)

        return None

    def contains_monetary_amount(text):
        # Check if the text contains any monetary amount (e.g. $11.1, 11 dollars, etc.)
        pattern = r"\$?\d+(\.\d{2})? dollars?|USD|euro|€"
        return bool(re.search(pattern, text))
