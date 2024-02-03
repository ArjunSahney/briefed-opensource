Search-Summarize-Search Algorithm:

1. Search for top headlines in a specific area `topic`
2. Summarize each top headline into a `top_headline_phrase`
3. Call News API to search for all news related to each `top_headline_phrase`

Result is a dictionary of `{top_headline_phrase, news_json}` pairs, where the `news_json` contains news stories, with sources, related to the headline
Goal is to use this dictionary to create 'news shorts': 1-2 paragraph summaries on each top headline phrase that cite sources 