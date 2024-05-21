import re

def clean_string(input_string):
    # Convert to lowercase
    cleaned_string = input_string.lower()
    # Remove non-alphanumeric characters and spaces
    cleaned_string = re.sub(r'[^a-z0-9]', '', cleaned_string)
    return cleaned_string