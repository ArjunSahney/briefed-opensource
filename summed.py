"""Searches google news, retrieves top articles, summarizes articles into keywords.
Searches keywords through News API, generates combined contents of every article 
returned by News API using newspaper3K. Summarizes combined contents using GPT-4.

Written 2024-02-17

Instructions: 
  1.Export API Keys, see https://www.notion.so/API-Keys-66bf13bb561e42c08893108e2b0c8c02
    for API keys
  2.Call sum_by_keyword(keyword)
"""
__author__ = "Ram Gorthi, DJun Sahney"
__version__ = "1.0"

from newspaper import Article
from newspaper.article import ArticleException
from serpapi import GoogleSearch
import os
from openai import OpenAI

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

def get_google_results(query, num_results, engine="google_news"):
  """Returns JSON of articles fetched from google news
  User provides query, gets 'news_results' JSON containing title, snippet, 
  link, and source.

  Parameters
  ----------
  query : str
  num_results : int
    Number of articles to return
  engine : str, optional (default is "google_news")
    Can also input "google" for google search engine

  Returns
  -------
  JSON
    news_results dictionary containing title, link, source, snippet for each
    article
  """
  api_key=os.environ.get("serp_api_key")
  params = {
    "engine": engine,
    "q": query,
    "api_key": api_key,
  }
  search = GoogleSearch(params)
  results = search.get_dict()
  news_results = results["news_results"]
  return news_results[:num_results]

def get_text(url):
  """Returns text of article
  Uses newspaper 3k python library to download article, parse, and retrieve
  text (without the bullshit on the page). Catches exceptions where download()
  fails (typically paywalls).

  Parameters
  ----------
  url : str

  Returns
  -------
  str
    text of the article
  """
  article = Article(url)
  try:
    article.download()
    article.parse()
  except ArticleException as e:
    print(f"Failed to download or parse article: {e}")
    return None 
  except Exception as e:
    return None 
  return article.text

def get_search_keywords(url):
  """Gets 3-6 keywords based on the article text
  TODO: Compare the keywords generated based on the article text vs article title, because
        retrieving the text takes some time but retrieving the title does not
        Down-side of using the article's text is that some articles with paywalls won't be
        used for keyword extraction.
        Up-side of using article text is the keywords are better and we avoid click-baity
        article titles
  
  Parameters
  ----------
  url : str

  Returns
  -------
  str
    3-6 keywords
  None if unable to get text of article
  """
  article_text = get_text(url)
  if article_text is None:
    return None
  keywords = get_gpt_response(f"Return a 3-6 word google search to retrieve more information about this article: {article_text}", "gpt-3.5-turbo")
  return keywords

def get_combined_newsAPI_contents(keywords):
  """
  TODO: Don't forget to include the SOURCES somehow
        Will need to think some more about this algo and how to include only the sources
        we actually use for the final summary. 
  """
  # TODO: bring in stuff from serp_custom 


def sum_by_keyword(keyword):
  news_results = get_google_results(keyword, 10)
  for article in news_results:
    url = article.get('link')
    if url is not None:
      keywords = get_search_keywords(url)
      if keywords is not None:
        prompt = f"Summarize: {get_combined_newsAPI_contents(keywords)}"
        print(get_gpt_response(prompt))

sum_by_keyword("Trump")