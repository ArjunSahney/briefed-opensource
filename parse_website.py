import requests
from bs4 import BeautifulSoup
# Send an HTTP request to the URL of the webpage you want to access
response = requests.get("https://www.cnn.com/2024/02/12/us/joel-osteen-lakewood-church-shooting-monday/index.html")
# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(response.content, "html.parser")
# Extract the text content of the webpage
text = soup.get_text()
import os


import google.generativeai as genai
# export gemini_api_key=AIzaSyAWs96_gNcexe7b-jquHWi5pArESWI3PUA

genai.configure(api_key=os.environ.get("gemini_api_key"))

### POSSIBLE IMPROVEMENT: Making the scraper only get the article content and not bullshit
###
def gemini_parse_website(url): 
    # Send an HTTP request to the URL of the webpage you want to access
    response = requests.get(url)
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.content, "html.parser")
    # Extract the text content of the webpage
    text = soup.get_text()


    # Set up the model
    generation_config = {
    "temperature": 0.9,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 2048,
    }


    model = genai.GenerativeModel(model_name="gemini-pro",
                                generation_config=generation_config,
                                )

    prompt_parts = [
    "Summarize this news webpage into 6-8 sentences in-depth that includes all exact statistics, examples, and events in the article in the style of the writing. Do not consider any advertisements or unrelated information on the webpage and INCLUDE THE NAME OF SOURCE AT THE BOTTOM", text

    ]

    response = model.generate_content(prompt_parts)
    # print(response.text)