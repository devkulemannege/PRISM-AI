
import requests
from config import GROQ_API_KEY, GROQ_LLM_URL

def call_llama(user_input):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama3-8b-8192",
        "messages": [
            {
                "role": "system",
                "content": "You are Prismai Test Agent, a friendly and concise WhatsApp bot. Respond to user messages in a helpful and conversational tone as a real sales agent, keeping replies under 100 words. If you don’t understand the message, say 'Sorry, I didn’t understand. Can you please rephrase?'"
            },
            {"role": "user", "content": user_input}
        ]
    }
    try:
        res = requests.post(url, headers=headers, json=data)
        res.raise_for_status()
        return res.json()['choices'][0]['message']['content']
    except Exception as e:
        print(f"Groq error: {e}")
        return "Sorry, I couldn't process that."
