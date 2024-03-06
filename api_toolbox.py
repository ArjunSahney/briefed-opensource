"""OpenAI API, News API, Newspaper3K library toolbox

Functions:
  Open AI API: 
    * def get_gpt_response(prompt)

  Serp API:
    * def get_google_results(query)

  Newspaper3K library:
    * def get_article_text(url)

  News API:
    * def get_news_api_response(keywords)

Written 2024-02-18

Export API Keys, see 
https://www.notion.so/API-Keys-66bf13bb561e42c08893108e2b0c8c02 for API keys
"""

import os
from openai import OpenAI
from newspaper import Article
from newspaper.article import ArticleException
import requests
import json
from serpapi import GoogleSearch

__author__ = "Ram Gorthi, DJun Sahney"
__version__ = "1.0"


def get_gpt_response(prompt, gpt_model="gpt-4"):
  """Encapsulates GPT prompting
  User provides prompt and gets only the text of GPT response

  Parameters
  ----------
  prompt : str
  model : str, optional (default is "gpt-4")
    Can also input "gpt-3.5-turbo"

  Returns
  -------
  str
    text response returned by chat completion agent
  None
    if no response received by GPT
  """

  client = OpenAI(
      api_key=os.environ.get("openai_api_key"),
  )
  response = client.chat.completions.create(
  messages=[
    {
      "role": "user",
      "content": prompt,
    }
  ],
  model=gpt_model,
  )
  if response.choices:
    response_text = response.choices[0].message.content
    return response_text
  else:
    return None

def get_top_stories(query, num_results):
  api_key=os.environ.get("serp_api_key")

  params = {
    "q": query,
    "hl": "en",
    "gl": "us",
    "api_key": api_key
  }

  search = GoogleSearch(params)
  results = search.get_dict()
  top_stories = results.get("top_stories")
  if top_stories is None:
    return None
  else:
    return top_stories[:num_results]
  
def get_google_results(query, num_results, engine="google_news", topic_token=None):
  """Returns dictionary of articles fetched from google news
  User provides query, gets 'news_results' JSON containing title, snippet, 
  link, and source.

  Parameters
  ----------
  query : str
    If query is empty, defaults to searching top headlines
  num_results : int
    Number of articles to return
  engine : str, optional (default is "google_news")
    Can also input "google" for google search engine
  topic_token : str, optional (default None)

  Returns
  -------
  Dictionary
    news_results dictionary containing title, link, source, snippet for each
    article
  """
  api_key=os.environ.get("serp_api_key")
  if (query == ""):
    if __debug__:
      print("Searching top headlines in get_google_results()")
    params = {
      "engine": engine,
      "api_key": api_key,
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    news_results = results.get("news_results", [])
    if not news_results:
        return None
    formatted_news_results = []
    if __debug__:
      print(json.dumps(news_results[:num_results], indent=4))
    # Handle the unique JSON we receive when searching top results
    for result in news_results[:num_results]:
      title = None
      if 'highlight' in result and 'title' in result['highlight']:
        title = result['highlight']['title']
      else:
        title = result['title']
      formatted_news_results.append({
          'title': title
      })
  else:
    params = {
      "api_key": api_key,
      "engine": "google",
      "q": query,
      "google_domain": "google.com",
      "gl": "us",
      "hl": "en",
      "tbm": "nws",
      "tbs": "qdr:d"
    }

    search = GoogleSearch(params)
    results = search.get_dict()
    news_results = results.get("news_results", [])
    if not news_results:
        return None

    # Select the top `num_results` news items
    top_news_results = news_results[:num_results]
    if __debug__:
      print(json.dumps(top_news_results, indent=4))
    # Optionally, format the results for cleaner output
    formatted_news_results = [{
          'title': result['title'],
          'link': result['link'],
          'source': result['source'],
          'date': result['date'],
          'snippet': result['snippet']
      } for result in top_news_results]

  return formatted_news_results
  

def get_article_text(url, part="body", errors="off"):
  """Returns requested part of article (body or title)
  Uses newspaper 3k python library to download article, parse, and retrieve
  text (without the bullshit on the page). Catches exceptions where download()
  fails (typically paywalls).

  Parameters
  ----------
  url : str
  part : str (optional, default is "body" which returns body of article)
    Supports "body" or "title"

  Returns
  -------
  str
    text or title of the article
  """
  article = Article(url)
  try:
    article.download()
    article.parse()
  except ArticleException as e:
    if (errors == "on"):
      print(f"Failed to download or parse article: {e}")
    return None 
  except Exception as e:
    return None 
  if (part == "body"):
    return article.text
  elif (part == "title"):
    return article.title

def get_news_api_response(query, get="articles", endpoint="/v2/everything"):
  """Gets JSON of News API response to query
  
  Parameters
  ----------
  query : str
    The search query string for the News API.
  get : str, optional
    The data from News API JSON to be retrieved, default is "articles"
    Can also do "all"
  endpoint : str, optional
    The API endpoint to query. Default is "/v2/everything". Other valid options include:
      * "/v2/top-headlines": For breaking news headlines for categories or countries.
      * "/v2/top-headlines/sources": For breaking news headlines from the most notable sources.
  
  Returns
  -------
  List of dictionaries
    Each dictionary represents an article from the News API response.
  """
  
  url_stem = "https://newsapi.org"
  url = url_stem + endpoint

  api_key = os.environ.get("news_api_key")
  params = {
    "q": query, 
    "apiKey": api_key
  }

  response = requests.get(url, params=params)
  if (response.json().get('status') != "ok"):
    print("Error: In get_news_api_response, failed to retreive News API response")
    print(response.json().get('message'))
    return None
  
  if (get == "all"):
    return response.json()
  if (get == "articles"):
    related_articles = response.json().get('articles', [])
    return related_articles
  else:
    print("Error: In get_news_api_response, invalid 'get'")
    return None