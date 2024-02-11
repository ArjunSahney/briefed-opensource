from serpapi import GoogleSearch
import json
import requests
import os
from openai import OpenAI


# Initialize API keys
newsapi_key = '5f67759ab3e74c6089d70eb25b88c160'
# openai_api_key = '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'
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

def search_topic(query):
    if query: 
        params = {
            "engine": "google_news",

            "q": query,
            "api_key": "6bd8076584cc412e4de18cd156206095ceefc0b2e16c7f6a4de7f1af84879d9a",
            "num": 13  # Only retrieve 5 results
        }
    else: 
        params = {
            "engine": "google_news",
            "api_key": "6bd8076584cc412e4de18cd156206095ceefc0b2e16c7f6a4de7f1af84879d9a",
            "num": 13  # Only retrieve 5 results
        }

    search = GoogleSearch(params)
    results = search.get_dict()
    print("Fetched results from google news")
    news_results = results.get("news_results", [])

    # Loop through the first 5 results and print their titles
    for i in range(min(len(news_results), 15)):
        article = news_results[i]

    return news_results  # You can still return the results for further processing


def summarize_search_newsapi(query):
    news_results = search_topic(query)
    custom_dict = dict(query=dict())
    for article in news_results:
        
        title = article['title']
        # Same titles from above made here 
        
        summary = summarize_headline_5_words(title)
        # print("2nd Summary:" + summary)
        
        # Search for related articles
        url = "https://newsapi.org/v2/everything"
        params = {"q": summary, "apiKey": newsapi_key}
        response = requests.get(url, params=params)
        related_articles = response.json().get('articles', [])
        
        if related_articles:
            contents = [a['content'] for a in related_articles[:100] if a.get('content')]
            combined_contents = ' '.join(contents)
            if combined_contents:
                topic_prompt = f"You are a world class, objective journalist who only uses sources that exist. Summarize the following into a factual 75-word summary using multiple sources:\n\n{combined_contents}"
                perspective_prompt = "You are a fantastic journalist, who cites multiple, sources that exist and provides true information. Identify and summarize the two major perspectives with specifics in 50 words each using existing sources based on the following content:\n\n" + combined_contents
                
                # Summarize topic
                topic_summary_response = client.chat.completions.create(
                    messages=[
                        {
                            "role": "user",
                            "content": topic_prompt,
                        }
                    ],
                    model="gpt-4",
                )
                if topic_summary_response.choices:
                    topic_summary = topic_summary_response.choices[0].message.content
                else:
                    print("No response received for topic prompt")

                # Summarize perspectives
                perspective_summary_response = client.chat.completions.create(
                    messages = [
                        {
                            "role": "user",
                            "content": perspective_prompt,
                        }
                    ],
                    model="gpt-4",
                )
                if perspective_summary_response.choices:
                    perspective_summary = perspective_summary_response.choices[0].message.content
                else:
                    print("No response received for perspective prompt")

                custom_dict[query] = {
                    'summary': summary,
                    'topic_summary': topic_summary,
                    'perspective_summary': perspective_summary
                }

                print(topic_summary)
                print(perspective_summary)

    
def summarize_headline_5_words(article):
    """Summarizes the article headline into 5 words."""
    headline_summary_response = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"Please summarize this headline into 5 words: \"{article}\"",
            }
        ],
        model="gpt-3.5-turbo",
    )

    if headline_summary_response.choices:
        headline_summary = headline_summary_response.choices[0].message.content
    else:
        print("No summary received for headline prompt")

    return headline_summary


def morning_briefing(industry, subindustry, company): 
    top_headlines = summarize_search_newsapi()
    overall_industry = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"If this is technology related return this topic token -- CAAqJggKIiBDQkFTRWdvSUwyMHZNRGRqTVhZU0FtVnVHZ0pWVXlnQVAB. If this is business related return this topic token -- CAAqJQgKIh9DQkFTRVFvTEwyY3ZNVEl4YW01eE1XMFNBbVZ1S0FBUAE. \"{industry}\"",
            }
        ],
        model="gpt-3.5-turbo",
    )
    
    


