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
    """Writes top headline briefs to a file marked by current date"""
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
        for keyword in trending_keywords:
            trending_brief = in_brief(keyword, 1)
            file.write(trending_brief)
    
def search(company, industry, topic, topic2=""): 
    # Get the top headlines from headlines.txt
    headline_filename = "brief_files/headlines_" + curr_date + ".txt"
    if not os.path.exists(headline_filename):
        if __debug__:
            print("Getting Headlines")
        getTopHeadlinesBriefs()
    with open(headline_filename, 'r') as file:
        headlines_content = file.read()
    top_briefs = headlines_content
    
    # Get trending headlines from trending.txt
    trending_filename = "brief_files/trending_" + curr_date + ".txt"
    if not os.path.exists(trending_filename):
        if __debug__:
            print("Getting Trending Headlines")
        getTrendingBriefs()
    with open(trending_filename, 'r') as file:
        trending_content = file.read()
    trending_briefs = trending_content

    career_briefs = in_brief(company, 2)
    industry_briefs = in_brief(industry, 2)
    topic_briefs = in_brief(topic, 2)
    # topic2_briefs = in_brief(topic2, 2)

    briefing_dictionary = {}
    briefing_dictionary["top_headlines"] = top_briefs
    custom_headline_briefs = ""
    if industry_briefs is not None:
        custom_headline_briefs = custom_headline_briefs + "\n" + industry_briefs
    if topic_briefs is not None:
        custom_headline_briefs = custom_headline_briefs + "\n" + topic_briefs
    # if topic2_briefs is not None:
    #     custom_headline_briefs = custom_headline_briefs + "\n" + topic2_briefs
    if career_briefs is not None:
        custom_headline_briefs = custom_headline_briefs + "\n" + career_briefs
    briefing_dictionary["custom_headlines"] = custom_headline_briefs
    briefing_dictionary["trending_headlines"] = trending_briefs
    
    summary_prompt_v2 = f"""
    Create an oral transcript of a morning briefing with a duration of approximately 5 minutes. 
    Aim for minimal bias, ensuring that the information is presented clearly and factually, without leaning towards 
    any particular viewpoint and cite the sources provided in the given dictionary: 
    {json.dumps(briefing_dictionary, indent=4)}"""

    summary_prompt = f"""
    Create a morning briefing transcript designed to be read aloud, with a duration of approximately 5 minutes. 
    The briefing should be structured into three distinct sections: top global news stories (top_headlines), news stories 
    tailored to the listener's interests (custom_headlines), and lighter, fun news stories to start the day on a positive note 
    (fun_headlines). Aim for minimal bias, ensuring that the information is presented clearly and factually, without leaning towards 
    any particular viewpoint and cite the sources given the sources provided in the given dictionary: .{json.dumps(briefing_dictionary, indent=4)}"""
    print(summary_prompt)
    if __debug__:
        start_time = time.time()
    summary = get_gpt_response(summary_prompt_v2, gpt_model="gpt-4-turbo-preview")
    if __debug__:
        end_time = time.time()
        duration = end_time - start_time
        print(f"Final GPT call execution time: {duration} seconds")

    print(summary)


# Run this one time per day
# getTopHeadlinesBriefs()
# getTrendingBriefs()

# Viraj
# search("Amazon Corporation", "Sony Corporation", "Elden Ring")

# Nick
search("2024 US Election", "Climate and Business", "Alberta provincial politics", "Washington state politics")

# Christian: global politics and economy, basketball, social science acadameia, armenia, turkey, scientific innovation
# search("Global Politics and Economy", "Basketball", "Armenia", "Turkey")

# Daniel
# search("cats", "Technology", "piano", "")