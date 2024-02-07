<<<<<<< HEAD
import openai
from openai import OpenAI
from newsapi import NewsApiClient
import requests
import datetime
import json
from colorama import Fore
import requests
from bs4 import BeautifulSoup
from dotenv import find_dotenv, load_dotenv
from googlesearch import search


# Initialize API keys
newsapi_key = '5f67759ab3e74c6089d70eb25b88c160'
openai_api_key = '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'
serpapi_key = '6bd8076584cc412e4de18cd156206095ceefc0b2e16c7f6a4de7f1af84879d9a'
searchapi_key = 'uLNHyAJp6zs7QxZ6kyfNdhBK'

# Set up NewsApiClient and OpenAI
newsapi = NewsApiClient(api_key=newsapi_key)
load_dotenv()
openai.api_key = openai_api_key

client = OpenAI(
    api_key='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'
)

def generate_google_search_query(user_input):
    """
    Uses GPT-4-turbo to convert user input into a Google Search query.
    """
    prompt = f"Convert the following user query into an optimized Google search query: '{user_input}'"

    try:
        completion = client.chat.completions.create(
            model="gpt-4-0125-preview",
            messages=[
                {"role": "system", "content": "You are a Google Search Expert. Your task is to convert user inputs to optimized Google search queries. Example: USER INPUT: 'Why was Sam Altman fired from OpenAI?' OPTIMIZED Google Search Query: 'Sam Altman Fired OpenAI'"},
                {"role": "user", "content": prompt}
            ]
        )
        # Accessing the response directly
        if completion.choices:
            response_message = completion.choices[0].message
            if hasattr(response_message, 'content'):
                return response_message.content.strip()
            else:
                return "No content in response."
        else:
            return "No response from GPT-4 Turbo."
    except Exception as e:
        print(f"Error in generating Google search query: {e}")
        return None

# Define the function to get news results
def get_organic_results(query, num_results=3, location="United States"):
    params = {
        "q": query,
        "tbm": "nws",
        "location": location,
        "num": str(num_results),
        "api_key": "______"
    }
    # modified search params for debugging
    scraped_results = {}
    urls = []
    for i in search(query, tld='co.in', lang='en', num=1, start=0, stop=None, pause=0):
        urls.append(i)
        # url, data = scrape_website(i)
        # scraped_results[url] = data
    
    # print(scraped_results)   

    # news_results = results.get("news_results", [])
    # urls = [result['link'] for result in news_results]
    return urls

# Define the function to scrape data from a URL and return the URL
def scrape_website(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        page_content = response.content
        soup = BeautifulSoup(page_content, 'html.parser')
        paragraphs = soup.find_all('p')
        scraped_data = [p.get_text() for p in paragraphs]
        formatted_data = "\n".join(scraped_data)
        return url, formatted_data  # Return both URL and content
    else:
        return url, "Failed to retrieve the webpage"

# Create an Assistant with a specific name
# client = openai()
# # client = openai.Client(api_key='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')
assistant = client.beta.assistants.create(
# assistant = openai.Assistant.create(
    name="GoogleGPT",
    description="A set of capabilities for fetching and displaying news articles based on user inputs to Google queries.",
    model="gpt-4-0125-preview",
    tools=[
        {
            "type": "function",
            "function": {
                "name": "get_organic_results",
                "description": "Fetch news URLs based on a search query",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "num_results": {"type": "integer", "description": "Number of results to return"},
                        "location": {"type": "string", "description": "Location for search context"},
                    },
                    "required": ["query"]
                },
            }
        },
        {
            "type": "function",
            "function": {
                "name": "scrape_website",
                "description": "Scrape the textual content from a given URL",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "URL to scrape"},
                    },
                    "required": ["url"]
                },
            }
        }
    ]
)

# Main loop to handle user queries
while True:
    user_query = input(Fore.CYAN + "Please enter your query (type 'exit' to quit): ")
    if user_query.lower() == "exit":
        break

    # Generate a Google Search query from the user input
    google_search_query = generate_google_search_query(user_query)
    print(f"Converted Google Search Query: {google_search_query}")

    if google_search_query:
        # Fetch news URLs based on the generated query
        news_urls = get_organic_results(google_search_query)

        # Scrape content from the first URL (for demonstration)
        if news_urls:
            url, news_content = scrape_website(news_urls[0])  # Get URL and content

            # Prepare grounding context
            grounding_context = f"Context: {news_content}\nUser Query: {user_query}"
            print(grounding_context)

            # Chat completion to handle grounding context
            completion = client.chat.completions.create(
                model="gpt-4-0125-preview",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant, always return only the essential parts that answer the USER original USER query, but add 3 bullet points to backup your reasoning for the answer."},
                    {"role": "user", "content": grounding_context}
                ]
            )

            # Process and display the response
            response = completion.choices[0].message.content if completion.choices else ""
            print(Fore.YELLOW + "Response GPT-4")
            print(Fore.YELLOW + response)
        else:
            print("No news articles found for your query.")
    else:
        print("Failed to generate a Google search query.")
=======
import os
import requests
from bs4 import BeautifulSoup
from langchain.agents import Tool, create_react_agent
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
from langchain.utilities import GoogleSearchAPIWrapper
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")

# Initialize OpenAI Client
client = OpenAI(api_key=OPENAI_API_KEY)

# Function to optimize search queries using GPT-4
def generate_google_search_query(user_input):
    prompt = f"Convert the following user query into an optimized Google search query: '{user_input}'"
    try:
        completion = client.chat.completions.create(
            model="gpt-4-0125-preview",
            messages=[
                {"role": "system", "content": "You are a Google Search Expert. Your task is to convert user inputs to optimized Google search queries."},
                {"role": "user", "content": prompt}
            ]
        )
        if completion.choices:
            response_message = completion.choices[0].message
            return response_message.content.strip()
        else:
            return "No response from GPT-4 Turbo."
    except Exception as e:
        print(f"Error in generating Google search query: {e}")
        return None

# Function to scrape website content
def scrape_website(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        text = ' '.join(soup.stripped_strings)
        return text
    else:
        return "Failed to retrieve the webpage"

search = GoogleSearchAPIWrapper()

# Enhanced Google Search Tool
class EnhancedGoogleSearchTool(Tool):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def run(self, input_text, **kwargs):
        optimized_query = generate_google_search_query(input_text)
        search_results = search.run(optimized_query)
        top_links = [result['link'] for result in search_results['items'][:5]]  # Top 5 links
        scraped_contents = [scrape_website(link) for link in top_links]
        return scraped_contents

tools = [
    EnhancedGoogleSearchTool(
        name="EnhancedSearch",
        func=search.run,
        description="Searches and scrapes top links from Google"
    ),
]

memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

llm = ChatOpenAI(api_key=OPENAI_API_KEY, temperature=0)

# Create an agent using the new method
agent_chain = create_react_agent(tools=tools, llm=llm, verbose=True, memory=memory)

# Terminal interaction
while True:
    input_text = input("Enter your query (or type 'exit' to quit): ")
    if input_text.lower() == 'exit':
        break
    response = agent_chain.run(input=input_text)
    print("Response:", response)
>>>>>>> 0f46a8ab (custom google news logic)
