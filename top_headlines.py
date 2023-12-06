from newsapi import NewsApiClient
import requests

# Initialize the NewsApiClient
api_key = '785379e735a84282af1c6b35cf335a59'
newsapi = NewsApiClient(api_key=api_key)

def get_top_headlines(source=None, category=None, country=None):
    """Fetch the top headlines based on source, category or country."""
    return newsapi.get_top_headlines(
        sources=source,
        category=category,
        country=country,
        language='en'
    )

def extract_headlines(response):
    """Extract and return the headlines from the response."""
    articles = response.get('articles', [])
    return [article['title'] for article in articles]

def fetch_headlines_by_category():
    categories = ['news', 'sports', 'entertainment', 'technology', 'business']
    headlines_by_category = {}
    
    # Fetch headlines for each category and store them in the dictionary
    for category in categories:
        if category == 'news':
            # Since there's no direct "news" category, we'll combine headlines from multiple sources
            bbc_news = extract_headlines(get_top_headlines(source='bbc-news'))
            us_news = extract_headlines(get_top_headlines(country='us'))
            google_news = extract_headlines(get_top_headlines(source='google-news'))
            headlines_by_category[category] = bbc_news + us_news + google_news
        else:
            headlines_by_category[category] = extract_headlines(get_top_headlines(category=category))
    
    return headlines_by_category

def display_headlines_by_category():
    headlines = fetch_headlines_by_category()
    for category, headlines_list in headlines.items():
        print(f"{category.title()} News:")
        for idx, headline in enumerate(headlines_list, 1):
            print(idx, headline)
        print()

# Driver code
if __name__ == '__main__':
    display_headlines_by_category()
