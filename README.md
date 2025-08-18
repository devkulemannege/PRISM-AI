# PRISM-AI

# Personalized Responsive &amp; Intelligent Sales Machine

A personalized AI agent that attracts customers to businesses by acting as a salesperson through interactive conversations done through social media platforms.

**Main File to Execute: [app.py](app.py)**

# PRISM-AI WhatsApp Agent Workflow

1. User sends a WhatsApp message to the business number.
2. Meta (WhatsApp) sends a webhook POST to /webhook in Master/app.py.
3. Flask receives the webhook and extracts the sender and message text.
4. The system attempts to match the sender to a customer in the database.
5. The incoming message text is passed to the FAISS vector store (find_relevant_campaign in faiss_store.py) to find the most relevant campaign (by campaign_id).
6. The campaign_id is used to fetch campaign details from the SQL database and/or vector store (llm_chain.py).
7. The system loads recent conversation history for the customer (from chatlog table).
8. All relevant campaign fields (offer, main_benefits, product_type, etc.) and conversation history are assembled into a prompt template.
9. The prompt is sent to the LLM (LangChain + Groq Llama3) to generate a response.
10. The AI-generated response is sent back to the user via WhatsApp API.
11. The conversation (user message, AI reply, campaign_id) is logged in the chatlog table for future context.
12. (Optional) Outbound campaign messages can be sent in bulk to customers using send_template_to_all.

### Key Components:
- app.py: Flask app, webhook, main routing, WhatsApp API integration
- faiss_store.py: Vector store for campaign retrieval (semantic search)
- llm_chain.py: LLM prompt construction, campaign/context assembly, LangChain logic
- chatlog_table.py: Conversation logging
- connect_db.py: Database connection utility
- CustomerUpload/: Uploaded customer CSVs for campaign targeting

Data Flow:
WhatsApp → Flask webhook → DB lookup & vector search → campaign/context assembly → LLM → WhatsApp reply → chatlog

[Click here for video demonstration.](https://www.youtube.com/watch?v=xiRZh_X4XKk&t=284s)

