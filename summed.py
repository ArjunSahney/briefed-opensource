
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
from datetime import datetime
from image_scraper import download_main_image
from topic_tokens import *

# How many articles summarized per brief
ARTICLES_PER_BRIEF = 5

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
  summary = get_gpt_response(f"""Summarize the key points and essential information from the following article in a single paragraph of approximately 150 words. Focus on the most impactful facts and conclusions drawn in the article: {article_text}""", gpt_model=gpt_model)
  
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
    keywords = get_gpt_response(f"""Optimize/summarize this article title into a 3-5 word search query: {article_title}""", 
                                "gpt-4-turbo-preview")
  if keywords is not None:
    import re
    keywords = re.sub(r'^\"|\"$', '', keywords)

  return keywords

def get_formatted_googleNews_contents(keywords):
    """
    Fetches and formats news articles from Google News based on given keywords. 
    The function aims to return a dictionary where each key is a unique identifier 
    mapping to information about each article, including its title, summary, source, 
    publication date, and URL. This structured format is suitable for input into a 
    summarizer that requires detailed source citation.

    Parameters
    ----------
    keywords : str
        The search keywords to find relevant news articles on Google News.

    Returns
    -------
    articles_dict : dict
        A dictionary where each key maps to another dictionary containing details 
        of a news article (title, summary, source, date, and URL).
    """
    # Initialize an empty dictionary to hold formatted article details.
    articles_dict = {}
    
    # Fetch search results from Google News using predefined parameters.
    # The number of results fetched is limited to 5.
    formatted_results = get_google_results_valueserp(keywords, ARTICLES_PER_BRIEF, engine="google_news", topic_token=None)
    if formatted_results is None:
      return None
    # Keep track of the number of articles summarized.
    articles_summarized = 0 
    
    # Iterate over each article in the fetched results.
    for article in formatted_results:
        if __debug__:
          print("Individual article JSON in formatted dictionary")
          print(json.dumps(article, indent=4))
        # Extract the title and URL of the article.
        title = article.get("title")
        link = article.get("link")
        if (link == 'None'):
          continue

        # Generate a summary for the article using a summarization function (spaCy)
        summary = get_spaCy_article_summary(link, ratio=0.05, max_words=None)
        
        # Attempt to extract the publication date. Doesn't convert '5 hours ago' to today's date.
        date = article.get('date', None)
        
        # Try to extract the source name.
        source = article.get('source')

        # Skip the article if not enough information is present.
        if (title is None or link is None or source is None or summary is None):
            continue
        
        # Increment the counter for summarized articles.
        articles_summarized += 1
        
        # Add the article details to the dictionary, using the summary count as a key.
        articles_dict[source] = {
            "title": title,
            "summary": summary,
            "source": source,
            "date": date,
            "url": link
        }

    # Return the dictionary containing formatted article details.
    return articles_dict

def get_formatted_newsAPI_contents(keywords, google_news_results):
  """
  Get formatted contents of News API keyword search. Should return title, summary,
  source, and URL in a clean format for purposes of inputting it into a summarizer
  that will cite the correct sources. 

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
  articles_summarized = 0
  # Loop through the list of related articles, assigning each a unique number
  for article in related_articles:
    if (articles_summarized > ARTICLES_PER_BRIEF): # Hard limit number of articles summarized per briefed
      break

    url = article.get('url', 'None')
    if (url == 'None'):
      url = article.get('link')
    title = article.get('title', 'No Title Available')

    # Keep ratio low to ensure GPT-4 can handle the combined summary
    summary = get_spaCy_article_summary(url, ratio=0.05) 
    # Defensive checks
    if (summary is None) or (title == "[Removed]"):
      continue 

    articles_summarized += 1
    publishedAt = article.get('publishedAt', None)
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
    
# TODO: Modify dictionary by removing source/url from copy you put into GPT
def generate_brief(article_dict, keyword):
  """Receives article dictionary of form:
    (v2)
    articles_dict : {
      source: {
          "title": "Title 1"
          "summary": "Summary 1"
          "source": "Source 1"
          "url": "https://example.com/article1"
      }
      source: ... 
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
    JSON
      Brief, containing title, summary, sources as separate key-value pairs
  """
  # Get summary with GPT-4
  #   Ignore any articles not pertaining to the keyword '{keyword}'. 

  summary_prompt = f"""Summarize the key points in this JSON of articles into an explainer. Cite the article source in parens at the end of each sentence when you use information from a specific article, for example: (Source 1, Source 2). Limit response to 100 words. 
  If there are no relevant articles, return None for title and summary. 
  Explain key concepts and details. Use clear, precise language. Prioritize substance.
  Return response in a JSON of this format: {{ "Title": title, "Summary": summary }}.
  {json.dumps(article_dict, indent=4)}"""
  if __debug__:
    print("Article dictionary: ")
    print(json.dumps(article_dict, indent=4))
  summary_string = get_gpt_response(summary_prompt, gpt_model="gpt-4-turbo-preview", response_format="json")
  print(summary_string)
  summary_json = json.loads(summary_string)

  
  # Future improvement: change regex to better handle double/triple+ citations in parens
  # Retrieve sources in parens in summary using regex
  import re
  pattern = r'\((.*?)\)'
  sources = re.findall(pattern, summary_string)

  if sources:
    extracted_sources = [source_list.split(', ') for source_list in sources]
    flattened_sources = [source for sublist in extracted_sources for source in sublist]
    print(flattened_sources)
  
    confirmed_sources = []
    for source in flattened_sources:
      if source in article_dict:
        confirmed_sources.append(source)
  
    # Prevent double citations and add to a sources string
    seen_articles = set()
    # Store sources in a list of 3-item lists (source name, date, URL)
    sources_list = []
    sources = "\n"
    # Keep count of articles for citation section
    article_num = 0
    for article_source in confirmed_sources:
      article_num += 1
      if article_source in seen_articles:
        continue
      seen_articles.add(article_source)
      article_url = article_dict[article_source]["url"]
      article_date = article_dict[article_source]["date"]
      sources_list_item = [article_source, article_url, article_date]
      sources_list.append(sources_list_item)
      summary_json['sources'] = sources_list
  else:
    summary_json['sources'] = []
  return (summary_json)

def get_trending_topics(num_results):
  """Returns list of `num_results` top trending story titles.
  Returned titles can be plugged directly into in_brief()
  
  Parameters
  ----------
  num_results : int
  
  Returns
  -------
  list of strings
  """
  api_key=os.environ.get("serp_api_key")
  params = {
    "engine": "google_trends_trending_now",
    "frequency": "daily",
    "api_key": api_key
  }

  search = GoogleSearch(params)
  results = search.get_dict()
  daily_searches = results["daily_searches"]
  searches_list = daily_searches[0]["searches"]
  trending_titles = []
  num_titles = 0
  for search in searches_list:
    articles = search.get("articles", None)
    if articles is None:
      continue
    
    title = articles[0].get("title", None)
    if title is None:
      continue
    
    keywords = get_search_keywords(article_title=title)
    trending_titles.append(keywords)
    
    num_titles += 1
    if num_titles >= num_results:
      break
  # Return list of `num_results` top titles
  return trending_titles


def in_brief(keyword, num_briefs):
  """Returns num_briefs briefs on a keyword
  
  Parameters
  ----------
  keyword : str
  num_briefs : int
  
  Returns
  -------
  str
    Consolidated list of briefs on keyword
  """
  # If brief file already exists, do not create a new one and return contents of current file
  curr_date = datetime.now().strftime('%Y-%m-%d')
  brief_filename = "brief_files/" + keyword + "_" + curr_date + ".txt"
  if os.path.exists(brief_filename):
    with open(brief_filename, 'r') as file:
      content = file.read()
    return content
  if __debug__:
    start_time = time.time()
  if (keyword.lower() == "headlines"):
    if __debug__:
      print("searching top headlines")
    news_results = get_google_results("", num_briefs)

  elif (topics[keyword]!=None) :
    get_google_results("query", num_briefs, engine="google_news", topic_token=topics[keyword])
  else:
    news_results = get_google_results_valueserp(keyword, num_briefs)  
  if __debug__:
    end_time = time.time()
    duration = end_time - start_time
    print(f"Google News retrieval execution time: {duration} seconds")
  if news_results is None:
    print(f"No news on {keyword}")
    return
  brief_json_list = []
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
      # Title working w/ Arjun new approach
      
    if __debug__:
      start_time = time.time()
    if title is not None:
      search_keywords = get_search_keywords(method="title", article_title=title)
      
    else:
      print("Error: Unable to retrieve article title")
    if __debug__:
      end_time = time.time()
      duration = end_time - start_time
      print(f"Search words retrieval execution time: {duration} seconds")

    if search_keywords is not None:
      if __debug__:
        print(search_keywords) 
        start_time = time.time()
      # formatted_contents = get_formatted_newsAPI_contents(search_keywords, news_results)
      formatted_contents = get_formatted_googleNews_contents(search_keywords)
      # TODO: add a check here that broadens the search keywords if there were very few results returned
      if __debug__:
        end_time = time.time()
        duration = end_time - start_time
        # print(f"Get Formatted News API contents execution time: {duration} seconds")
        print(f"Get Formatted Google News API contents execution time: {duration} seconds")

      if (formatted_contents is not None and formatted_contents != {}):
        if __debug__:
          start_time = time.time()
        image_downloaded = False
        # Image generation
        # For each brief, pull one image from a source -- if there is an error move on to next source
        # Save the image as the same filename as brief just img
        img_filename = search_keywords + "_" + curr_date
        for article in formatted_contents.items():
          url = article[1]['url']
          if __debug__:
            print("Printing article JSON for image generation")
            print(json.dumps(article, indent=4))
            print(url)
          # Download the main image from the article URL if not already downloaded and if url is valid
          if not image_downloaded and url is not None:
            image_url = download_main_image(url, img_filename)
            if image_url:
              image_downloaded = True
        brief = generate_brief(formatted_contents, search_keywords)
        # Add image filepath into brief JSON
        if image_downloaded:
          brief["Image Filepath"] = image_url
        brief_json_list.append(brief)

        if __debug__:
          end_time = time.time()
          duration = end_time - start_time
          print(f"Generate brief execution time: {duration} seconds")
          
                
  with open(brief_filename, 'w') as file:
    # First write operation
    brief_string = json.dumps(brief_json_list, indent=4)

    file.write(brief_string)
  return brief_string


# print(in_brief("US Presidential Election", 3))
# results = get_google_results("Biden", 5)
# results = results[:5]
# print(json.dumps(results, indent=4))
# print(get_trending_topics(5))
in_brief("US Politics", 4)