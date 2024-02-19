"""Searches google news, retrieves top articles, summarizes articles into keywords.
Searches keywords through News API, generates combined contents of every article 
returned by News API using newspaper3K. Summarizes combined contents using GPT-4.

Written 2024-02-17

Instructions: 
  1.Export API Keys, see https://www.notion.so/API-Keys-66bf13bb561e42c08893108e2b0c8c02
    for API keys
"""
__author__ = "Ram Gorthi, DJun Sahney"
__version__ = "1.0"

from newspaper import Article
from newspaper.article import ArticleException
from serpapi import GoogleSearch
import os
import requests
from openai import OpenAI
from api_toolbox import *

def get_summary(url):
  """Return short summary of article, using GPT-4

  Parameters
  ----------
  url : str

  Returns
  -------
  str
    summary of article
  """
  article_text = get_article_text(url)
  if article_text is None:
    return None
  summary = get_gpt_response(f"Summarize the key points and essential information from the following article in a single paragraph of approximately 150 words. Focus on the most impactful facts and conclusions drawn in the article: {article_text}")
  return summary

def get_search_keywords(url, method="summary"):
  """Gets 3-6 keywords based on the article text using GPT
  TODO: Compare the keywords generated based on the article text vs article title, because
        retrieving the text takes some time but retrieving the title does not
        Down-side of using the article's text is that some articles with paywalls won't be
        used for keyword extraction.
        Up-side of using article text is the keywords are better and we avoid click-baity
        article titles
  
  Parameters
  ----------
  url : str
  method : str (optional)
    Generate keywords off of either summary or article title
    Default is "summary," can also use "title"

  Returns
  -------
  str
    3-6 keywords
  None if unable to get text of article
  """
  if (method == "summary"):
    article_text = get_article_text(url)
    if article_text is None:
      return None
    keywords = get_gpt_response(f"Return a 3-6 word google search to retrieve more information about this topic: {article_text}", "gpt-3.5-turbo")
  elif (method == "title"):
    article_title = get_article_text(url, "title")
    keywords = get_gpt_response(f"Optimize this article title into a 3-6 word google search query: {article_title}", "gpt-3.5-turbo")
  return keywords

def get_formatted_newsAPI_contents(keywords):
  """
  Get formatted contents of News API keyword search. Should return title, summary,
  source, and URL in a clean format for purposes of inputting it into a summarizer
  that will cite the correct sources. 

  Strategy 1: Create a Dictionary where a number hashes to (article title, summary, source, URL)
              Pass dictionary in to GPT and tell it to cite the article number. Then, we can
              hyperlink the URL to the number and include source at bottom as a footnote.

  Parameters
  ----------
  keywords : str

  Returns
  -------
  articles_dict : {
    1: {
        "title": "Title 1"
        "summary": "Summary 1"
        "source": "Source 1"
        "url": "https://example.com/article1"
    }   
    2: ...
    ...  
  }
  """

  # Strategy 1 (see docustring)
  related_articles = get_news_api_response(keywords)
  if (related_articles is None):
    print("Error: In get_formatted_NewsAPI_contents(), received no articles")
    return None
  
  articles_dict = {}

  # Loop through the list of related articles, assigning each a unique number
  for index, article in enumerate(related_articles, start=1):

    title = article.get('title', 'No Title Available')
    url = article.get('url', 'No URL Available')
    date = article.get('publishedAt', 'No date Available')

    # TODO: Build in a defensive check here for URL and within get_summary()
    summary = get_summary(url)
    source = article.get('source', {}).get('name', 'Unknown Source')

    # Add the extracted information to the articles_dict, keyed by the index
    articles_dict[index] = {
      "title": title,
      "summary": summary,
      "source": source,
      "date": date,
      "url": url
    }

  return articles_dict
    
def sum_by_keyword(keyword):
  news_results = get_google_results(keyword, 10)
  for article in news_results:
    url = article.get('link')
    if url is not None:
      keywords = get_search_keywords(url, "summary")
      if keywords is not None:
        formatted_contents = get_formatted_newsAPI_contents(keywords)
        print(formatted_contents)
        # prompt = f"Summarize the key points in this 'articles dictionary' into
        #           a 150-word explainer. Cite the article number in parens when you
        #           use information from a specific article. {formatted_contents}"
        # print(get_gpt_response(prompt))

sum_by_keyword("Trump")