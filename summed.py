"""Searches google news, retrieves top articles, summarizes articles into keywords.
Searches keywords through News API, gets contents of every article 
returned by News API, summarizes using GPT-4. Combined summaries into a combined
contents dictionary. Summarizes combined contents using GPT-4.

Written 2024-02-17

Instructions: 
  1.Export API Keys, see https://www.notion.so/API-Keys-66bf13bb561e42c08893108e2b0c8c02
    for API keys
"""
__author__ = "Ram Gorthi, DJun Sahney"
__version__ = "1.6"

import json
from openai import OpenAI
from api_toolbox import *
from spaCy_summarizer import *
import time # debugging latency

# How many articles summarized per brief
ARTICLES_PER_BRIEF = 2

def get_gpt_summary(url, gpt_model="gpt-3.5-turbo"):
  """Return short summary of article, using GPT-4

  Parameters
  ----------
  url : str
  gpt_model : str

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
                             most impactful facts and conclusions drawn in the article: {article_text}""", gpt_model=gpt_model)
  return summary

# TODO: Use keyword extraction API monkey learn, IBM Watson, Amazon Comprehend
def get_search_keywords(url="", method="title", article_title=""):
  """Gets 3-5 keywords based on the article text using GPT

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
  keywords = None
  if (method == "summary"):
    article_text = get_article_text(url)
    if article_text is None:
      return None
    keywords = get_gpt_response(f"Return a 3-5 word google search to retrieve more information about this topic: {article_text}", "gpt-4-turbo-preview")
  elif (method == "title"):
    if (article_title == ""):
      article_title = get_article_text(url, "title")
    keywords = get_gpt_response(f"""Optimize this article title into a 3-5 word search query: {article_title}""", 
                                "gpt-4-turbo-preview")
  if keywords is not None:
    import re
    keywords = re.sub(r'^\"|\"$', '', keywords)

  return keywords

def get_formatted_newsAPI_contents(keywords, google_news_results):
  """
  Get formatted contents of News API keyword search. Should return title, summary,
  source, and URL in a clean format for purposes of inputting it into a summarizer
  that will cite the correct sources. 

  V2: Integrate the google_news_results dictionary into the formatted news dictionary
  if able to scrape it!

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
  # TODO: Potentially change logic here such that we can utilize all the best articles:
  #       Cluster the articles on similar stories together somehow? 
  #       Use Synthesis' architecture but with a lighter-weight model? 
  # Reason this doesn't work is because it'll just append the google_news_results
  # dictionary to the top of related_articles every time, so it'll keep summarizing the
  # top 3 google news results... total L.
  if google_news_results is not None: 
    related_articles = google_news_results + related_articles

  articles_dict = {}
  articles_summarized = 0
  # Loop through the list of related articles, assigning each a unique number
  for article in related_articles:
    if (articles_summarized > ARTICLES_PER_BRIEF): # Hard limit number of articles summarized per briefed
      break

    url = article.get('url', 'None')
    if (url == 'None'):
      url = article.get('link')
    title = article.get('title', 'No Title Available')
    #summary = get_article_text(url)
    # Keep ratio low to ensure GPT-4 can handle the combined summary
    summary = get_spaCy_article_summary(url, ratio=0.05) 
    if (summary is None) or (title == "[Removed]"):
      continue 

    articles_summarized += 1
    publishedAt = article.get('publishedAt', None)
    if (publishedAt is None):
      publishedAt = article.get('date', 'No date available')
    date = publishedAt[:10]
    try:
      source = article.get('source', {}).get('name', 'Unknown Source')
    except AttributeError:
      source = article.get('source')
    # Add the extracted information to the articles_dict, keyed by the index
    articles_dict[articles_summarized] = {
      "title": title,
      "summary": summary,
      "source": source,
      "date": date,
      "url": url
    }

  return articles_dict
    
# TODO: Modify dictionary by removing source/url from copy you put into GPT
def generate_brief(article_dict):
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
    under a common topic! Summarizes using GPT-4. Will not function correctly with
    GPT-3.5-turbo.

    Parameters
    ----------
    articles_dict : dictionary

    Returns
    -------
    str
      Brief
  """
  from collections import deque
  summary_prompt = f"""Summarize the key points in this 'articles dictionary' into an 
  explainer. Cite the article number in parens when you
  use information from a specific article, for example: (Article 2, Article 3).
  Include a short title for the summary. Limit response to 100 words.
  {json.dumps(article_dict, indent=4)}"""
  summary = get_gpt_response(summary_prompt, gpt_model="gpt-4-turbo-preview")
  # Retrieve sources used in summary using regex
  import re
  # Step 1: Match the entire sequence within parentheses
  pattern = r"\((Article\s+\d+(?:,\s*Article\s+\d+)*)\)"
  # Find all matches in the text for the sequences
  sequences_matches = re.findall(pattern, summary)
  # Step 2: Extract individual article numbers from each matched sequence
  article_numbers = []
  for sequence in sequences_matches:
      nums = re.findall(r"Article\s+(\d+)", sequence)
      article_numbers.extend(nums)  # Add found numbers to the main list
  # Additionally, capture standalone article numbers in the format "(3)"
  standalone_nums = re.findall(r"\((\d+)\)", summary)
  article_numbers.extend(standalone_nums)
  # Convert matched article numbers from strings to integers
  article_numbers_int = [int(num) for num in article_numbers]

  seen_articles = set()
  sources = "\n"
  for article_num in article_numbers_int:
    if article_num in seen_articles:
      continue
    seen_articles.add(article_num)
    article_source = article_dict[article_num]["source"]
    article_url = article_dict[article_num]["url"]
    sources = sources + "\n" + str(article_num) + ". " + article_source + ", " + article_url

  return (summary + sources + "\n")

def in_brief(keyword, num_briefs):
  start_time = time.time()
  if (keyword.lower() == "top headlines"):
    news_results = get_google_results("", num_briefs)
  else:
    news_results = get_google_results(keyword, num_briefs)  
  end_time = time.time()
  duration = end_time - start_time
  print(f"Google News retrieval execution time: {duration} seconds")
  if news_results is None:
    print(f"No news on {keyword}")
    return
  brief = ""
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
    
    start_time = time.time()
    if title is not None:
      search_keywords = get_search_keywords(method="title", article_title=title)
    else:
      print("Error: In sum_by_keyword, unable to retrieve article title")
    end_time = time.time()
    duration = end_time - start_time
    print(f"Search words retrieval execution time: {duration} seconds")

    if search_keywords is not None:
      print(search_keywords) # for debugging
      start_time = time.time()
      # Try giving get_formatted_newsAPI_contents the news_results dict too!
      formatted_contents = get_formatted_newsAPI_contents(search_keywords, news_results)
      end_time = time.time()
      duration = end_time - start_time
      print(f"Get Formatted News API contents execution time: {duration} seconds")

      if (formatted_contents != {}):
        start_time = time.time()
        brief = brief + generate_brief(formatted_contents)
        #print(get_spaCy_article_dict_summary(formatted_contents))
        end_time = time.time()
        duration = end_time - start_time
        print(f"Generate brief execution time: {duration} seconds")
  return brief

print(in_brief("Morgan Stanley", 3))
# results = get_google_results("Biden", 5)
# results = results[:5]
# print(json.dumps(results, indent=4))

