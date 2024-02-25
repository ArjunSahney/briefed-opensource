import openai
import requests
from newsapi import NewsApiClient
import datetime
# ADD TECHNICALS 
# Improvements: 
    # Use newsapi search asw for top headlines 

# Here is how the script works:
    # First it searches the top 100 articles per category for different sources i.e. Reuters
    # It then retrieves x many articles from Reuters and stores information about these different articles in dict
    # Then, it parses over the dictionary and summarizes each headline in 5 words and then searches for the summarized headline in NewsAPI
    # If articles are found (if related_articles:); then it summarizes them and stores the summaries in the dict

# Initialize API keys
newsapi_key = '5f67759ab3e74c6089d70eb25b88c160'
openai_api_key = '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'

# Set up NewsApiClient and OpenAI
newsapi = NewsApiClient(api_key=newsapi_key)
openai.api_key = openai_api_key

def summarize_headline_5_words(article):
    """Summarizes the article headline into 5 words."""
    message = {
        "role": "system",
        "content": "You are a helpful assistant. Summarize headlines into 5 words."
    }
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            message,
            {"role": "user", "content": f"Please summarize this headline: {article}"}
        ]
    )
    summarized_text = response['choices'][0]['message']['content'].strip()
    return summarized_text

import datetime

def fetch_articles_from_source(source, num_articles=100):
    """Fetch articles from a specified source within the last 24 hours."""
    articles_list = []
    pages_needed = (num_articles + 99) // 100

    # Calculate the date for 24 hours ago
    date_24_hours_ago = datetime.datetime.now() - datetime.timedelta(days=1)
    date_str = date_24_hours_ago.strftime('%Y-%m-%d')

    for page in range(1, pages_needed + 1):
        response = newsapi.get_top_headlines(sources=source, 
                                        #   from_param=date_str, 
                                          page_size=100, 
                                          page=page, 
                                          language='en')
        articles_list.extend(response.get('articles', []))
    return articles_list[:num_articles]

# def fetch_articles_from_source(source, num_articles=100):
#     """Fetch articles from a specified source."""
#     articles_list = []
#     pages_needed = (num_articles + 99) // 100
#     for page in range(1, pages_needed + 1):
#         response = newsapi.get_everything(sources=source, page_size=100, page=page, language='en')
#         articles_list.extend(response.get('articles', []))
#     return articles_list[:num_articles]

def fetch_articles_by_keyword(keyword, num_articles=10):
    # Fetch a specified number of articles related to a keyword
    articles_list = []
    response = newsapi.get_everything(q=keyword, page_size=num_articles, language='en')
    articles_list.extend(response.get('articles', []))
    return articles_list

def fetch_and_store_articles_by_category_and_source():
    """Fetch and store articles by category and source."""
    sources_by_category = {
        "news": ["reuters", "associated-press", "bbc-news"],
        "business": ["business-insider", "financial-times", "the-wall-street-journal"],
        "technology": ["techcrunch", "the-verge", "engadget"]
    }
    num_articles_by_category = {
        "news": 10,
        "business": 10,
        "technology": 10
    }
    articles_by_category = {}
    for category, sources in sources_by_category.items():
        articles_by_category[category] = []
        num_articles_per_source = num_articles_by_category[category] // len(sources)
        for source in sources:
            articles_by_category[category].extend(fetch_articles_from_source(source, num_articles_per_source))
    return articles_by_category

# Fetch articles
articles_by_category = fetch_and_store_articles_by_category_and_source()

# Process each article
for category, articles in articles_by_category.items():
    for article in articles:
        headline = article['title']
        summary = summarize_headline_5_words(headline)

        # Search for related articles
        url = "https://newsapi.org/v2/everything"
        params = {"q": summary, "apiKey": newsapi_key}
        response = requests.get(url, params=params)
        related_articles = response.json().get('articles', [])

        # Create a 75-word summary
        if related_articles:
            # Extract content from up to the first 100 articles
            contents = [a['content'] for a in related_articles[:100] if a.get('content')]
            combined_contents = ' '.join(contents)
        if related_articles:
            # Initial issue is that it was using descriptions to form article opinions etc. 
            # descriptions = ' '.join([a['description'] for a in related_articles if a['description']])
            topic_prompt = f"You are a world class, objective journalist who only uses sources that exist. Summarize the following into a factual 75-word summary using multiple sources:\n\n{combined_contents}"
            perspective_prompt = "You are a fantastic journalist, who cites multiple, sources that exist and provides true information. Identify and summarize the two major perspectives with specifics in 50 words each using existing sources based on the following content:\n\n" + combined_contents

            # Summarize topic
            topic_summary = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": topic_prompt}]
            )['choices'][0]['message']['content'].strip()

            # Summarize perspectives
            perspective_summary = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": perspective_prompt}]
            )['choices'][0]['message']['content'].strip()

            article['summary'] = summary
            article['topic_summary'] = topic_summary
            article['perspective_summary'] = perspective_summary

            # print(f"Summary: {summary}")
            # print(f"Topic Summary: {topic_summary}")
            # print(f"Perspective Summary:\n{perspective_summary}\n")