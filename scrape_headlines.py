#!/usr/bin/env python
# coding: utf-8

# Imports
import requests
from bs4 import BeautifulSoup
from termcolor import colored, cprint
import sys
from search import *
from briefed_main import *

#vars
stories = ['null']

def get_soup(url):
	response = requests.get(url)
	soup = BeautifulSoup(response.text, "html.parser")	
	return soup

def get_headlines(item_start_id, links_to_fetch):
	# scrape_url = "http://feeds.bbci.co.uk/news/rss.xml"
	scrape_url = "https://www.reutersagency.com/feed/?taxonomy=best-topics&post_type=best"
	current_item = item_start_id
	#request and parse html
	soup = get_soup(scrape_url)
	#isolate the rest of the headlines (articles)
	articles = soup.find_all('item')
	#extract headlines and url from links on main page & print
	for item in range(links_to_fetch):
		articleurl = articles[item].guid.text
		articleheadline = articles[item].title.text
		stories.append(articleurl)
		cprint(f"[{current_item}]{articleheadline}:", 'red', attrs=['bold'],end='\n')
		current_item+=1

#partial url example ( /news/1072279 ) 
def get_article_text(article_url):
	soup = get_soup(article_url)
	story = soup.find_all('p')
	#range_start is set to 12 to ignore all the pre-amble / social media ads.
	range_start = 12
	for p_tag in range(len(story)):
		if p_tag < range_start:
			pass
		else:
			print(story[p_tag].text)

	cprint("Press any key to return to Main Menu", 'red', attrs=['bold'], end='\n')
	input()

def main():
	get_headlines(1, 10)
	article_id = input("select an article id or Q to quit\n")
	if article_id.lower() == 'q':
		cprint("Goodbye!", 'red', end='\n')
		sys.exit()
	
	else:
		article_url = stories[int(article_id)]
		get_article_text(article_url)

while __name__ == "__main__":
	main()
	
def provide_headlines(aritcles_per_source):
	list_of_headlines = []

def create_headlines(num_headlines):
	sources = 5
	sources_by_story = {}

	articles_per_source = num_headlines//sources
	headlines = provide_headlines(articles_per_source)
	for headline in headlines: 
		search_terms_list = (get_improved_title_using_snippet(headline, None, type="search terms"))
		if search_terms_list is None:
			print("Error: Search terms not found")
            # Grab the first 5 words from article title as search words
			words = headline.split()  # Split the text into words
			search_terms = ' '.join(words[:5])  # Join the first five words
		else: 
			search_terms = ' '.join(search_terms_list[:3])
		sources_by_story[headline] = scrape_news(search_terms, DEFAULT_NUM_ARTICLES_PER_BRIEF)
		if sources_by_story[headline] is None:
			continue
		sources_by_story[headline].append(search_terms)
	return clean_sources(sources_by_story)
        
		
		
		
		
		
	
	