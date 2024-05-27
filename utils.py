import re
from datetime import datetime

def clean_string(input_string):
    # Convert to lowercase
    cleaned_string = input_string.lower()
    # Remove non-alphanumeric characters and spaces
    cleaned_string = re.sub(r'[^a-z0-9]', '', cleaned_string)
    return cleaned_string

def convert_birthday(date_str):
    input_format = "%b %d"
    output_format = "%m-%d"
    
    date_obj = datetime.strptime(date_str, input_format)

    converted_date = date_obj.strftime(output_format)
    
    return converted_date

