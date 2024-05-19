from .models import Brief
import json
import os
from datetime import datetime
from api_toolbox import *
from topic_tokens import *
from search import *
from image_scraper import download_main_image
from spaCy_summarizer import *
import time
from briefed_main import *

CURR_DATE = datetime.now().strftime('%Y-%m-%d')

def generate_brief(article_dict):
    summary_prompt = f"""Summarize the key points in this JSON of articles into an explainer. Cite the article source in parens at the end of each sentence when you use information from a specific article, for example: (Source 1, Source 2). Limit response to 100 words. 
    If there are no relevant articles, return None for title and summary. 
    Explain key concepts and details. Use clear, precise language. Prioritize substance.
    Return response in a JSON of this format: {{ "Title": title, "Summary": summary }}.
    {json.dumps(article_dict, indent=4)}"""
    
    summary_string = get_gpt_response(summary_prompt, gpt_model="gpt-4-turbo-preview", response_format="json")
    summary_json = json.loads(summary_string)

    import re
    pattern = r'\((.*?)\)'
    sources = re.findall(pattern, summary_string)

    if sources:
        extracted_sources = [source_list.split(', ') for source_list in sources]
        flattened_sources = [source for sublist in extracted_sources for source in sublist]
    
        confirmed_sources = []
        for source in flattened_sources:
            if source in article_dict:
                confirmed_sources.append(source)
    
        seen_articles = set()
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
    return summary_json

def download_image(story_title, sources_list):
    image_downloaded = False
    img_filename = story_title + "_" + CURR_DATE
    for article_object in sources_list:
        if isinstance(article_object, str):
            continue
        url = article_object.get("link", None)
        if url is None:
            url = article_object.get("url", None)
        if url is None:
            continue
        if not image_downloaded and url is not None:
            image_url = download_main_image(url, img_filename)
            if image_url:
                image_downloaded = True
    return (image_downloaded, image_url)

def generate_custom(user, interests):
    custom_briefs = []
    for interest in interests:
        existing_briefs = Brief.objects.filter(interest=interest)
        if existing_briefs.exists():
            custom_briefs.extend(existing_briefs)
        else:
            stories_and_sources = search(interest, num_briefs=6)
            for story, sources in stories_and_sources.items():
                formatted_contents = {}
                for source in sources:
                    if isinstance(source, str):
                        continue
                    source_name = source.get("source", None)
                    source_title = source.get("title", None)
                    source_link = source.get("link", None)
                    source_date = source.get("date", None)
                    source_summary = get_spaCy_article_summary(source_link, ratio=0.1, max_words=200)
                    formatted_contents[source_name] = {
                        "title": source_title,
                        "summary": source_summary,
                        "date": source_date,
                        "url": source_link
                    }
                (image_downloaded, image_url) = download_image(story, sources)
                brief = generate_brief(formatted_contents)
                if image_downloaded:
                    brief["Image Filepath"] = image_url
                brief_obj = Brief.objects.create(
                    title=brief["Title"],
                    content=brief["Summary"],
                    interest=interest,
                    sources=json.dumps(brief["sources"]),
                    image_url=brief.get("Image Filepath", "")
                )
                custom_briefs.append(brief_obj)
    return custom_briefs

#### 
## Generate 200 general briefs CODE: 

def general_headlines(num_headlines): 
    in_brief("headlines", num_headlines)
    #

