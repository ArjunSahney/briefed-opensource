import spacy
from api_toolbox import *
from bs4 import BeautifulSoup
import requests
import time # debugging latency

# Load the pre-trained spaCy model
nlp = spacy.load("en_core_web_sm")

def get_text_beautifulSoup(url):
    """Basic html parser, low latency: ~.2s

    Parameters
    ----------
    url : str

    Returns
    -------
    str
    """
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    paragraphs = soup.find_all("p")
    text = " ".join([p.get_text() for p in paragraphs])
    return text

def spaCy_summarize(text, ratio=0.1, max_words=None):
    """Summarizes using spaCy

    Parameters
    ----------
    text : str
        Text of article to summarize
    ratio : float
        Ratio of given article to return back in summary
    max_words : int
    
    Returns
    -------
    str 
        Article summary
    """
    # Process the article text with spaCy
    doc = nlp(text)

    # Tokenize the sentences and calculate their importance
    sentence_importance = {}
    for sentence in doc.sents:
        sentence_importance[sentence] = sum([token.vector_norm for token in sentence if not token.is_stop])

    # Sort the sentences by importance and select the top ones based on the ratio
    sorted_sentences = sorted(sentence_importance, key=sentence_importance.get, reverse=True)
    
    if max_words:
        # Combine the selected sentences into a single string until the word limit is reached
        summary_text = ""
        word_count = 0
        for sentence in sorted_sentences:
            if word_count + len(sentence.text.split()) <= max_words:
                summary_text += str(sentence)
                word_count += len(sentence.text.split())
            else:
                break
    else:
        num_sentences = int(len(sorted_sentences) * ratio)
        summary = sorted(sorted_sentences[:num_sentences], key=lambda x: x.start)

        # Combine the selected sentences into a single string
        summary_text = " ".join(str(sentence) for sentence in summary)

    # Remove the annoyting 'Follow:' token at beginning of spaCy's summaries
    lines = summary_text.strip().split('\n')
    if lines[0].strip().startswith('Follow'):
        summary_text = '\n'.join(lines[1:])
    else:
        summary_text = text

    return summary_text

def get_spaCy_article_summary(url, ratio=0.1, max_words=None):
    """Gets low-latency text summary of article
    ~.4s total including article retrieval. Uses open source spacy library.

    Parameters
    ----------
    url : str
    ratio : float
        Length of summary, optional, default is 0.1
        Can also do 0.05 for even shorter summary
    max_words : int
        If user wants to restrict summary length, can specify word limit
        Summary will be truncated to max_words
    
    Returns
    -------
    str
        Summary of article
    """
    article_text = get_text_beautifulSoup(url)
    # start_time = time.time()
    summary = spaCy_summarize(article_text, ratio=ratio, max_words=max_words)
    # end_time = time.time()
    # duration = end_time - start_time
    # print(f"spaCy summarizer: {duration} seconds")
    return summary

def get_spaCy_article_dict_summary(articles_dict, ratio=0.2, max_words=None):
    """Logic for summarizing article dictionary without AI to reduce latency
    Doesn't work as intended unfortunately... don't have a way of citing sources
    with this model. 
    """
    combined_summary = ""
    article_summaries = {}

    for article_number, article_info in articles_dict.items():
        article_title = article_info["title"]
        article_summary = article_info["summary"]
        article_source = article_info["source"]

        # Process the article summary text with spaCy
        doc = nlp(article_summary)

        # Tokenize the sentences and calculate their importance
        sentence_importance = {}
        for sentence in doc.sents:
            sentence_importance[sentence] = sum([token.vector_norm for token in sentence if not token.is_stop])

        # Sort the sentences by importance and select the top ones based on the ratio
        sorted_sentences = sorted(sentence_importance, key=sentence_importance.get, reverse=True)
        num_sentences = int(len(sorted_sentences) * ratio)
        summary = sorted(sorted_sentences[:num_sentences], key=lambda x: x.start)

        # Combine the selected sentences into a single string
        summary_text = " ".join(str(sentence) for sentence in summary)

        # Append the individual article summaries to the combined summary with parenthetical citations
        combined_summary += f"{summary_text} ({article_number}: {article_title} - {article_source}) "

    return combined_summary