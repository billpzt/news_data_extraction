import os
import re
import requests
import openpyxl
from robocorp import storage
from Locators import Locators as loc

class FileUtils:
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