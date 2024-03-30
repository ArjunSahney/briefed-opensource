from summed import *
from api_toolbox import get_gpt_response
from datetime import datetime
import json 
import time

# Components of Morning Briefing: 
    # 1. Top headlines (4)
    # 2. Top relevant/industry headlines (5)
    # 3. Fun/entertaining stories (1-2)

# Pseudocode: 

    # Search top_headlines (w/ param 5 articles) 
    # Search career, industry, and topic headlines
    # Search entertainment headlines 

    # Store top_headlines, relevant headlines, and entertainment briefs in dictionary 
    # Dictionary: 
        # top_headlines
            # string of summed.py return -- 5 briefs
         
        # custom_headlines
            # string of summed.py return 2 top briefs per search -- 6 briefs

        # fun_headlines
            # string of summed.py return 2 top briefs per entertainment section -- 2 briefs
    
    # Parse through dictionary w/ GPT specific prompt 

#########


# Get the top headlines and top trending once per day and store them in files
NUM_TRENDING_BRIEFS = 3
NUM_HEADLINE_BRIEFS = 3
curr_date = datetime.now().strftime('%Y-%m-%d')

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
        file.write("{")
        for keyword in trending_keywords:
            trending_brief = in_brief(keyword, 1)
            if trending_brief is not None:
                file.write(trending_brief + ",")
        file.write("}")
def generate_morning_briefing(name, briefing_dictionary):
    """Takes list of briefs and generates morning briefing with GPT call
    
    Parameters
    ----------
    briefs : list of strings
    
    Returns
    -------
    string
        Morning briefing text

    """
    summary_prompt = f"""You are a news assistant. Create a morning briefing of approximately 500 words based on the news updates provided below. Aim for minimal bias. Utilize clear and precise language. Prioritize substance. There should be a clean logical flow between topics. Return response in a JSON of this format:
    {{
        "Story 1": [
            briefing,
            [source 1, source 2, etc],
        ]
        ...
        "Story n": [
            briefing,
            [source 1, source 2, etc],
        ]
    }}
    
    News updates to use in briefing:
    {json.dumps(briefing_dictionary, indent=4)}
    """
    
    print(summary_prompt)
    if __debug__:
        start_time = time.time()
    morning_briefing = get_gpt_response(summary_prompt, gpt_model="gpt-4-turbo-preview", response_format="json")
    if __debug__:
        end_time = time.time()
        duration = end_time - start_time
        print(f"Final GPT call execution time: {duration} seconds")
    
    filename = "brief_files/morning_" + name + "_" + curr_date + ".txt"
    with open(filename, 'w') as file:
        file.write(morning_briefing)
    filename = "brief_files/briefingJSON_" + name + "_" + curr_date + ".txt"
    
    with open(filename, 'w') as file:
        file.write(json.dumps(briefing_dictionary, indent=4))

    print(morning_briefing) 
    

def in_morning_brief(name, company, industry, topic): 
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
        trending_content_formatted = trending_content.replace('][', ',')
        trending_briefs = json.loads(trending_content_formatted)
    else:
        # The string is empty
        if __debug__:
            print("Trending briefs is empty.")

    career_content = in_brief(company, 2)
    industry_content = in_brief(industry, 2)
    topic_content = in_brief(topic, 2)
    
    custom_headline_briefs = []
    if industry_content is not None:
        custom_headline_briefs.append(json.loads(industry_content))
    if topic_content is not None:
        custom_headline_briefs.append(json.loads(topic_content))
    if career_content is not None:
        custom_headline_briefs.append(json.loads(career_content))

    briefing_dictionary = {}
    if top_briefs:
        briefing_dictionary["Top Headlines"] = top_briefs
    if custom_headline_briefs:
        briefing_dictionary["Custom Headlines"] = custom_headline_briefs
    if trending_briefs:
        briefing_dictionary["Trending Headlines"] = trending_briefs
    generate_morning_briefing(name, briefing_dictionary)

# Run this one time per day
# getTopHeadlinesBriefs()
# getTrendingBriefs()

# Viraj
# search("Amazon Corporation", "Sony Corporation", "Elden Ring")

# Nick
in_morning_brief("Nick", "2024 US Election", "Climate and Business", "Alberta provincial politics")

# Christian: global politics and economy, basketball, social science acadameia, armenia, turkey, scientific innovation
# search("Global Politics and Economy", "Basketball", "Armenia", "Turkey")

# Daniel
# search("cats", "Technology", "piano", "")