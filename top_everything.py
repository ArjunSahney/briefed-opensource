from newsapi import NewsApiClient
import requests

# Initialize the NewsApiClient
api_key = '785379e735a84282af1c6b35cf335a59'
newsapi = NewsApiClient(api_key=api_key)

def fetch_articles_from_source(source, num_articles=100):
    articles_list = []
    
    # Calculate the number of pages needed
    pages_needed = (num_articles + 99) // 100  # Using integer division to round up
    
    for page in range(1, pages_needed + 1):
        response = newsapi.get_everything(sources=source, page_size=100, page=page, language='en')
        articles_list.extend(response.get('articles', []))
    
    # Trim the list to the desired number of articles
    return articles_list[:num_articles]

def fetch_and_store_articles_by_category_and_source():
    sources_by_category = {
        "news": ["google-news"],  # Adjusted for 4 sources
        "business": ["business-insider"],  # Added bloomberg
        "technology": ["techcrunch", "the-verge"]  # Added the-verge
    }
    
    num_articles_by_category = {
        "news": 100,  # Now we'll fetch 50 from each of the 4 sources
        "business": 100,  # 50 each from business-insider and bloomberg
        "technology": 100  # 50 each from techcrunch and the-verge
    }
    
    articles_by_category = {}
    for category, sources in sources_by_category.items():
        articles_by_category[category] = []
        num_articles_per_source = num_articles_by_category[category] // len(sources)
        
        for source in sources:
            articles_by_category[category].extend(fetch_articles_from_source(source, num_articles_per_source))
    
    return articles_by_category

def display_articles_by_category_and_source():
    articles = fetch_and_store_articles_by_category_and_source()
    for category, articles_list in articles.items():
        print(f"{category.title()} News:")
        for idx, article in enumerate(articles_list, 1):
            print(idx, article['title'])
        print()

# Driver code
if __name__ == '__main__':
    display_articles_by_category_and_source()