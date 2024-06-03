import os
import re

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

import requests

import openpyxl
from robocorp import storage
from RPA.Robocorp.Storage import Storage

from Locators import Locators as loc

work_items = _workitem

class Utils:
    def date_formatter(date):
        try:
            date = datetime.strptime(date, '%B %d, %Y')
        except:
            try:
                date = datetime.strptime(date, '%b. %d, %Y')
            except:
                date = datetime.today()  # Ex: 24/04/2024

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

    def contains_monetary_amount(text):
        # Check if the text contains any monetary amount (e.g. $11.1, 11 dollars, etc.)
        pattern = r"\$?\d+(\.\d{2})? dollars?|USD|euro|€"
        return bool(re.search(pattern, text))

    def LOCAL_download_picture(picture_url):
        # Prepare the local path for the picture
        # Using current working directory
        output_dir = os.path.join(os.getcwd(), "output", "images")
        os.makedirs(output_dir, exist_ok=True)  # Ensure the directory exists

        sanitized_filename = re.sub(
            r'[\\/*?:"<>|]', "", os.path.basename(picture_url))
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
                print(f"Picture downloaded successfully: {picture_filename}")
                return picture_filename
            else:
                picture_filename = "No picture found"
                print(
                    f"Failed to download picture from {picture_url}. Status code: {response.status_code}")
        except Exception as e:
            print(f"Error downloading picture: {e}")

        return None

    def download_picture(picture_url):
        # Prepare the local path for the picture
        # Using current working directory
        output_dir = os.path.join(os.getcwd(), "output", "images")
        os.makedirs(output_dir, exist_ok=True)  # Ensure the directory exists

        sanitized_filename = re.sub(
            r'[\\/*?:"<>|]', "", os.path.basename(picture_url))
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
                print(f"Picture downloaded successfully: {picture_filename}")

                # Store the picture as an asset in Control Room
                asset_name = sanitized_filename  # You can customize the asset name as needed
                Storage.set_file_asset(asset_name, picture_filename)
                print(f"Picture stored as asset: {asset_name}")

                return picture_filename
            else:
                print(
                    f"Failed to download picture from {picture_url}. Status code: {response.status_code}")
        except Exception as e:
            print(f"Error downloading picture: {e}")

        return None

    def picture_extraction(local, article):
        # Download picture if available and extract the filename
        try:
            e_img = article.query_selector(
                loc.article_image_xpath).as_element()
        except:
            picture_url = ''
            picture_filename = ''
        else:
            picture_url = e_img.get_attribute("src")
            if local:
                picture_filename = Utils.LOCAL_download_picture(picture_url)
            else:
                picture_filename = Utils.download_picture(picture_url)
        return picture_filename

    def LOCAL_save_to_excel(results):
        wb = openpyxl.Workbook()
        ws = wb.active

        headers = ["Title", "Date", "Description", "Picture Filename",
                   "Count of Search Phrases", "Monetary Amount"]
        ws.append(headers)

        # Write the data rows
        for result in results:
            # print(result)
            row = [
                result["title"],
                result["date"],
                result["description"],
                result["picture_filename"],
                result["count_search_phrases"],
                result["monetary_amount"]
            ]
            ws.append(row)
        wb.save('./output/results.xlsx')

    def save_to_excel(results):
        wb = openpyxl.Workbook()
        ws = wb.active

        headers = ["Title", "Date", "Description", "Picture Filename",
                   "Count of Search Phrases", "Monetary Amount"]
        ws.append(headers)

        # Write the data rows
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

        excel_path = './output/results.xlsx'
        wb.save(excel_path)
        print(f"Excel file saved: {excel_path}")

        # Store the Excel file as an asset in Control Room
        asset_name = "results.xlsx"  # You can customize the asset name as needed
        storage.set_file(asset_name, excel_path)
        print(f"Excel file stored as asset: {asset_name}")
