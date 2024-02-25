from summed import in_brief 
from api_toolbox import get_gpt_response
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

def search(company, industry, topic): 
    top_briefs = in_brief("top headlines", 5)
    career_briefs = in_brief(company, 2)
    industry_briefs = in_brief(industry, 2)
    topic_briefs = in_brief(topic, 2)
    fun_briefs = in_brief("entertainment", 2)

    briefing_dictionary = {}
    briefing_dictionary["top_headlines"] = top_briefs
    custom_headline_briefs = ""
    if industry_briefs is not None:
        custom_headline_briefs = custom_headline_briefs + "\n" + industry_briefs
    if topic_briefs is not None:
        custom_headline_briefs = custom_headline_briefs + "\n" + topic_briefs
    if career_briefs is not None:
        custom_headline_briefs = custom_headline_briefs + "\n" + career_briefs

    briefing_dictionary["custom_headlines"] = custom_headline_briefs
    briefing_dictionary["fun_headlines"] = fun_briefs
    summary_prompt = f"""
    Create a morning briefing transcript designed to be read aloud, with a duration of approximately 5 minutes. 
    The briefing should be structured into three distinct sections: top global news stories (top_headlines), news stories 
    tailored to the listener's interests (custom_headlines), and lighter, fun news stories to start the day on a positive note 
    (fun_headlines). Aim for minimal bias, ensuring that the information is presented clearly and factually, without leaning towards 
    any particular viewpoint and cite the sources given the sources provided in the given dictionary: .{json.dumps(briefing_dictionary, indent=4)}"""
    print(summary_prompt)
    start_time = time.time()
    summary = get_gpt_response(summary_prompt, gpt_model="gpt-4-turbo-preview")
    end_time = time.time()
    duration = end_time - start_time
    print(summary)
    print(f"Final GPT call execution time: {duration} seconds")


# Testing: 
search("Google", "Technology", "Cybersecurity")







