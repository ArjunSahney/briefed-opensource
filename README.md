# Briefed - Personalized News and Morning Podcast

Briefed was a project developed by Arjun Sahney and Ram Gorthi that aimed to provide personalized news briefings and morning podcasts, summarizing top headlines and relevant articles from a variety of sources. It leveraged web scraping and summarization techniques to deliver tailored news briefings in text and audio formats, ensuring users received the most pertinent information based on their interests.

---

## **Table of Contents**
- [Overview of the System](#overview-of-the-system)
- [Scripts](#scripts)
  - [1. `search.py`](#1-searchpy)
  - [2. `briefed_main.py`](#2-briefed_mainpy)
  - [3. `morning_briefing.py`](#3-morning_briefingpy)
- [Directory Structure](#directory-structure)
- [User Experience and Example Usage](#user-experience-and-example-usage)
- [Interconnected Workflow](#interconnected-workflow)
- [Summary of How it Works](#summary-of-how-it-works)

---

## **Overview of the System**
The Briefed system automates the process of scraping news articles, summarizing them, and delivering personalized news briefings to users in both text and audio formats. The system follows a three-part pipeline:

1. **Scrape** news from various sources like Google News and Reuters.
2. **Summarize** articles using GPT-4, tailored to user preferences.
3. **Deliver** briefings in text and audio (podcast) formats.

---

## **Scripts**

### **1. `search.py`** - **News Scraping**
The `search.py` script forms the core of the news-gathering operation, using web scraping to retrieve articles relevant to user queries.

- **Primary Search**: Takes a user query (Q1) and scrapes relevant articles, storing results in a dictionary keyed by titles.
- **Secondary Search**: Generalizes the query to broaden the search and scrapes additional articles to provide depth.
- **Result Ranking**: Uses GPT-4 to rank articles by relevance to Q1.

**Outputs**: A dictionary mapping article titles to related content, which is passed to the next phase for summarization.

### **2. `briefed_main.py`** - **Brief Generation**
This script processes the news articles retrieved by `search.py` and generates summarized news briefs.

- **Summarization**: Articles are summarized using GPT-4 to create concise, easy-to-read briefings.
- **Additional Content**: Downloads images related to the articles for enhanced user experience.
- **File Management**: Summaries are saved in text format in the `brief_files/` directory.

**Outputs**: Text-based summaries that are either displayed to users or passed on for conversion into audio briefings.

### **3. `morning_briefing.py`** - **Personalized Morning Podcast**
This script generates daily personalized briefings and converts them into audio format for user access.

- **Formatting**: Cleans up text summaries to make them suitable for text-to-speech.
- **Top Headlines**: Fetches top news from `briefed_main.py` and combines them with personalized content.
- **Text-to-Speech**: Converts the briefing into an MP3 file, stored in the `audio/` directory for user download or streaming.

**Outputs**: Daily personalized podcasts in MP3 format based on user preferences.

---

## **Directory Structure**
- **`brief_files/`**: Stores daily text briefings.
- **`audio/`**: Stores the generated audio briefings in MP3 format.
  
---

## **User Experience and Example Usage**

For users like Arjun, the process would be as follows:

1. Input interests: Topics such as **Artificial Intelligence**, **Startups**, and **Technology**.
2. Receive summarized briefs for each topic.
3. Listen to personalized morning podcasts in audio format, delivered daily.
4. Access both text and audio briefings through organized directories.

---

## **Interconnected Workflow**
1. **News Scraping** (`search.py`): Retrieves relevant news articles.
2. **Brief Generation** (`briefed_main.py`): Summarizes the news articles into concise briefs.
3. **Morning Brief Creation** (`morning_briefing.py`): Compiles the summaries into a podcast format, accessible in both text and audio.

Each script is dependent on the outputs from the previous phase, ensuring an efficient and streamlined news briefing system.

---

## **Summary of How it Works**

Briefed provides users with a personalized news experience by:
1. Scraping and summarizing news articles tailored to user interests.
2. Organizing these summaries into easy-to-read text formats.
3. Converting the text into personalized podcasts for daily listening.
