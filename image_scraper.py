import requests
from bs4 import BeautifulSoup
import os

def download_main_image(url):
    """
    Downloads the main image from the specified article URL.

    This function attempts to locate the main image of an article by employing different approaches.
    It searches for the main image using the following methods in order:
    1. Looking for the <meta> tag with property="og:image".
    2. Finding an <img> tag with a specific class or attribute indicating the main image.
    3. Searching for an <img> tag within a specific container (e.g., <figure>, <div>) for the main image.

    If a main image is found, it downloads the image and saves it in the "img" folder with the original filename.
    If no main image is found, it prints a message indicating that no main image was found.

    Args:
        url (str): The URL of the article from which to download the main image.

    Returns:
        None
    """
    # Send a GET request to the URL
    response = requests.get(url)

    # Create a BeautifulSoup object to parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')

    # Approach 1: Find the <meta> tag with property="og:image"
    og_image = soup.find('meta', property='og:image')
    if og_image:
        img_url = og_image['content']
        img_tag = soup.new_tag('img', src=img_url)
    else:
        img_tag = None

    # Approach 2: Find an <img> tag with a specific class or attribute indicating the main image
    if not img_tag:
        img_tag = soup.find('img', class_=lambda x: x and 'main-image' in x)

    # Approach 3: Find an <img> tag within a specific container (e.g., <figure>, <div>) for the main image
    if not img_tag:
        main_image_container = soup.find(['figure', 'div'], class_=lambda x: x and 'main-image' in x)
        if main_image_container:
            img_tag = main_image_container.find('img')

    if img_tag:
        # Extract the source URL of the image
        img_url = img_tag['src']

        # Check if the image URL is absolute or relative
        if not img_url.startswith('http'):
            # Create an absolute URL by joining the base URL and the relative image URL
            img_url = url.rsplit('/', 1)[0] + '/' + img_url

        # Extract the filename from the image URL
        filename = os.path.basename(img_url)

        # Create the "img" folder if it doesn't exist
        if not os.path.exists('img'):
            os.makedirs('img')

        # Send a GET request to download the image
        img_response = requests.get(img_url)

        # Save the image to a file in the "img" folder with the extracted filename
        with open(os.path.join('img', filename), 'wb') as file:
            file.write(img_response.content)

        print(f"Main image downloaded successfully as {filename} in the img folder.")
    else:
        print("No main image found in the article.")

# Prompt the user to enter the article URL
url = input("Enter the article URL: ")

# Download the main image
download_main_image(url)