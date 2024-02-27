from serpapi import GoogleSearch
import os

api_key=os.environ.get("serp_api_key")

params = {
    "q": "Morgan Stanley",
    "hl": "en",
    "gl": "us",
    "api_key": api_key
}

search = GoogleSearch(params)
results = search.get_dict()
top_stories = results.get("top_stories")
if top_stories is None:
  print("NONE")
else: print(top_stories[:10])