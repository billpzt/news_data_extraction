from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class DateUtils:
    
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
