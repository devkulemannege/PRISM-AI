from langchain_groq import ChatGroq
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain_core.runnables.history import RunnableWithMessageHistory
from connect_db import get_db_connection
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), "credentials.env")))
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def initialize_llm_chain(customer_id, sender):
    llm = ChatGroq(api_key=GROQ_API_KEY, model="llama3-8b-8192")

    prompt_template = PromptTemplate(
        input_variables=["history", "input", "customer_name", "campaign_name"],
        template="""
        You are a friendly and concise WhatsApp bot. Respond in a helpful and conversational tone as a real sales agent, keeping replies under 100 words.
        Customer Name: {customer_name}
        Campaign Name: {campaign_name}
        Conversation History: {history}
        User Message: {input}
        """
    )

    # Fetch customer and campaign details
    connection, cursor = get_db_connection()
    customer_name = "New Customer"
    campaign_name = "General Campaign"
    try:
        if customer_id and connection and cursor:
            cursor.execute("SELECT fName FROM customer WHERE mobileNo = %s", (sender,))
            customer_row = cursor.fetchone()
            if customer_row:
                customer_name = customer_row[0]
            cursor.execute("""
                SELECT b.campaignId, b.CampaignName
                FROM campaign b
                JOIN customer_campaign cb ON b.campaignId = cb.campaignId
                WHERE cb.customerId = %s LIMIT 1
            """, (customer_id,))
            campaign_row = cursor.fetchone()
            if campaign_row:
                campaign_id, campaign_name = campaign_row[0], campaign_row[1]
    except Exception as e:
        print(f"Database error in llm_chain: {e}")
    finally:
        if connection and cursor:
            cursor.close()
            connection.close()

    memory = ConversationBufferMemory(return_messages=True)

    # Define a function to get memory key (for multi-user, you can use sender or customer_id)
    def get_memory_key(inputs):
        return str(customer_id)

    # Build the runnable chain
    chain = prompt_template | llm

    runnable = RunnableWithMessageHistory(
        runnable=chain,
        memory=memory,
        get_session_history=get_memory_key,
        input_messages_key="input",
        history_messages_key="history"
    )

    # Return the runnable and context variables
    return runnable, customer_name, campaign_name



def call_llm_with_chain(runnable, user_input, customer_name, campaign_name, session_id=None):
    # Use customer_id or sender as session_id for uniqueness
    if session_id is None:
        session_id = customer_name  # or customer_id if available
    response = runnable.invoke(
        {
            "input": user_input,
            "customer_name": customer_name,
            "campaign_name": campaign_name
        },
        {"configurable": {"session_id": str(session_id)}}
    )
    return response