import openai
import requests
from newsapi import NewsApiClient

# Initialize API keys
newsapi_key = '2387cb1f2f0c45579e322e9869140678'
openai_api_key = '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'

# Set up NewsApiClient and OpenAI
newsapi = NewsApiClient(api_key=newsapi_key)
openai.api_key = openai_api_key

def summarize_headline(headline):
    """Summarizes article headline into a few words."""
    message = {
        "role": "system",
        "content": "You are an objective journalist. Summarize this headline into a few words."
    }
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            message,
            {"role": "user", "content": f"Article headline: {headline}"}
        ]
    ) 
    summarized_text = response['choices'][0]['message']['content'].strip()
    return summarized_text

def fetch_articles_from_source(source, num_articles=10):
    """Fetch articles from a specified source."""
    articles_list = []
    pages_needed = (num_articles + 99) // 100
    for page in range(1, pages_needed + 1):
        response = newsapi.get_everything(sources=source, page_size=100, page=page, language='en')
        articles_list.extend(response.get('articles', []))
    return articles_list[:num_articles]

def fetch_and_store_articles_by_keyword(keyword):
    """Fetch and store articles by keyword."""
    ##TODO: Change function to operate by keyword and fetch 10 articles
    sources_by_category = {
        "news": ["reuters", "associated-press", "axios"],
        "business": ["business-insider", "financial-times"],
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
articles_by_category = fetch_and_store_articles_by_keyword()

# Process each article
for category, articles in articles_by_category.items():
    for article in articles:
        headline = article['title']
        summary = summarize_headline(headline)

        # Search for related articles
        url = "https://newsapi.org/v2/everything"
        params = {"q": summary, "apiKey": newsapi_key}
        response = requests.get(url, params=params)
        related_articles = response.json().get('articles', [])

        # Create a 75-word summary
        if related_articles:
            descriptions = ' '.join([a['description'] for a in related_articles if a['description']])
            topic_prompt = f"You are a world class, objective journalist. Summarize the following into a factual and informative 75-word summary. List the given sources at the bottom of your summary:\n\n{descriptions}"
            # perspective_prompt = "You are a fantastic journalist, who cites multiple, diverse sources and provides analytical, true information. Identify and summarize the two major perspectives with specifics in 50 words each using sources based on the following content:\n\n" + descriptions
            perspective_prompt = "Identify and summarize the two major perspectives with specifics in 50 words based on the following content.\n\n" + descriptions

            # Summarize topic
            topic_summary = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": topic_prompt}]
            )['choices'][0]['message']['content'].strip()

            # Summarize perspectives
            perspective_summary = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": perspective_prompt}]
            )['choices'][0]['message']['content'].strip()

            article['summary'] = summary
            article['topic_summary'] = topic_summary
            article['perspective_summary'] = perspective_summary

            print(f"Summary: {summary}")
            print(f"Topic Summary: {topic_summary}")
            print(f"Perspective Summary:\n{perspective_summary}\n")