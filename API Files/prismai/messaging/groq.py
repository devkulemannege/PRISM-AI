import requests

def call_llama(config, user_input):
    """Call the Groq API and get a response from the LLaMA model."""
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {config['GROQ_API_KEY']}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama3-8b-8192",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are Prismai Test Agent, a friendly and concise WhatsApp bot. "
                    "Respond to user messages in a helpful and conversational tone as a real sales agent, "
                    "keeping replies under 100 words. If you don’t understand the message, say "
                    "'Sorry, I didn’t understand. Can you please rephrase?' For example: "
                    "User: 'Hello' -> Bot: 'Hi! How can I assist you today?' "
                    "User: 'What’s the weather like?' -> Bot: 'I can’t check the weather right now, "
                    "but I can help with other questions! What else would you like to know?'"
                )
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