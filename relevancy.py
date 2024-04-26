import os
import openai
import time

start_time = time.time()

client = openai.OpenAI(
    base_url="https://mistral-7b.lepton.run/api/v1/",
    api_key=os.environ.get('lepton_api_key')
)

titles = """
1. Snowflake releases a flagship generative AI model of its own

2. Perplexity hits unicorn status with $63M investment, launches secure AI enterprise search

3. Linux Foundation launches new industry push to develop better generative AI for enterprises

4. Exclusive | Jack Altman's Venture Fund Launches Accelerator for Enterprise AI Startups

5. Open-source vector database Qdrant launches hybrid cloud for enterprise AI apps

6. Recorded Future Launches Enterprise AI for Intelligence

7. Intel, Tech Giants Join Forces to Launch Open Platform for Enterprise AI

8. Intel and others commit to building open generative AI tools for the enterprise

9. Intel Announces Hala Point – World's Largest Neuromorphic System for Sustainable AI

10. AutoAlign spins off from Armilla, launches AI security platform 'Sidecar'

11. Snorkel AI Launches Snorkel Flow to Help Firms Harness Their Data for Custom AI Solutions

12. Snowflake targets enterprise AI with launch of Arctic LLM

13. Snowflake launches Arctic: An open enterprise-grade large language model - ET Edge Insights

14. Generative AI Search Startup Perplexity AI Raises $62.7M And Launches Enterprise Platform

15. AI Search Startup Perplexity's Series B Funding Raises Nearly $63M, Launches Enterprise Pro

16. Snowflake launches open LLM Arctic to cater to enterprise needs

17. AWS Announces New Capabilities for Amazon Bedrock

18. Intel Launches Gaudi 3 Accelerator, Advancing Enterprise AI with Performance and Openness

19. Snowflake unveils open LLM for cost-effective enterprise use cases

20. Snowflake Launches Arctic: The Most Open, Enterprise-Grade Large Language Model
"""

relevancyPrompt = f"""
Determine which of these article titles are most relevant to an individual interested in enterprise AI launches. Reference the titles by their number in the list. Return response in this form {{8, 4, 2, ...}}, where 8 is the most relevant article title.
{titles}
"""

relevant_titles = """
12. Snowflake targets enterprise AI with launch of Arctic LLM

13. Snowflake launches Arctic: An open enterprise-grade large language model - ET Edge Insights

14. Generative AI Search Startup Perplexity AI Raises $62.7M And Launches Enterprise Platform

15. AI Search Startup Perplexity's Series B Funding Raises Nearly $63M, Launches Enterprise Pro

16. Snowflake launches open LLM Arctic to cater to enterprise needs

1. Snowflake releases a flagship generative AI model of its own

8. Intel and others commit to building open generative AI tools for the enterprise

11. Snorkel AI Launches Snorkel Flow to Help Firms Harness Their Data for Custom AI Solutions

20. Snowflake Launches Arctic: The Most Open, Enterprise-Grade Large Language Model
"""

clusteringPrompt = f"""
Cluster similar news titles together into a list. 
Return response in JSON of this format 
{{
  "1": {{title n, title n2, title n3}}, 
  "2": {{title n, title n2}}, 
  ..
}}
{relevant_titles}
"""

completion = client.chat.completions.create(
    model="mistral-7b",
    messages=[
        {"role": "user", "content": clusteringPrompt},
    ],
    # max_tokens=128,
    stream=True,
    response_format={ "type": "json_object" },
)

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
