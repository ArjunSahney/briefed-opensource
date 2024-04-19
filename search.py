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

NUM_TITLES = 10
NUM_ARTICLES_PER_BRIEF = 5

# -------------------------------- PRIMARY SEARCH -------------------------------- #

def generalize_keyword(keyword):
  """Use llama to generalize a specific news topic"""

def get_most_relevant_titles(titles, keyword):
  """Returns list of most relevant titles to a given keyword"""

def format_serp_results(results):
  """Formats Serp API results into dictionary keyed by title"""

def primary_search(keyword):
  """Retrieve most relevant titles to the keyword"""

# -------------------------------------------------------------------------------- #


# -------------------------------- SECONDARY SEARCH ------------------------------ #

def append_missing_words(words_to_append, append_to_this_string):
  """Appends words from "words_to_append" to "append_to_this_string" if they are missing"""

def title_to_searchwords(title):
  """Get the optimal searchwords from a news title"""

# -------------------------------------------------------------------------------- #
