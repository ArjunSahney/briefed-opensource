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
import openai
from newspaper import Article
from newspaper.article import ArticleException
import requests
import json
import time 
from serpapi import GoogleSearch

__author__ = "Ram Gorthi, DJun Sahney"
__version__ = "1.0"

def get_gpt_response(prompt, gpt_model="gpt-4", json_mode=False, response_format=""):
  """Encapsulates GPT prompting
  User provides prompt and gets only the text of GPT response

  Parameters
  ----------
  prompt : str
  gpt_model : str, optional (default is "gpt-4")
    Can also input "gpt-3.5-turbo"
  response_format : str, optional
    Input "json" for json format
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
  if response_format == "json": 
    response = client.chat.completions.create(
    messages=[
      {
        "role": "user",
        "content": prompt,
      }
    ],
    response_format={ "type": "json_object" },
    model=gpt_model,
    )
  else:
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

def get_togetherAI_response(prompt, gpt_model="", response_format=""):
  TOGETHER_API_KEY = "aa58ec68cc6d1d36f211bac4effc828a971fcbf86b92dfa6fce0311efef7c99e"

  client = OpenAI(
    api_key=TOGETHER_API_KEY,
    base_url='https://api.together.xyz/v1',
  )

  chat_completion = client.chat.completions.create(
    messages=[
      {
        "role": "system",
        "content": "You are an expert writer.",
      },
      {
        "role": "user",
        "content": prompt,
      }
    ],
    response_format={ "type": "json_object" },
    model="mistralai/Mixtral-8x7B-Instruct-v0.1"
  )

  return (chat_completion.choices[0].message.content)


def get_lepton_response(prompt, model="mistral-7b", json_mode = False, max_tokens=None):
  """Gets response from mistral-7b through lepton
  
  Model selection can be modified within the function. Currently uses Mistral-7B.
  
  Parameters
  ----------
  prompt
  model : str, defaults to "mistral-7b"
    Can also input "Wizardlm-2-8x22b"
  json_mode : boolean, defaults false
  
  Returns
  -------
  response as string
  """
  if (model == "mistral-7b"):
    model_url = "https://mistral-7b.lepton.run/api/v1/"
  if (model == "Wizardlm-2-8x22b"):
    model_url = "https://wizardlm-2-8x22b.lepton.run/api/v1/"
  client = openai.OpenAI(
    base_url=model_url,
    api_key=os.environ.get('lepton_api_key')
  )

  completion_args = {
    "model": model,
    "messages": [{"role": "user", "content": prompt}],
    # max_tokens=128,
    "stream": True,
  }

  if json_mode:
    completion_args["response_format"] = {"type": "json_object"}
  if max_tokens:
    completion_args["max_tokens"] = max_tokens

  if __debug__:
    print(f"Getting response from {model} with prompt: {prompt}")
  completion = client.chat.completions.create(**completion_args)


  response = ""
  for chunk in completion:
      if not chunk.choices:
          continue
      content = chunk.choices[0].delta.content
      if content:
          response = response + content
  return response
  
def get_json_from_lepton(response, triple_ticks=False, attempt_num=1):
  """
  Given a response string, this function uses regular expressions to find the first JSON object within the string. If a JSON object is found, it is returned as a string. If no JSON object is found, a message is printed to the console indicating that no JSON was found in the text.
  
  Parameters
  ----------
  response (str): The response string from which to extract the JSON object.
  triple_ticks (bool): Is the JSON in triple ticks in the string?
  second_attempt (bool): Is this the second attempt at extracting JSON from the string? Do not modify. Used for recursion.
  
  Returns
  -------
  str
  """
  
  # Use regular expression to find the JSON object in the response string
  # Handles the very annoying case where the LM fails to complete the JSON and stops mid-way
  # This should have been done with a loop rather than recursion, but it's too late now, may re-do later
  if __debug__:
    start_time = time.time()
    print(f"Parsing to JSON {response}")

  import re
  
  # Remove triple ticks if present
  if triple_ticks:
    pattern = r'```json\s*(.*?)\s*```'
    match = re.search(pattern, response, re.DOTALL)
    if match:
      response = match.group(0)

  # Capture text with curly braces (including the braces)
  pattern = r'\{.*?\}'
  match = re.search(pattern, response, re.DOTALL)
  data = None
  if match:
    json_string = match.group(0)
    print("Extracted json string: ", json_string)
    # Parse the JSON string
    try:
      data = json.loads(json_string)
      return data
    except json.decoder.JSONDecodeError as e:
      print(f"Error parsing JSON: {e}")
  
  print("No JSON found in the text")
  print("Attempting to manually complete the JSON string")
  print(f"Attempt {attempt_num}")
  if (attempt_num == 1):
      # Add quotation and end curly brace
      response += "\"\n}"
  elif (attempt_num == 2):
      # Add only end curly brace
      response = response[:-3]
      response += "\n}"
  elif (attempt_num == 3):
      # Remove comma, add end curly brace
      response = response[:-4]
      response += "}"
  elif (attempt_num > 3):
      # Stop recursion
      return None
  data = get_json_from_lepton(response, triple_ticks=False, attempt_num=attempt_num+1)
  
  if __debug__:
    end_time = time.time()
    duration = end_time - start_time
    print(f"Parse to JSON attempt {attempt_num}: {duration} seconds")
  return data


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
    if __debug__:
      print("Serp API returns:")
      print(results['search_metadata']['id'])
      print(json.dumps(results, indent=4))

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
  
def get_google_results_valueserp(query, num_results, engine="google_news", topic_token=""):
  api_key=os.environ.get("valueserp_api_key")
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
  # Handling non-query case    
  else:
    params = {
      "api_key": api_key,
      "search_type": 'news',
      'q': query,
      'hl': 'en',
      'time_period': 'last_day'

    }
    # make the http GET request to VALUE SERP
    api_result_string = requests.get('https://api.valueserp.com/search', params)
    api_result_json = json.dumps(api_result_string.json(), indent=4)
    api_result_json = json.loads(api_result_json)
    print(json.dumps(api_result_json, indent=4))
    news_results = api_result_json.get("news_results", [])
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