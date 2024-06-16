import requests
from bs4 import BeautifulSoup

def extract_data(url, tag, class_name):
    # Send a GET request to the URL
    response = requests.get(url)

    # Parse the HTML content
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all elements with the specified tag and class
    elements = soup.find_all(tag, class_=class_name)

    # Extract text from each element
    data = [element.get_text() for element in elements]

    return data