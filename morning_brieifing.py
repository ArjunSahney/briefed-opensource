from summed import *
from api_toolbox import get_gpt_response
from datetime import datetime
from text_speech import *
from mp3_upload import *
import json 
import time
import re

# Constants
NUM_TRENDING_BRIEFS = 3
NUM_HEADLINE_BRIEFS = 6
NUM_CUSTOM_BRIEFS = 18
NUM_CUSTOM_TOPICS = 3
curr_date = datetime.now().strftime('%Y-%m-%d')

def remove_sources(summary):
    """Helper method for in_morning_brief
    
    Takes a summary string (brief) and removes the sources. Used for morning briefing creation.
    
    Returns
    -------
    string
    """
    # Regular expression pattern to match parentheses and their contents
    pattern = r'\([^)]*\)'
    
    # Replace all matches with an empty string
    cleaned_summary = re.sub(pattern, '', summary)
    
    return cleaned_summary

def format_headlines(data):
    """Helper method for in_morning_brief to reformat email briefing JSON into morning briefing JSON
    
    Returns
    -------
    JSON/dict of this format:
    {
        "Story 1": [
            title,
            briefing,
            [source name 1, source name 2, etc],
        ]
        ...
        "Story n": [
            title,
            briefing,
            [source name 1, source name 2, etc],
        ]
    }
    """
    formatted_data = {}
    story_count = 1

    # Top Headlines
    if data['Top Headlines'] is not None:
        for headline in data['Top Headlines']:
            title = headline['Title']
            summary = remove_sources(headline['Summary'])
            sources = [source[0] for source in headline['sources']]
            formatted_data[f"Story {story_count}"] = [title, summary, sources]
            story_count += 1

    # Custom Headlines
    for topic, topic_briefs in data["Custom Headlines"].items():
        if topic_briefs is None: continue
        for topic_brief in topic_briefs:
            title = topic_brief['Title']
            summary = remove_sources(topic_brief['Summary'])
            sources = [source[0] for source in topic_brief['sources']]
            formatted_data[f"Story {story_count}"] = [title, summary, sources]
            story_count += 1

    # Trending Headlines
    if ('Trending Headlines' in data) and (data['Trending Headlines'] is not None):
        for headline in data['Trending Headlines']:
            title = headline['Title']
            summary = remove_sources(headline['Summary'])
            sources = [source[0] for source in headline['sources']]
            formatted_data[f"Story {story_count}"] = [title, summary, sources]
            story_count += 1

    return formatted_data

def getTopHeadlinesBriefs():
    """Writes top headline briefs as JSON to a file marked by current date"""
    global todays_top_briefs
    top_headline_briefs = in_brief("headlines", NUM_HEADLINE_BRIEFS)
    filename = "brief_files/headlines_" + curr_date + ".txt"
    with open(filename, 'w') as file:
        file.write(top_headline_briefs)

def getTrendingBriefs():
    """Writes top trending briefs to a file marked by current date"""
    trending_keywords = get_trending_topics(NUM_TRENDING_BRIEFS)
    filename = "brief_files/trending_" + curr_date + ".txt"
    with open(filename, 'w') as file:
        trending_briefs_list = []
        # Retrieve briefs and store in list
        for keyword in trending_keywords:
            trending_briefs_list.append(in_brief(keyword, 1))
        # Clean up trending briefs list by removing empty briefs
        non_empty_trending_briefs = []
        for trending_brief in trending_briefs_list:
            if (trending_brief is not None) and (trending_brief != "[]"):
                non_empty_trending_briefs.append(trending_brief)
        # Now process trending_briefs to add to briefing_dictionary
        file.write("[")
        last_brief_index = len(non_empty_trending_briefs) - 1
        for index, trending_brief in enumerate(non_empty_trending_briefs, start=0):
            # Remove highest-level open and close brackets on trending_brief
            trending_brief_formatted = trending_brief[1:-1]
            file.write(trending_brief_formatted)
            if index != last_brief_index:
                file.write(", ")
        file.write("]")
            
def generate_morning_briefing(name, briefing_dictionary, use_gpt=False):
    """Takes list of briefs and generates morning briefing and email briefing
    
    Parameters
    ----------
    name : of person briefing is for
    briefing_dictionary : dict/JSON of briefs
    use_gpt : boolean: if true, will use GPT to generate briefing; if false, will convert it manually. Defaults 'False'.
    
    Returns
    -------
    string
        Morning briefing text

    """
    
    #briefing_dictionary = json.loads(briefing_dictionary)
    # print(json.dumps(briefing_dictionary, indent=4))
    email_dictionary = {}
    morning_dictionary = {}
    # Take bottom half of all the briefs sections
    if briefing_dictionary["Top Headlines"] is not None:
        num_headline_briefs_actual = len(briefing_dictionary["Top Headlines"])
        email_dictionary["Top Headlines"] = briefing_dictionary["Top Headlines"][num_headline_briefs_actual//2:]
        morning_dictionary["Top Headlines"] = briefing_dictionary["Top Headlines"][:num_headline_briefs_actual//2]
    
    email_dictionary["Custom Headlines"] = {}
    morning_dictionary["Custom Headlines"] = {}
    for topic, topic_briefs in briefing_dictionary["Custom Headlines"].items():
        if topic_briefs is not None:
            # Set the email dictionary to cover the bottom half of the briefs
            num_topic_briefs = len(topic_briefs)
            email_dictionary["Custom Headlines"][topic] = topic_briefs[num_topic_briefs//2:]
            # Now truncate the original dictionary halfway
            morning_dictionary["Custom Headlines"][topic] = topic_briefs[:num_topic_briefs//2]
    
    if "Trending Headlines" in briefing_dictionary:
        if briefing_dictionary["Trending Headlines"] is not None:
            num_trending_briefs_actual = len(briefing_dictionary["Trending Headlines"])
            email_dictionary["Trending Headlines"] = briefing_dictionary["Trending Headlines"][num_trending_briefs_actual//2:]
            morning_dictionary["Trending Headlines"] = briefing_dictionary["Trending Headlines"][:num_trending_briefs_actual//2]

    # # Store dictionary for email briefing in email_name_date.txt
    # filename = "brief_files/email_dict_" + name + "_" + curr_date + ".txt"
    # with open(filename, 'w') as file:
    #     file.write(json.dumps(email_dictionary, indent=4))
    filename = "brief_files/morning_dict_" + name + "_" + curr_date + ".txt"
    with open(filename, 'w') as file:
        file.write(json.dumps(morning_dictionary, indent=4))

    if (use_gpt):
        summary_prompt_2 = f"""You are a news assistant tasked with creating a morning briefing to be read aloud for {name}. Your briefing should have the following characteristics:

1. Be based solely on the news updates provided, citing the sources using phrases like "From Reuters," or "According to the Associated Press."

2. Maintain an objective and impartial tone, aiming for minimal bias in your language and framing.

3. Use clear, precise, and concise language suitable for an oral briefing.

4. Prioritize substantive and relevant information over minor details.

5. Transition smoothly between topics.

6. Return your briefing as plain text without any special symbols or formatting.

Please create the morning briefing following these guidelines and incorporating the provided news updates.
        {json.dumps(morning_dictionary, indent=4)}
        """

        summary_prompt_1 = f"""You are a news assistant. Create a morning briefing to be read out loud for {name} based on the news updates provided below. Cite the sources provided in the updates. Aim for minimal bias. Utilize clear and precise language. Prioritize substance. Return plain text with no symbols. 
        
        News updates to use in briefing:
        {json.dumps(morning_dictionary, indent=4)}
        """

        if __debug__:
            start_time = time.time()
        briefing_text = get_gpt_response(summary_prompt_2, gpt_model="gpt-4-turbo-preview")
        # morning_briefing = get_togetherAI_response(summary_prompt, gpt_model="gpt-4-turbo-preview", response_format="json")

        if __debug__:
            end_time = time.time()
            duration = end_time - start_time
            print(f"morning briefing GPT call execution time: {duration} seconds")
    else:
        morning_briefing = format_headlines(morning_dictionary)
        data = morning_briefing

        # Initialize an empty list to store the story texts
        story_texts = []

        # Iterate over the stories
        for i, (story_key, story_value) in enumerate(data.items(), start=1):
            # Extract the story text and sources
            story_title = story_value[0]
            story_text = story_value[1]
            sources = ', '.join(story_value[2])

            # Construct the story text with the sources
            story_texts.append(f"Story {i} is {story_title}. {story_text} The sources I read to write this briefing are: {sources}.")

        # Construct the morning briefing text
        briefing_text = f"Good morning {name}! Today's briefing has {len(story_texts)} stories.\n\n"
        briefing_text += "\n\n".join(story_texts)
        briefing_text += "\nThat concludes your briefing for today."
    
    if __debug__:
        print(briefing_text) 
    
    briefing_text = briefing_text.replace('**', '')
    # Store copy of briefing transcript in morning_name_date.txt
    filename = "brief_files/morning_" + name + "_" + curr_date + ".txt"
    with open(filename, 'w') as file:
        file.write(briefing_text)
    # Convert to audio and store in audio/name.txt
    text_to_speech(briefing_text, name)
    audio_filename = "audio/" + name + ".mp3"
    mp3_url = upload_mp3_file('briefed_mvp2_mp3', audio_filename)
    email_dictionary["Audio URL"] = mp3_url
    # Store dictionary for email briefing in email_name_date.txt
    filename = "brief_files/email_dict_" + name + "_" + curr_date + ".txt"
    with open(filename, 'w') as file:
        file.write(json.dumps(email_dictionary, indent=4))


def in_morning_brief(name, company, industry, topic): 
    """Takes a name and 3 user attributes and generates email and morning briefing
    
    Returns 
    -------
    None
    """
    # Initialize briefs to None
    trending_briefs = None
    top_briefs = None
    custom_headline_briefs = None
    # Get the top headlines from headlines.txt
    headline_filename = "brief_files/headlines_" + curr_date + ".txt"
    if not os.path.exists(headline_filename):
        if __debug__:
            print("Getting Top Headlines")
        getTopHeadlinesBriefs()
    with open(headline_filename, 'r') as file:
        headlines_content = file.read()
    top_briefs = json.loads(headlines_content)
    
    # Get trending headlines from trending.txt
    trending_filename = "brief_files/trending_" + curr_date + ".txt"
    if not os.path.exists(trending_filename):
        if __debug__:
            print("Getting Trending Headlines")
        getTrendingBriefs()
    with open(trending_filename, 'r') as file:
        trending_content = file.read()
    if trending_content:
        # The string is not empty, proceed with JSON parsing
        # Replace '][' with ',' for json.loads() to work
        trending_content_formatted = trending_content.replace('][', ',')
        trending_briefs = json.loads(trending_content_formatted)
    else:
        # The string is empty
        if __debug__:
            print("Trending briefs is empty.")

    career_content = in_brief(company, NUM_CUSTOM_BRIEFS//NUM_CUSTOM_TOPICS)
    industry_content = in_brief(industry, NUM_CUSTOM_BRIEFS//NUM_CUSTOM_TOPICS)
    topic_content = in_brief(topic, NUM_CUSTOM_BRIEFS//NUM_CUSTOM_TOPICS)
    if career_content is not None and career_content != "[]":
        career_content = json.loads(career_content)
    else: career_content = None

    if industry_content is not None and industry_content != "[]":
        industry_content = json.loads(industry_content)
    else: industry_content = None

    if topic_content is not None and topic_content != "[]":
        topic_content = json.loads(topic_content)
    else: topic_content = None
          
    briefing_dictionary = {}
    if top_briefs:
        briefing_dictionary["Top Headlines"] = top_briefs
    else: briefing_dictionary["Top Headlines"] = None
    briefing_dictionary["Custom Headlines"] = {
        company: career_content,
        industry: industry_content,
        topic: topic_content
    }
    if trending_briefs:
        briefing_dictionary["Trending Headlines"] = trending_briefs
    
    generate_morning_briefing(name, briefing_dictionary, True)

# Run this one time per day
# getTopHeadlinesBriefs()
# getTrendingBriefs()

# Viraj
# search("Amazon Corporation", "Sony Corporation", "Elden Ring")

# in_morning_brief("Nick", "US Presidential Election", "Climate and Business", "Alberta provincial politics")

# in_morning_brief("Christian Chantayan", "Global Politics and Economy", "Basketball", "Armenia")

# in_morning_brief("Daniel Liu", "Cats", "Technology", "Piano")

# in_morning_brief("Jack Friedman", "AI", "Software", "Startups")

# in_morning_brief("Rishik", "Venture Capital", "OJ Simpson", "Tinnitus")

# in_morning_brief("Arjun", "Foreign Policy", "Economy", "International Affairs")

# in_morning_brief("John", "Ukraine", "Mortgage Rates", "2024 Presidential Election")

# in_morning_brief("Inika", "Google", "Quantum Computing", "U.S. Interest Rates")
