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
