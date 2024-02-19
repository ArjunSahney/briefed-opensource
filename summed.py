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
import json
from openai import OpenAI
from api_toolbox import *

# How many articles summarized per brief
ARTICLES_PER_BRIEF = 3

def get_summary(url):
  """Return short summary of article, using GPT-4

  Parameters
  ----------
  url : str

  Returns
  -------
  str
    summary of article
  None
    if errors
  """
  article_text = get_article_text(url)
  if article_text is None:
    return None
  summary = get_gpt_response(f"""Summarize the key points and essential information from the following 
                             article in a single paragraph of approximately 150 words. Focus on the 
                             most impactful facts and conclusions drawn in the article. If there is 
                             any issue, simply return 'No': {article_text}""")
  return summary

def get_search_keywords(url="", method="summary", article_title=""):
  """Gets 3-5 keywords based on the article text using GPT
  TODO: Compare the keywords generated based on the article text vs article title, because
        retrieving the text takes some time but retrieving the title does not
        Down-side of using the article's text is that some articles with paywalls won't be
        used for keyword extraction.
        Up-side of using article text is the keywords are better and we avoid click-baity
        article titles
  
  Parameters
  ----------
  url : str (optional)
  method : str (optional)
    Generate keywords off of either summary or article title
    Default is "summary," can also use "title"
  title : str (optional)
    If the user does not need us to retrieve the title for them, they can input it here

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
    keywords = get_gpt_response(f"Return a 3-5 word google search to retrieve more information about this topic: {article_text}", "gpt-3.5-turbo")
  elif (method == "title"):
    if (article_title == ""):
      article_title = get_article_text(url, "title")
    keywords = get_gpt_response(f"""Optimize this article title into a 3-5 word google search query 
                                to retrieve more information on this topic: {article_title}""", 
                                "gpt-3.5-turbo")
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
  articles_summarized = 1
  # Loop through the list of related articles, assigning each a unique number
  for article in related_articles:
    if (articles_summarized > ARTICLES_PER_BRIEF): # Hard limit number of articles summarized per briefed
      break

    url = article.get('url', 'No URL Available')
    title = article.get('title', 'No Title Available')
    summary = get_summary(url)
    if (summary is None) or (title == "[Removed]"):
      continue 

    articles_summarized += 1
    publishedAt = article.get('publishedAt', 'No date Available')
    date = publishedAt[:10]
    source = article.get('source', {}).get('name', 'Unknown Source')
    # Add the extracted information to the articles_dict, keyed by the index
    articles_dict[articles_summarized] = {
      "title": title,
      "summary": summary,
      "source": source,
      "date": date,
      "url": url
    }

  return articles_dict
    
def generate_brief(title, article_dict):
  """Receives article dictionary of form:
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
    And returns a brief. Can be called whenever you have multiple URLs & sources
    under a common topic!

    Parameters
    ----------
    title : str
      Title of the brief
    articles_dict : dictionary

    Returns
    -------
    str
      Brief
  """
  summary_prompt = f"""Summarize the key points in this 'articles dictionary' into a 
  150-word explainer. Cite the article number in parens when you
  use information from a specific article. {json.dumps(article_dict, indent=4)}"""
  summary = get_gpt_response(summary_prompt)
  title_prompt = f"Generate a short, informative title for this news summary: {summary}"
  return (get_gpt_response(title_prompt) +"\n" + summary)

def in_brief(keyword, num_briefs):
  news_results = get_google_results(keyword, num_briefs)  
  for article in news_results:
    # Some of these article objects are actually not individual articles but
    # groups of articles that are located in "stories", which contains a link within it
    title = None
    if article.get('stories'):
      stories = article['stories']
      first_story = stories[0]
      title = first_story['title']
    else: # It is an individual article and not a 'story'
      title = article.get('title')
    
    if title is not None:
      search_keywords = get_search_keywords(method="title", article_title=title)
    else:
      print("Error: In sum_by_keyword, unable to retrieve article title")

    if search_keywords is not None:
      formatted_contents = get_formatted_newsAPI_contents(search_keywords)
      if (formatted_contents != {}):
        print(generate_brief(get_search_keywords, formatted_contents))

in_brief("Biden", 2)