import json
from api_toolbox import *
import time # debugging latency
from datetime import datetime
from topic_tokens import *
import search
from image_scraper import download_main_image
from spaCy_summarizer import *

CURR_DATE = datetime.now().strftime('%Y-%m-%d')

def generate_brief(article_dict):
    """Receives article dictionary of form:

    {
        source: {
            "title": "Title 1"
            "summary": "Summary 1"
            "date": "date"
            "url": "https://example.com/article1"
        }
        source: ... 
        ...
    }
    
    And returns a brief. Can be called whenever you have multiple URLs & sources
    under a common topic! Summarizes using GPT-4. Will not function correctly with
    GPT-3.5-turbo.

    Parameters
    ----------
    articles_dict : dictionary

    Returns
    -------
    JSON
      Brief, containing title, summary, sources as separate key-value pairs
    """

    summary_prompt = f"""Summarize the key points in this JSON of articles into an explainer. Cite the article source in parens at the end of each sentence when you use information from a specific article, for example: (Source 1, Source 2). Limit response to 100 words. 
    If there are no relevant articles, return None for title and summary. 
    Explain key concepts and details. Use clear, precise language. Prioritize substance.
    Return response in a JSON of this format: {{ "Title": title, "Summary": summary }}.
    {json.dumps(article_dict, indent=4)}"""
    
    if __debug__:
        print("Article dictionary: ")
        print(json.dumps(article_dict, indent=4))
        
    summary_string = get_gpt_response(summary_prompt, gpt_model="gpt-4-turbo-preview", response_format="json")
    print(summary_string)
    summary_json = json.loads(summary_string)

        # Retrieve sources in parens in summary using regex
    import re
    pattern = r'\((.*?)\)'
    sources = re.findall(pattern, summary_string)

    if sources:
        extracted_sources = [source_list.split(', ') for source_list in sources]
        flattened_sources = [source for sublist in extracted_sources for source in sublist]
        print(flattened_sources)
    
        confirmed_sources = []
        for source in flattened_sources:
            if source in article_dict:
                confirmed_sources.append(source)
    
        # Prevent double citations and add to a sources string
        seen_articles = set()
        # Store sources in a list of 3-item lists (source name, date, URL)
        sources_list = []
        sources = "\n"
        for article_source in confirmed_sources:
            seen_articles.add(article_source)
            article_url = article_dict[article_source].get("url", "No URL")
            article_date = article_dict[article_source].get("date", "No date")
            sources_list_item = [article_source, article_url, article_date]
            sources_list.append(sources_list_item)
        summary_json['sources'] = sources_list
    else:
        summary_json['sources'] = []
    return (summary_json)

def download_image(story_title, sources_list):
    """
    Returns (boolean, image_url) tuple
    """
    image_downloaded = False
    # For each brief, pull one image from a source -- if there is an error move on to next source
    # Save the image as the same filename as brief just img
    img_filename = story_title + "_" + CURR_DATE
    for article_object in sources_list:
        url = article_object.get("link", None)
        if url is None:
            url = article_object.get("url", None)
        # Download the main image from the article URL if not already downloaded and if url is valid
        if not image_downloaded and url is not None:
            image_url = download_main_image(url, img_filename)
            if image_url:
                image_downloaded = True
    return (image_downloaded, image_url)

def in_brief(keyword, num_briefs):
    """Returns num_briefs briefs on a keyword
    
    Parameters
    ----------
    keyword : str
    num_briefs : int
    
    Returns
    -------
    str
        Consolidated list of briefs on keyword
    """
    # If brief file already exists, do not create a new one and return contents of current file
    curr_date = datetime.now().strftime('%Y-%m-%d')
    brief_filename = "brief_files/" + keyword + "_" + curr_date + ".txt"
    if os.path.exists(brief_filename):
        with open(brief_filename, 'r') as file:
            content = file.read()
        return content
    if __debug__:
        start_time = time.time()
    if (keyword.lower() == "headlines"):
        if __debug__:
            print("searching top headlines")
        # TODO: Need to handle top headlines
    
    else:
        stories_and_sources = search(keyword, num_briefs)
        brief_json_list = []

    # Collate articles in news_results    
    for story, sources in stories_and_sources.items():
        # Create formatted article dictionary for brief generation
        formatted_contents = {}
        for source in sources:
            source_name = source.get("source", None)
            source_title = source.get("title", None)
            source_link = source.get("link", None)
            source_date = source.get("date", None)
            source_summary = get_spaCy_article_summary(source_link, ratio=0.05, max_words=None)
            formatted_contents[source_name] = {source_title, source_summary, source_link, source_date}
            
        # Download image from one of the sources
        (image_downloaded, image_url) = download_image(story, sources)
        
        brief = generate_brief(formatted_contents)
        # Add image filepath into brief JSON
        if image_downloaded:
          brief["Image Filepath"] = image_url
        brief_json_list.append(brief)

        if __debug__:
          end_time = time.time()
          duration = end_time - start_time
          print(f"Generate brief execution time: {duration} seconds")
                
    with open(brief_filename, 'w') as file:
        # First write operation
        brief_string = json.dumps(brief_json_list, indent=4)

        file.write(brief_string)
    return brief_string
