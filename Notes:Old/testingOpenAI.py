import os
from openai import OpenAI

client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
)
print(os.environ.get("OPENAI_API_KEY"))

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "Make up a name and tell it to me",
        }
    ],
    model="gpt-4",
)

#print(chat_completion)

if chat_completion.choices:
    # Access the first choice's message content
    ai_response = chat_completion.choices[0].message.content
    print("AI Response:", ai_response)
else:
    print("No response received.")
