from serpapi import GoogleSearch
import json
import openai
import requests

# Initialize API keys
newsapi_key = '5f67759ab3e74c6089d70eb25b88c160'
openai_api_key = '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'


def search_topic(query):
    params = {
        "engine": "google_news",
        "q": query,
        "api_key": "6bd8076584cc412e4de18cd156206095ceefc0b2e16c7f6a4de7f1af84879d9a"
    }

    search = GoogleSearch(params)
    results = search.get_dict()
    return results.get("news_results", [])


def summarize_search_newsapi(query):
    news_results = search_topic(query)
    # parsed_news = json.loads(news_results)
    custom_dict = dict(query=dict())
    for article in news_results:
        
        title = article['title']
        summary = summarize_headline_5_words(title)
        
        
        # Search for related articles
        url = "https://newsapi.org/v2/everything"
        params = {"q": summary, "apiKey": newsapi_key}
        response = requests.get(url, params=params)
        related_articles = response.json().get('articles', [])

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

            custom_dict[query] = {
                'summary': summary,
                'topic_summary': topic_summary,
                'perspective_summary': perspective_summary
            }

            print(topic_summary)

    
    


def summarize_headline_5_words(article):
    """Summarizes the article headline into 5 words."""
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": f"Please summarize this headline into 5 words: \"{article}\""}
            ]
        )
        summarized_text = completion.choices[0].message['content'].strip()
        return summarized_text
    except Exception as e:
        print(f"An error occurred: {e}")
        return ""


summarize_search_newsapi("tesla")


