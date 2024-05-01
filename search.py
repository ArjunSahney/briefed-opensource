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
  """
  Using title and snippet from news article object, returns an improved title as a string. 
  
  Caller must pass in the title and snippet strings from the news article object from the news_results JSON. Uses Mistral7B to optimize the title. Uses regex to extract JSON from LLM response (Mistral's JSON-mode is not as clean as GPT-4's)
  
  Parameters
  ----------
  title: str
  snippet: str
  
  Returns
  -------
  str
  """
  
  optimize_title_prompt = f"""Given the following title and snippett from a news article, optimize the title for the article to be descriptive and explanatory. Remove any clickbait or buzz words. Return response in this form {{"title": title}}.
  
  title: {title}
  snippet: {snippet}
  """
  if __debug__:
    start_time = time.time()
    
  improved_title_response = get_lepton_response(optimize_title_prompt, json_mode=True)
  
  # Use regular expression to find the JSON object in the respone string
  title_json = get_json_from_lepton(improved_title_response)
  if title_json is None:
    print("No JSON found in the text")
  else:
    title = title_json["title"]
    print("Optimized title: ", title)
  
  if __debug__:
    end_time = time.time()
    duration = end_time - start_time
    print(f"Optimize title: {duration} seconds")

  return title

def generalize_topic(topic):
  """Use LLMs (gpt-4) to generalize a specific news topic.
  Other LLMs don't work well (e.g. Mistral)
  
  """
  
  generalize_prompt = f"""Given the following topic, broaden the topic by simplifying.
  Examples:
  2024 US Presidential Election -> US Election
  Bitcoin Pricing -> Cryptocurrency
  Enterprise AI Launches -> AI

  Now simplify the following topic: {topic}
  """
  response = get_gpt_response(generalize_prompt, gpt_model="gpt-3.5-turbo")
  # if __debug__:
  print("Generalized topic: " + response)
  return response

def parse_ranked_list(string_ranked_list, range):
  """Takes a string of a ranked list and returns a list of strings"""
  list_items = []
  lines = string_ranked_list.split('\n')
  # Loop through each line
  for line in lines:
      # Check if the line starts with a number followed by a dot (indicating an article title)
      if line.strip().startswith(tuple(f"{i}." for i in range(1, len(range)))):
          # Split the line at the first dot followed by a space to isolate the title
          item = line.split('. ', 1)[1]
          # Append the isolated item (string) to the list
          list_items.append(item)
  return list_items

def get_most_relevant_titles(news_results, keyword, num_results=DEFAULT_NUM_TITLES):
  """Returns list of most relevant titles to a given keyword
  
  Parameters
  ----------
  news_results: JSON
    Caller should simply pass in the news results JSON
  keyword: str
  num_results: int
    Limit relevancy determination to only the top num_results titles
  
  Returns
  -------
  JSON
    Same format as the news results JSON
  """
  if __debug__:
    start_time = time.time()
  if news_results[0].get("title") is None:
    print("News results JSON is empty")
    return None
  titles = []
  titles_string = ""
  for article_object in news_results:
    titles.append(article_object["title"])
    titles_string += article_object["title"] + "\n"
  
  # TODO: Add functionality to optimize title before passing to LLM?
  # Will add ~2s of latency for each title
  
  range = min(num_results*2, len(titles))
  # If we only have num_results titles, just return them, no need to rank
  if (range <= num_results):
    return titles
  else:
    range_string = str(range)
  relevancyPrompt = f"""Determine which {range_string} of these article titles are most relevant to an individual interested in {keyword}. Return response as a JSON in this format:
{{
  "1": title 1,
  "2": title 2,
  ...
  "{range_string}": title {range_string}
}}

{titles_string}
  """
  if __debug__:
    print(relevancyPrompt)
  response = get_lepton_response(relevancyPrompt, model="Wizardlm-2-8x22b", json_mode=True)
  response_json = get_json_from_lepton(response, triple_ticks=True)
  if __debug__:
    print("Relevancy response: " + response)
    print("Relevancy response JSON: " + json.dumps(response_json, indent=4))
  if response_json is None:
    return news_results
  
  # Populate relevant_news_results with the titles in response_json in order
  relevant_news_results = []
  for rank, title in response_json.items():
    relevant_news_results.append(title)
  # Replace each title in relevant_news_titles with its corresponding article object
  # This preserves the ranking of each article from the relevancy determination
  for article_object in news_results:
    if article_object["title"] in relevant_news_results:
      # Don't need to catch a ValueError here because we know the title is in the list
      index = relevant_news_results.index(article_object["title"])
      # Replace the title in the list with the article object
      relevant_news_results[index] = article_object
  
  if __debug__:
    print("Most relevant news results: ")
    print(json.dumps(relevant_news_results, indent=4))
  
  if __debug__:
    end_time = time.time()
    duration = end_time - start_time
    print(f"Relevancy determination: {duration} seconds")

  return relevant_news_results
  
def scrape_news(keyword, num_results):
  """Returns scraped results for a keyword
  
  Parameters
  ----------
  keyword: string
  num_results: integer
  
  Returns
  -------
  News results dictionary
  None if no news from serp
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
  """Retrieve a JSON of news articles in order of relevancy to a given keyword"""
  
  # First, scrape news on keyword and store in news_results
  # The user wants the top num_titles results, so grab the top num_titles*5 so we can cut down
  scope = 5
  news_results = scrape_news(keyword, num_titles*scope)
  
  # Next, scrape news on generalized keyword and add to dictionary
  general_keyword = generalize_topic(keyword)
  generalization_factor = 10
  # Add the generalized results to news results
  general_results = scrape_news(general_keyword, num_titles*scope*generalization_factor)
  if general_results:
    news_results.extend(general_results)
  
  # Sort the list by relevancy
  # For now, we will keep all the news results because in secondary search, we may find some articles unparseable
  relevant_news_results = get_most_relevant_titles(news_results, keyword, num_titles)
  print(json.dumps(relevant_news_results, indent=4))
  
# -------------------------------------------------------------------------------- #

primary_search("Software", 6)

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

def secondary_search(keyword, most_relevant_titles, a_or_b, original_results, num_articles_per_brief=DEFAULT_NUM_ARTICLES_PER_BRIEF):
  # Initializing final dict and num articles per title 
  sources_by_story = {}
  num_articles = 10
  # If secondary a or b
  if a_or_b == "a":
    return secondary_a(sources_by_story,most_relevant_titles, keyword, num_articles)
  else: 
    return secondary_b(sources_by_story,most_relevant_titles, keyword, num_articles, original_results)
    
def secondary_a(sources_by_story, most_relevant_titles, keyword, num_articles):
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
  """
  Checking if any title matches the given title. If not, add to formatted_news_results
  """
  match_found = False
  for news_item in formatted_news_results:
    if news_item['title'] == title:
      match_found = True
      break

  if match_found == False:
    # If not, adding original article
    formatted_news_results[title] = original_results[title]

  return formatted_news_results
    

  
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
  