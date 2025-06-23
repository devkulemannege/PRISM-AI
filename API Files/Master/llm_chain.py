from langchain_groq import ChatGroq
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain_core.runnables.history import RunnableWithMessageHistory
from connect_db import get_db_connection
import os
from dotenv import load_dotenv
import faiss
import pickle
from sentence_transformers import SentenceTransformer

# Load environment variables
load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), "credentials.env")))
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


# Store ChatMessageHistory instances for each session
session_histories = {}
llm = ChatGroq(api_key=GROQ_API_KEY, model="llama3-8b-8192")
def initialize_llm_chain(customer_id, db_sender, campaign_id):
    llm = ChatGroq(api_key=GROQ_API_KEY, model="llama3-8b-8192")
    # Remove Tavily tool and agent logic, revert to prompt template chain

    # Fetch customer and campaign details
    connection, cursor = get_db_connection()
    customer_name = "New Customer"
    campaign_name = "General Campaign"
    db_prompt = ""  # Ensure db_prompt is always defined
    campaign_prompt = """
        You are a friendly and concise WhatsApp bot and YOUR PRISM-AI whatsapp agent. Respond in a helpful and conversational tone as a real sales agent, keeping replies under 100 words.
        Customer Name: {customer_name}
        Campaign Name: {campaign_name}
        Conversation History: {history}
        User Message: {input}
        """
    history_data = []
    try:
        if customer_id and connection and cursor:
            # Fetch customer name
            cursor.execute("SELECT fName FROM customer WHERE mobileNo = %s", (db_sender,))
            customer_row = cursor.fetchone()
            if customer_row:
                customer_name = customer_row[0]

            # Fetch campaign details including the prompt
            cursor.execute(""" 
                SELECT campaignName, prompt FROM campaign
                WHERE campaignId = %s
            """, (campaign_id,))
            campaign_row = cursor.fetchone()
            campaign_data = None
            if campaign_row:
                campaign_name, db_prompt = campaign_row
                # Fetch campaign data from vector store
                campaign_data = fetch_campaign_by_name(campaign_name)

            # Load conversation history from chatlog
            cursor.execute("""
                SELECT customer_msg, LLM_msg FROM chatlog
                WHERE customerId = %s ORDER BY timestamp DESC LIMIT 5
            """, (customer_id,))
            history = cursor.fetchall()
            for user_msg, ai_msg in history:
                history_data.append({"input": user_msg, "output": ai_msg})
    except Exception as e:
        print(f"Database error in llm_chain: {e}")
    finally:
        if connection and cursor:
            cursor.close()
            connection.close()

    # Extract extra fields from campaign_data if available
    offer = campaign_data.get('offer', '') if campaign_data else ''
    main_benefits = campaign_data.get('main_benefits', '') if campaign_data else ''
    product_type = campaign_data.get('product_type', '') if campaign_data else ''
    target_audience = campaign_data.get('target_audience', '') if campaign_data else ''
    target_problem = campaign_data.get('target_problem', '') if campaign_data else ''
    unique_solution = campaign_data.get('unique_solution', '') if campaign_data else ''
    reason_why_needed = campaign_data.get('reason_why_needed', '') if campaign_data else ''
    social_proof = campaign_data.get('social_proof', '') if campaign_data else ''
    price = campaign_data.get('price', '') if campaign_data else ''
    urgency = campaign_data.get('urgency', '') if campaign_data else ''
    cta = campaign_data.get('cta', '') if campaign_data else ''

    # Initialize ChatMessageHistory for this session
    session_id = str(customer_id) if customer_id else db_sender
    if session_id not in session_histories:
        message_history = ChatMessageHistory()
        for item in history_data:
            message_history.add_user_message(item["input"])
            message_history.add_ai_message(item["output"])
        session_histories[session_id] = message_history

    # Define get_session_history
    def get_session_history(session_id):
        if session_id not in session_histories:
            session_histories[session_id] = ChatMessageHistory()
        return session_histories[session_id]

    # Use prompt template as before
    prompt_template = PromptTemplate(
        input_variables=[
            "history", "db_prompt", "input", "customer_name", "campaign_name", "offer", "main_benefits",
            "product_type", "target_audience", "target_problem", "unique_solution", "reason_why_needed",
            "social_proof", "price", "urgency", "cta"
        ],
        template=""":
        Prompt : {db_prompt}\n
        Customer Name: {customer_name}\n
        Campaign Name: {campaign_name}\n
        Product Type: {product_type}\n
        Target Audience: {target_audience}\n
        Target Problem: {target_problem}\n
        Unique Solution: {unique_solution}\n
        Reason Why Needed: {reason_why_needed}\n
        Main Benefits: {main_benefits}\n
        Social Proof: {social_proof}\n
        Price: {price}\n
        Offer: {offer}\n
        Urgency: {urgency}\n
        CTA: {cta}\n
        Conversation History: {history}\n
        User Message: {input}\n
        """
    )

    # Build the runnable chain
    chain = prompt_template | llm
    runnable = RunnableWithMessageHistory(
        runnable=chain,
        get_session_history=get_session_history,
        input_messages_key="input",
        history_messages_key="history"
    )

    # Return all required values for the prompt
    return (
        runnable, customer_name, campaign_name, offer, main_benefits, product_type, target_audience, target_problem,
        unique_solution, reason_why_needed, social_proof, price, urgency, cta, db_prompt, history_data
    )

def fetch_campaign_by_name(campaign_name, faiss_index_path="campaign_vector.index", meta_path="campaign_vector_meta.pkl"):
    # Load FAISS index and metadata
    faiss_index = faiss.read_index(faiss_index_path)
    with open(meta_path, "rb") as f:
        campaign_meta = pickle.load(f)  # List of dicts or objects

    # Encode the campaign name
    model = SentenceTransformer('all-MiniLM-L6-v2')
    campaign_vec = model.encode([campaign_name])

    # Search for the most similar campaign
    D, I = faiss_index.search(campaign_vec, k=1)
    best_idx = I[0][0]
    best_campaign = campaign_meta[best_idx]
    return best_campaign

def call_llm_with_chain(runnable, user_input, customer_name, campaign_name, session_id=None,
                        offer='', main_benefits='', product_type='', target_audience='', target_problem='',
                        unique_solution='', reason_why_needed='', social_proof='', price='', urgency='', cta='', db_prompt='', history=None):
    try:
        # Use session_id for uniqueness
        response = runnable.invoke(
            {
                "input": user_input,
                "customer_name": customer_name,
                "campaign_name": campaign_name,
                "offer": offer,
                "main_benefits": main_benefits,
                "product_type": product_type,
                "target_audience": target_audience,
                "target_problem": target_problem,
                "unique_solution": unique_solution,
                "reason_why_needed": reason_why_needed,
                "social_proof": social_proof,
                "price": price,
                "urgency": urgency,
                "cta": cta,
                "db_prompt": db_prompt,
                "history": history or []
            },
            {"configurable": {"session_id": str(session_id)}}
        )
        print(f"Response object: {repr(response)}")
        print(f"Response type: {type(response)}")
        if hasattr(response, 'content'):
            return response.content
        return str(response)
    except Exception as e:
        print(f"Error in call_llm_with_chain: {e}")
        raise




