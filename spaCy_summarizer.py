import spacy
from api_toolbox import *
from bs4 import BeautifulSoup
import requests
import time # debugging latency

# Load the pre-trained spaCy model
nlp = spacy.load("en_core_web_sm")

def get_text_beautifulSoup(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    paragraphs = soup.find_all("p")
    text = " ".join([p.get_text() for p in paragraphs])
    return text

def summarize_article(text, ratio=0.1):
    # Process the article text with spaCy
    doc = nlp(text)

    # Tokenize the sentences and calculate their importance
    sentence_importance = {}
    for sentence in doc.sents:
        sentence_importance[sentence] = sum([token.vector_norm for token in sentence if not token.is_stop])

    # Sort the sentences by importance and select the top ones based on the ratio
    sorted_sentences = sorted(sentence_importance, key=sentence_importance.get, reverse=True)
    num_sentences = int(len(sorted_sentences) * ratio)
    summary = sorted(sorted_sentences[:num_sentences], key=lambda x: x.start)
    summary_text = " ".join(str(sentence) for sentence in summary)
    lines = summary_text.strip().split('\n')
    if lines[0].strip().startswith('Follow'):
        summary_text = '\n'.join(lines[1:])
    else:
        summary_text = text

    return summary_text

# Example usage
article_text = get_text_beautifulSoup("https://www.cnn.com/2024/02/21/politics/student-loan-forgiveness-biden-debt/index.html")
start_time = time.time()
summary = summarize_article(article_text)
end_time = time.time()
duration = end_time - start_time
print(f"spaCy summarizer: {duration} seconds")
print(summary)