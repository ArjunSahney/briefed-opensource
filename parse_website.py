import requests
from bs4 import BeautifulSoup

import os

def get_html(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    text = soup.get_text()
    return text


import google.generativeai as genai
genai.configure(api_key=os.environ.get("gemini_api_key"))
# export gemini_api_key=AIzaSyAWs96_gNcexe7b-jquHWi5pArESWI3PUA

def get_clean_contents(url):
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
    "Print out the contents of the article, removing anything extraneous: ", get_html(url)

    ]

    response = model.generate_content(prompt_parts)
    return response.text


print(get_html("https://www.cnn.com/2024/02/12/us/joel-osteen-lakewood-church-shooting-monday/index.html"))