"""Implements primary and secondary search:

Primary Search: 
  =Pipeline A= 
  Scrape news on given query (Q1) and store top NUM_TITLES hits in dictionary keyed by title.
  =Pipeline B=
  Generalize given query (Q1) into Q2 and scrape news on Q2. Append top NUM_TITLES*10 hits to dictionary created in Pipeline A. 
  =>Merge<=
  Create list of all titles in dictionary. Request top NUM_TITLES most relevant titles on Q1 from LLM. Retrieve objects keyed by title from dictionary and store in a new dictionary, 'most_relevant_articles'

Secondary Search:
  Create a new dictionary, 'sources_by_story.'
  For each title in 'most_relevant_titles': 
    Simplify title to keywords (Q3). 
    (Approach R) Append Q1 keywords to Q3 if not present.
    Scrape NUM_ARTICLES_PER_BRIEF on Q3. Format into a dictionary 'sources' keyed by title and mapped to a dictionary of key-value pairs containing source, link, thumbnail, etc.
    If sources does not contain title, append most_relevant_titles[title] to the sources dictionary.
    (Approach A) Parse list of top NUM_TITLES titles with LLM and return JSON of most relevant to Q1.
    Store sources in sources_by_story[title].

End result is a dictionary of NUM_TITLES title strings, each mapped to a dictionary of NUM_ARTICLES_PER_BRIEF title strings, each mapped to key-value pairs containing source, link, thumbnail, etc.

Next, feed this dictionary into a collating algorithm to read through each source on each title and generate a coherent brief on that story. This may require an additional LLM call.

Written 2024-04-18
"""

__author__ = "Ram Gorthi, DJun Sahney"
__version__ = "2"

import json
from openai import OpenAI
from api_toolbox import *
from spaCy_summarizer import *
import time # debugging latency

DEFAULT_NUM_TITLES = 10
DEFAULT_NUM_ARTICLES_PER_BRIEF = 5

# -------------------------------- PRIMARY SEARCH -------------------------------- #

def get_improved_title_using_snippet(title, snippet):
  optimize_title_prompt = f"""Given the following title and snippett from a news article, optimize the title for the article to be descriptive and explanatory. Remove any clickbait or buzz words. Return response in this form {{"title": title}}.
  
  title: {title}
  snippet: {snippet}
  """
  get_lepton_response(optimize_title_prompt, json_mode=True)
  
def get_general_keyword(keyword):
  """Use llama to generalize a specific news topic"""

def get_most_relevant_titles(titles, keyword):
  """Returns list of most relevant titles to a given keyword"""

def format_serp_results(results):
  """Formats Serp API results into dictionary keyed by title"""

def scrape_news(keyword, num_results):
  """Returns scraped results for a keyword
  
  Parameters
  ----------
  keyword: string
  num_results: integer
  
  Returns
  -------
  News results dictionary
  
  """
  # Scrape news on initial keyword
  if __debug__:
    print(f"Retrieving top titles on {keyword}")
    start_time = time.time()

  news_results = get_google_results_valueserp(keyword, num_results)
  
  if __debug__:
    end_time = time.time()
    duration = end_time - start_time
    print(f"ValueSerp retrieval time: {duration} seconds for {keyword}")

  if news_results is None:
    print(f"No news on {keyword}")
    return None
  else:
    return news_results


def primary_search(keyword, num_titles=DEFAULT_NUM_TITLES):
  """Retrieve most relevant titles to the keyword"""
  
  # First, scrape news on keyword and store in dictionary
  news_results = scrape_news(keyword, num_titles)
  article_dictionary = format_serp_results(news_results)
  
  # Next, scrape news on generalized keyword and add to dictionary
  general_keyword = get_general_keyword(keyword)
  news_results = scrape_news(general_keyword, num_titles)
  article_dictionary.update(format_serp_results(news_results))
  
  # Create a list of all titles in the dictionary
  title_list = []
  for title in article_dictionary:
    title_list.append(title)
  
  # Get the most relevant num_titles from the list
  
  
# -------------------------------------------------------------------------------- #


# -------------------------------- SECONDARY SEARCH ------------------------------ #

def append_missing_words(words_to_append, append_to_this_string):
    """Appends words from "words_to_append" to "append_to_this_string" if they are missing.
    
    Args:
    words_to_append (list): A list of words to potentially append.
    append_to_this_string (str): The string to which words will be appended.

    Returns:
    str: The updated string with missing words appended.
    """
    # Split the string into a set of words for faster membership checking
    existing_words = set(append_to_this_string.split())

    # Iterate through each word in the list to check if it's in the string
    for word in words_to_append:
        if word not in existing_words:
            # Append the word if it's missing, preceded by a space
            append_to_this_string += " " + word

    return append_to_this_string


def title_to_searchwords(title):
  """Get the optimal searchwords from a news title"""

def secondary_search(keyword,most_relevant_titles, a_or_b, original_results num_articles_per_brief=DEFAULT_NUM_ARTICLES_PER_BRIEF):
  # Initializing final dict and num articles per title 
  sources_by_story = {}
  num_articles = 10
  # If secondary a or b
  if a_or_b == "a":
    return secondary_a(sources_by_story,most_relevant_titles, keyword, num_articles)
  else: 
    return secondary_b(sources_by_story,most_relevant_titles, keyword, num_articles, original_results)
    
def secondary_a(sources_by_story,most_relevant_titles, keyword, num_articles):
  #Parse list of top NUM_TITLES titles with LLM and return JSON of most relevant to Q1.
  most_relevant_titles = get_most_relevant_titles(most_relevant_titles, keyword)
  for title in most_relevant_titles:
    simplified_title = title_to_searchwords(title)
    sources_by_story[title] = scrape_news(simplified_title, num_articles)
  return sources_by_story

def secondary_b(sources_by_story,most_relevant_titles, keyword, num_articles, original_results):
  for title in most_relevant_titles:
    simplified_title = title_to_searchwords(title)
    simplified_title = append_missing_words(keyword,simplified_title)
    sources_by_story[title] = scrape_news(simplified_title, num_articles)
    #If sources does not contain title, append most_relevant_titles[title] to the sources dictionary.
    #Loop through sources_by_story[title] and see if it contains title, if not add it 
    
  sources_by_story=(sources_by_story, title, original_results)

  return sources_by_story

def match_found(formatted_news_results, title, original_results):
  # Checking if any title matches the given title
  match_found = False
  for news_item in formatted_news_results:
    if news_item['title'] == title:
      match_found = True
      break

  if match_found == False:
    # If not, adding original article
    formatted_news_results[title] = original_results[title]

  return formatted_news_results
    

  """"""
# -------------------------------------------------------------------------------- #
# Secondary Search:
#   Create a new dictionary, 'sources_by_story.'
#   For each title in 'most_relevant_titles': 
#     Simplify title to keywords (Q3). 
#     (Approach R) Append Q1 keywords to Q3 if not present.
#     Scrape NUM_ARTICLES_PER_BRIEF on Q3. Format into a dictionary 'sources' keyed by title and mapped to a dictionary of key-value pairs containing source, link, thumbnail, etc.
#     If sources does not contain title, append most_relevant_titles[title] to the sources dictionary.
#     (Approach A) Parse list of top NUM_TITLES titles with LLM and return JSON of most relevant to Q1.
#     Store sources in sources_by_story[title].

# End result is a dictionary of NUM_TITLES title strings, each mapped to a dictionary of NUM_ARTICLES_PER_BRIEF title strings, each mapped to key-value pairs containing source, link, thumbnail, etc.

def search(topic):
  """Call primary search, secondary search"""
  