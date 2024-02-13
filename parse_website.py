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

# Set up the model
generation_config = {
  "temperature": 0.9,
  "top_p": 1,
  "top_k": 1,
  "max_output_tokens": 2048,
}

safety_settings = [
  {
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
]

model = genai.GenerativeModel(model_name="gemini-pro",
                              generation_config=generation_config,
                              )

prompt_parts = [
  "Summarize this news webpage into 2-6 sentences that includes all exact statistics, examples, and events in the article. Do not consider any advertisements or unrelated information on the webpage", text

]

response = model.generate_content(prompt_parts)
print(response.text)