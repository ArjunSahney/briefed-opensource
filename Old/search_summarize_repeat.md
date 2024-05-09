# Search-Summarize-Repeat Algorithm:

### 1. Search for top headlines on a specific `topic`
Potentially utilize google search in python or SerpApi or other API to search for top headlines on a particular topic. Must be able to grab results on niche topics. Could even potentially just grab the top 10 URLs on a specific google search, then crawl the websites to determine the top news stories regarding that google search.

### 2. Summarize each top headline into a `top_headline_phrase`
Utilizing OpenAI API, GPT 3.5 turbo for simple summarization task.

### 3. Call News API to search for all news related to each `top_headline_phrase`
Result is a dictionary of `{top_headline_phrase, news_json}` pairs, where the `news_json` contains news stories, with sources, related to the headline.

### 4. Summarize each `{top_headline_phrase, news_json` pair into news shorts
Goal is to use dictionary to create 'news shorts': 1-2 paragraph summaries on each top headline phrase that cite sources. This will likely be done using OpenAI API, GPT 4 turbo for advanced summarization
