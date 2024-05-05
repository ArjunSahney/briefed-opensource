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
from datetime import datetime

DEFAULT_NUM_TITLES = 10
DEFAULT_NUM_ARTICLES_PER_BRIEF = 5
CURR_DATE = datetime.now().strftime('%Y-%m-%d')

if __debug__:
    import logging
    # Configure logging
    logging.basicConfig(filename='sources_by_story.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# -------------------------------- PRIMARY SEARCH -------------------------------- #

def get_improved_title_using_snippet(title, snippet, type="title"):
    """
    Using title and snippet from news article object, returns an improved title as a string. 
    
    Caller must pass in the title and snippet strings from the news article object from the news_results JSON. Uses Mistral7B to optimize the title. Uses regex to extract JSON from LLM response (Mistral's JSON-mode is not as clean as GPT-4's)
    
    Parameters
    ----------
    title: str
    snippet: str
    type : str
        Can be "title" or "search terms", depending on what you want returned
        
    Returns
    -------
    str (for "title")
    str list (for "search terms") of search terms, ie ["term 1", "term 2", "term 3"]
    """
    
    optimize_to_search_terms_prompt = f"""Given the following title and snippet from a news article, generate a few search terms to describe the article. Return response in this form {{"search terms": search terms}}.
    
title: {title}
snippet: {snippet}
    """
    optimize_to_title_prompt = f"""Given the following title and snippet from a news article, optimize the title for the article to be descriptive and explanatory. Remove any clickbait or buzz words. Return response in this form {{"title": title}}.
    
title: {title}
snippet: {snippet}
    """
    if __debug__:
        start_time = time.time()
    
    # Pick prompt based on what the user wants returned
    if type == "title":
        prompt = optimize_to_title_prompt
    elif type == "search terms":
        prompt = optimize_to_search_terms_prompt
    improved_title_response = get_lepton_response(prompt, json_mode=True)
    
    # Use regular expression to find the JSON object in the respone string
    title_json = get_json_from_lepton(improved_title_response)
    if title_json is None:
        print("No JSON found in the text")
    else:
        if type == "title":
            optimized = title_json["title"]
            print("Optimized title: ", optimized)
        elif type == "search terms":
            optimized = title_json["search terms"]
            print("Optimized search terms: ", optimized)
            
    if __debug__:
        end_time = time.time()
        duration = end_time - start_time
        print(f"Optimize {type}: {duration} seconds")

    return optimized

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

def get_most_relevant_titles(news_results, keyword, num_results):
    """Returns list of most relevant titles to a given keyword
    
    Parameters
    ----------
    news_results: JSON
        Caller should simply pass in the news results JSON
    keyword: str
    num_results: int
        Will ask the LLM to rank the top min(2*num_results titles, len(news_results)) titles
    
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
    relevancyPrompt = f"""Rank the top {range_string} article titles by relevance to an
    individual interested in {keyword}. Return response as a JSON in this format:
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
    retry_count = 0
    while (news_results == 1 and retry_count < 2):
        news_results = get_google_results_valueserp(keyword, num_results)
        retry_count += 1

    if __debug__:
        end_time = time.time()
        duration = end_time - start_time
        print(f"ValueSerp retrieval time: {duration} seconds for {keyword}")

    if news_results == 1:
        print("Failed scrape. Please retry.")
    elif news_results is None:
        print(f"No news on {keyword}")
        return None
    else:
        return news_results


def relevancy_search(keyword, num_titles=DEFAULT_NUM_TITLES):
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
    
    # Now that we have the relevant news results, we can start the secondary search
    return relevant_news_results
  
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

def is_unique_story(new_title_and_vector, titles_and_vectors, threshold=0.75):
    """
    Parameters
    ----------
    new_vector_and_title : tuple (vector, title)
    vectors_and_titles : list of tuples (vector, title)
    threshold : float
    
    Returns
    -------
    str of title it is similar to or None
    """
    for title, vector in titles_and_vectors:
        similarity = cosine_similarity(new_title_and_vector[1], vector)
        if similarity > threshold:
            return title  # Similar title exists, return it
    return None

def clean_sources(sources_by_story):
    """
    Clean the sources for each story in the sources_by_story dictionary.
    1. Keep the most relevant sources for each story
    2. Remove repeat stories

    Parameters
    ----------
    sources_by_story (dict): A dictionary containing sources for each story.
    
    Returns
    -------
    sources_by_story (dict): The cleaned dictionary containing the most relevant sources for each story.
    """
    if sources_by_story is None:
        return
    
    # As we loop through the titles, we compute their vectors and store in titles_and_vectors
    titles_and_vectors = []
    if __debug__:
        logging.info('Making relevancy determinations for sources_by_story:\n')
    for title, sources in sources_by_story.items():
        # If sources is empty, we don't need to do anything
        if sources is None:
            continue
        search_terms = sources.pop()
        title_vector_tuple = (title, compute_vector(title))
        # Compare cosine similirity with previous titles
        similar_title = is_unique_story(title_vector_tuple, titles_and_vectors)
        if (similar_title is None): # If there are no similar titles
            # Compute vector for the title and add to title_vectors
            titles_and_vectors.append(title_vector_tuple)
            sources = sources_by_story[title]
            # Get relevant sources to the search terms (based on title and snippet of article)
            relevant_sources = get_most_relevant_titles(sources, search_terms, DEFAULT_NUM_ARTICLES_PER_BRIEF)
            sources_by_story[title] = relevant_sources
            if __debug__:
                logging.info('Sources by story JSON:\n%s', json.dumps(sources_by_story, indent=4))
        else:
            # If it's not unique, we want to add the sources for this title to the title it is similar to
            sources_by_story[similar_title].extend(sources_by_story[title])
    
    return sources_by_story


def secondary_search(most_relevant_titles, keyword, num_articles, a_or_b):
    """
    Generates sources by story for most relevant titles based on input parameters.
    Approach A: Ensure cohesion of sources_by_story for the given story using LLM
    Approach B: Approach A + append missing words

    Parameters
    ----------
    sources_by_story (dict): A dictionary to store sources for each relevant title.
    most_relevant_titles (list): A list of article objects representing the most relevant titles.
    num_articles (int): The number of articles to scrape for each title.

    Returns
    -------
    sources_by_story (dict): A dictionary containing the most relevant sources for each story.
    """    
    # Create dictionary to store sources for each relevant title
    sources_by_story = {}

    # Generate sources by story for each of the most relevant tiles
    for article_object in most_relevant_titles:
        # Check that article_object is not a string
        if isinstance(article_object, str):
            continue
        title = article_object.get("title", None)
        if title is None:
            continue
        snippet = article_object.get("snippet", None)
        # Optimize search terms based on title and snippet of article, if available
        # TODO: Needs to be tested HEAVILY (the json response mode w/ lepton is very inconsistent)
        search_terms_list = (get_improved_title_using_snippet(title, snippet, type="search terms"))
        if search_terms_list is None:
            print("Error: Search terms not found")
            # Grab the first 5 words from article title as search words
            words = title.split()  # Split the text into words
            search_terms = ' '.join(words[:5])  # Join the first three words
        else: 
            search_terms = ' '.join(search_terms_list[:3])
        
        if (a_or_b == "b"):
            # Append any missing words to the search terms
            search_terms = append_missing_words(keyword, search_terms)

        if __debug__:
            print("Search terms:" + search_terms)
            logging.info('Sources by story JSON:\n%s', json.dumps(sources_by_story, indent=4))

        # Save news results per story in sources_by_story
        sources_by_story[title] = scrape_news(search_terms, num_articles)
        # Save search terms at the end of the list associated with 'title' in sources_by_story
        if sources_by_story[title] is None:
            continue
        sources_by_story[title].append(search_terms)

    return clean_sources(sources_by_story)

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
    if __debug__:
        start_time = time.time()
    news_results = relevancy_search(topic)
    sources_by_story = secondary_search(news_results, topic, DEFAULT_NUM_TITLES, "a")
    print(json.dumps(sources_by_story, indent=4))
    if __debug__:
        print("Search duration: %s seconds" % (time.time() - start_time))

# search("Biden")
# TODO: We should think about the frequency of doing web scrapes on a keyword. Even if we don't generate the JSON, maybe we should still save the web scraped results... not sure. it would be useful for testing at the very least.
# search("Biden")


# Testing clean_sources
# Read JSON from testJSON.json
with open('testJSON.json') as f:
    sources_by_story = json.load(f)

print(json.dumps(clean_sources(sources_by_story), indent=4))

# Improvements to be made based on logs:
# 1. Prevent repeat stories: there are two stories on the World Press Freedom shit 
# 2. Ensure original result titles make it into sources by story 