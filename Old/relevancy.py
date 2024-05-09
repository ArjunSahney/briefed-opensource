import os
import openai
import time

start_time = time.time()

client = openai.OpenAI(
    base_url="https://wizardlm-2-8x22b.lepton.run/api/v1/",
    api_key=os.environ.get('lepton_api_key')
)

titles = """  
ABB Startup Challenge winners use AI to support the energy transition
'The taste of stock options': Why startups are letting their staffers sell their shares
For AI startups, a billion-dollar dilemma: Why lofty valuations could be a hurdle in the race for talent
Kenyan mobility startup BuuPass acquires QuickBus to scale in Nigeria, SA
Can biotech startups upstage Eli Lilly and Novo Nordisk?
The 15 Start-Ups to Watch in 2024: Our Top Picks
GITEX Africa 2024:Your Ultimate Guide Towards an Innovative and Career-building Experience
Mint Explainer: Why good corporate-governance practices are crucial for startups | Mint
Impact startup Fynch Mobility banks €1M to make business trips greener
Indian GenAI Startup Tracker: Meet 60+ Startups Putting India On Global Map
"""

relevancyPrompt = f"""Rank the top 10 article titles by relevance to an individual interested in Startups. Return response as a JSON in this format:
{{
  "1": title 1,
  "2": title 2,
  ...
  "10": title 10
}}

{titles}
"""



relevant_titles = """
1. AI At The Edge: The New Vanguard Of Railway Innovation
2. Starseed Launches 'Pulitzer AI' for Automated Press Releases
3. Sayata launches groundbreaking AI platform for commercial insurance underwriting
4. Marin Software Launches AI-powered Anomaly Detector to Unlock Growth in Performance Marketing Campaigns
5. Google Launches AI Training Program For US Citizens And Grant Funds Worth IDR 1.2 Trillion
6. PROVEN Robotics launches OrionStar Mini, an AI service robot
7. Lonza launches AI-enabled route scouting
8. NIST launches GenAI evaluation program, releases draft publications on AI risks and standards
9. MHIRJ Launches New AI, Workforce Initiatives
10. UK startup Synthesia launches AI ‘expressive’ avatars that could cut cost of content creation
"""

clusteringPrompt = f"""
Combine any articles on the exact same story into a group.
Return your response in a JSON of this form,
{{
  "1": {{title n, title n2, title n3}}, 
  "2": {{title n, title n2}}, 
  ..
}}
{relevant_titles}
"""

title_snip = """"
"title": "\u2018Waiting for Trump\u2019: Viktor Orb\u00e1n hopes US election will change his political fortunes",
"snippet": "Exclusive: Hungary's PM and EU's most isolated leader says he is pursuing 'friendship with everybody' \u2013 particularly the former US president.",
"""

optimize_search_wordsPrompt = f"""Given the following title and snippett from a news article, optimize the title for the article to be descriptive and explanatory. Remove any clickbait or buzz words. Return response in this form {{"title": title}}.

{title_snip}

"""

completion = client.chat.completions.create(
    model="Wizardlm-2-8x22b",
    messages=[
        {"role": "user", "content": relevancyPrompt},
    ],
    max_tokens=300,
    stream=True,
    response_format={ "type": "json_object" }, # Switch JSON mode ON for relevancy and clustering prompts
)


print(relevancyPrompt)
for chunk in completion:
    if not chunk.choices:
        continue
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="")

end_time = time.time()
duration = end_time - start_time
print("")
print(f"Relevancy and clustering: {duration} seconds")
