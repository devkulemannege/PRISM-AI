#Module name: call_llama.py
#Location: PRISM/agent/call_llama.py
# Description: This module is to call_llama to generate a response

from dotenv import load_dotenv
import os
import requests


#Load env variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../credentials.env"))
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def call_llama(user_input, prompt):
    """"""
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama3-8b-8192",
        "messages": [
            {
                "role": "system",#in here its the role of the system set the prompt
                "content": prompt#In here its the 
            },
            {"role": "user", "content": user_input}
        ]
    }
    try:
        res = requests.post(url, headers=headers, json=data)
        res.raise_for_status()
        response_json = res.json()
        print(f"Groq API Response: {response_json}")
        if 'choices' not in response_json:
            print(f"Groq API Error: {response_json.get('error', 'Unknown error')}")
            return "Sorry, I couldn't process your request right now. Please try again later."
        return response_json['choices'][0]['message']['content']
    except Exception as e:
        print(f"Groq API Request Failed: {e}")
        return "Sorry, I couldn't process your request right now. Please try again later."
