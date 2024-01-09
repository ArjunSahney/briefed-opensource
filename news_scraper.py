"""
File: news_scraper.py
Author: Ram Gorthi
Date: January 8, 2024

Description: 
    This script fetches news headlines based on user-provided keywords. It uses the News API to retrieve
    current top headlines and summarizes them using the OpenAI API. The script demonstrates basic
    functionality for a news summary application.
"""

import requests
from typing import List

class Brief:
    def __init__(self, headline, summary):
        self.sources_list = []
        self.headline = headline
        self.summary = summary

    def add_source(self, source):
        if source not in self.sources_list:
            self.sources_list.append(source)

class Headlines:
    """
    Headlines will contain a list of Brief objects
    """
    def __init__(self, keyword):
        self.keyword = keyword
        self.briefs = []

    def add_brief(self, brief):
        if brief not in self.briefs:
            self.briefs.append(brief)

def prompt_user() -> List[str]:
    """
    Take three user inputs through the terminal on topics of interest.
    """
    print("Enter three keywords for news topics of interest:")
    keyword_list = [input(f"Keyword {i+1}: ") for i in range(3)]
    return keyword_list

def extract_keywords():
    """
    Not necessary in this iteration; may be used in later versions
    """
    pass

def scrape_news(keywords: List[str], api_key: str) -> Headlines:
    """Get current top headlines for category

    Parameters
    ----------
    keyword_list : List[str]
        Stores keywords for making news API calls
    
    Returns
    -------
    headline_summaries : Headlines
        Stores briefs (headline name, summary, sources) for each 
        headline returned by the news API
    """
    headlines_list = []
    base_url = "https://newsapi.org/v2/top-headlines"
    
    for keyword in keywords:
        
        params = {"country": "us", "apiKey": api_key, "q": keyword}
        response = requests.get(base_url, params=params)
        print(response.json())  # Added this line to debug

        data = response.json()
        
        if data["status"] == "ok":
            
            headlines_obj = Headlines(keyword)
            
            for article in data["articles"]:
                brief = Brief(article["title"], article["description"])
                brief.add_source(article["source"]["name"])
                headlines_obj.add_brief(brief)
            
            headlines_list.append(headlines_obj)
    
    return headlines_list

def display_news(headline_summaries: List[Headlines]):
    """
    Displays news in the following format: 

    Headline 1
    Summary:

    Headline 2
    Summary:

    etc

    Parameters
    ----------
    headline_summaries : Headlines
        Stores briefs (headline name, summary, sources) for each headline
    """
    for headlines in headline_summaries:
        print(f"\nKeyword: {headlines.keyword}\n{'-'*40}")
        
        for brief in headlines.briefs: 
            print(f"Headline: {brief.headline}\nSummary: {brief.summary}\nSources: {', '.join(brief.sources_list)}\n")

def main():
    """
    Call prompt_user(), send keyword_list into scrape_news(), 
    then call display_news() 
    """
    api_key = "2387cb1f2f0c45579e322e9869140678"
    keywords = prompt_user()
    headline_summaries = scrape_news(keywords, api_key)
    display_news(headline_summaries) 

if __name__ == "__main__":
    main()