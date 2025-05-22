from langchain_groq import ChatGroq
from langchain.memory import ChatMessageHistory
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain_core.runnables.history import RunnableWithMessageHistory
from connect_db import get_db_connection
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), "credentials.env")))
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Store ChatMessageHistory instances for each session
session_histories = {}

def initialize_llm_chain(customer_id, db_sender):
    llm = ChatGroq(api_key=GROQ_API_KEY, model="llama3-8b-8192")

    # Fetch customer and campaign details
    connection, cursor = get_db_connection()
    customer_name = "New Customer"
    campaign_name = "General Campaign"
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
                SELECT b.campaignId, b.campaignName, b.prompt
                FROM campaign b
                JOIN customer_campaign cb ON b.campaignId = cb.campaignId
                WHERE cb.customerId = %s LIMIT 1
            """, (customer_id,))
            campaign_row = cursor.fetchone()
            if campaign_row:
                campaign_id, campaign_name, db_prompt = campaign_row
                if db_prompt:  # Use the campaign-specific prompt if available
                    campaign_prompt = db_prompt

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

    # Create PromptTemplate with dynamic prompt
    prompt_template = PromptTemplate(
        input_variables=["history", "input", "customer_name", "campaign_name"],
        template=campaign_prompt
    )

    # Build the runnable chain
    chain = prompt_template | llm
    runnable = RunnableWithMessageHistory(
        runnable=chain,
        get_session_history=get_session_history,
        input_messages_key="input",
        history_messages_key="history"
    )

    # Return the runnable and context variables
    return runnable, customer_name, campaign_name

def call_llm_with_chain(runnable, user_input, customer_name, campaign_name, session_id=None):
    try:
        # Use session_id for uniqueness
        response = runnable.invoke(
            {
                "input": user_input,
                "customer_name": customer_name,
                "campaign_name": campaign_name
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