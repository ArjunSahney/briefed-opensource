from serpapi import GoogleSearch
import os

api_key=os.environ.get("serp_api_key")

params = {
    "q": "Biden",
    "hl": "en",
    "gl": "us",
    "api_key": api_key
}

import json
search = GoogleSearch(params)
results = search.get_dict()
top_stories = results.get("top_stories")
if top_stories is None:
  print("NONE")
else: print(json.dumps(top_stories[:5], indent=4))