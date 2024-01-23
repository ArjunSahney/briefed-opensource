from flask import Flask, render_template, request, redirect, url_for
from briefed_v2 import*

app = Flask(__name__)

# Route for the home page
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Extract form data and redirect to the results page
        keywords = request.form.get('keywords')
        return redirect(url_for('results', keywords=keywords))
    return render_template('index.html')

# Route to display results -- for now, summarization is NOT keyword-based
@app.route('/results/<keywords>')
def results(keywords):
    # Fetch and process the news summaries based on keywords
    summaries = fetch_and_summarize_news(keywords)  # This function will be defined later
    return render_template('results.html', summaries=summaries)

def fetch_and_summarize_news(keywords):
    articles_by_category = fetch_and_store_articles_by_category_and_source()
    processed_articles = []  # List to hold processed articles

    # Process each article
    for category, articles in articles_by_category.items():
        for article in articles:
            headline = article['title']
            summary = summarize_headline_5_words(headline)

            # Search for related articles
            url = "https://newsapi.org/v2/everything"
            params = {"q": summary, "apiKey": newsapi_key}
            response = requests.get(url, params=params)
            related_articles = response.json().get('articles', [])

            # Create a 75-word summary
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

                article['summary'] = summary
                article['topic_summary'] = topic_summary
                article['perspective_summary'] = perspective_summary

                print(f"Summary: {summary}")
                print(f"Topic Summary: {topic_summary}")
                print(f"Perspective Summary:\n{perspective_summary}\n")
            
                processed_articles.append({
                    'headline': article['title'],
                    'summary': summary,
                    'topic_summary': topic_summary,
                    'perspective_summary': perspective_summary
                })
    return processed_articles


if __name__ == '__main__':
    app.run(debug=True)