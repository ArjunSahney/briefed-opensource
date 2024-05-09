import spacy
from api_toolbox import *
from bs4 import BeautifulSoup
from http.client import RemoteDisconnected
import requests
from requests.exceptions import ConnectionError, Timeout, RequestException
import time # debugging latency
import numpy as np

# Load the pre-trained spaCy model
nlp = spacy.load("en_core_web_md")

def calculate_similarity(text1, text2):
    """
    Calculate the similarity between two texts using spaCy.

    Parameters:
        text1 (str): The first text to compare.
        text2 (str): The second text to compare.

    Returns:
        float: The similarity score between the two texts, ranging from 0 to 1.
    """
    if __debug__:
        start_time = time.time()
    # Process the texts
    doc1 = nlp(text1)
    doc2 = nlp(text2)

    # Compute the similarity between two documents
    similarity = doc1.similarity(doc2)
    if __debug__:
        end_time = time.time()
        duration = end_time - start_time
        print(f"spaCy similarity: {duration} seconds")
    return similarity

def compute_vector(title):
    """Takes a title (str) and returns vector representation"""
    return nlp(title).vector

def cosine_similarity(vec1, vec2):
    """Compute the cosine similarity between two vectors."""
    dot_product = np.dot(vec1, vec2)
    norm_product = np.linalg.norm(vec1) * np.linalg.norm(vec2)
    return dot_product / norm_product if norm_product else 0.0

def get_text_beautifulSoup(url):
    """Basic html parser, low latency: ~.2s
    Implemented some error handling

    Parameters
    ----------
    url : str

    Returns
    -------
    str
    """
    try:
        page = requests.get(url=url, timeout=10)
    except requests.exceptions.ConnectionError as e:
        if isinstance(e.args[0], RemoteDisconnected):
            print("RemoteDisconnected: The remote end closed connection without response")
        else:
            print("Other ConnectionError occurred")
        return None
    except Timeout:
        print("The request timed out after 10 seconds.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

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
    if len(text) >= nlp.max_length: # Skip extra-long articles
        print("Article text exceeds max nlp length")
        return None

    doc = nlp(text)

    # Tokenize the sentences and calculate their importance
    sentence_importance = {}
    for sentence in doc.sents:
        sentence_importance[sentence] = sum([token.vector_norm for token in sentence if not token.is_stop])

    # Sort the sentences by importance and select the top ones based on the ratio
    sorted_sentences = sorted(sentence_importance, key=sentence_importance.get, reverse=True)
    # print(sorted_sentences)
    if max_words:
        print(f"Compacting summary to {max_words}")
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

    return summary_text

def get_spaCy_article_summary(url, ratio=0.05, max_words=200):
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
    if article_text is None:
        return None
    if __debug__:
        start_time = time.time()
    summary = spaCy_summarize(article_text, ratio=ratio, max_words=max_words)
    # Check that summary does not exceed max_length:
    if len(summary) >= max_words:
        summary = summary[:max_words]
    if __debug__:
        end_time = time.time()
        duration = end_time - start_time
        print(f"spaCy summarizer: {duration} seconds")
    return summary


# Testing

