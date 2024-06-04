import os
import re
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import requests
import openpyxl
from robocorp import storage
from Locators import Locators as loc

class Utils:

    @staticmethod
    def date_formatter(date_str):
        """Format date string into a date object."""
        date_formats = ['%B %d, %Y', '%b. %d, %Y']
        for date_format in date_formats:
            try:
                return datetime.strptime(date_str, date_format).date()
            except ValueError:
                continue
        return datetime.today().date()

    @staticmethod    
    def date_checker(date_to_check, months):
        """Check if the date is within the specified months range."""
        number_of_months = months or 1
        cutoff_date = datetime.today().date() - relativedelta(months=number_of_months)
        return date_to_check >= cutoff_date
    
    @staticmethod
    def contains_monetary_amount(text):
        """Check if the text contains any monetary amount."""
        pattern = r"\$?\d+(\.\d{2})? dollars?|USD|euro|€"
        return bool(re.search(pattern, text))
    
    @staticmethod
    def download_picture(picture_url, local=True):
        """Download picture and save it locally or as an asset."""
        output_dir = os.path.join(os.getcwd(), "output", "images") if local else "./output"
        os.makedirs(output_dir, exist_ok=True)

        sanitized_filename = re.sub(r'[\\/*?:"<>|]', "", os.path.basename(picture_url))
        if not sanitized_filename.lower().endswith('.jpg'):
            sanitized_filename += ".jpg"
        picture_filename = os.path.join(output_dir, sanitized_filename)

        try:
            response = requests.get(picture_url, stream=True)
            response.raise_for_status()
            with open(picture_filename, 'wb') as file:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        file.write(chunk)
            print(f"Picture downloaded successfully: {picture_filename}")

            if not local:
                storage.set_file(sanitized_filename, picture_filename)

                return picture_filename
        except requests.RequestException as e:
            print(f"Error downloading picture: {e}")
            return None
    
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
            picture_filename = Utils.download_picture(picture_url, local)
        return picture_filename

    @staticmethod
    def save_to_excel(results, local=True):
        """Save extracted results to an Excel file."""
        wb = openpyxl.Workbook()
        ws = wb.active

        headers = ["Title", "Date", "Description", "Picture Filename",
                   "Search Phrase Count", "Monetary Amount"]
        ws.append(headers)

        for result in results:
            row = [
                result["title"],
                result["date"],
                result["description"],
                result["picture_filename"],
                result["count_search_phrases"],
                result["monetary_amount"]
            ]
            ws.append(row)

        output_dir = "./output"
        os.makedirs(output_dir, exist_ok=True)
        excel_path = os.path.join(output_dir, 'results.xlsx')
        wb.save(excel_path)

        if not local:
            asset_name = "results.xlsx"
            storage.set_file(asset_name, excel_path)
