"""
Module to create and manage a cloud vector store for campaign details using Qdrant Cloud.
"""

import os
from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv


# Load environment variables
load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'credentials.env')))

# Initialize Qdrant client with free tier credentials (replace with your values)
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = "campaigns"

# Initialize embedding model
embedding_model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')

# Initialize Qdrant client
qdrant_client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY
)

# Ensure the collection exists
def initialize_vector_store():
    """
    Initialize the Qdrant collection if it doesn't exist.
    """
    try:
        collections = qdrant_client.get_collections().collections
        if COLLECTION_NAME not in [c.name for c in collections]:
            qdrant_client.recreate_collection(
                collection_name=COLLECTION_NAME,
                vector_size=768,  # Matches all-MiniLM-L6-v2 output
                hnsw_config=models.HnswConfigDiff(
                    m=16,
                    ef_construct=100
                ),
                optimizers_config=models.OptimizersConfigDiff(
                    indexing_threshold=0
                )
            )
            print(f"Created Qdrant collection: {COLLECTION_NAME}")
        else:
            print(f"Qdrant collection {COLLECTION_NAME} already exists")
    except Exception as e:
        print(f"Error initializing Qdrant collection: {e}")
        raise

def add_campaign_to_vector_store(campaign_id, campaign_name, product_type, target_audience, target_problem, 
                                unique_solution, reason_why_needed, main_benefits, social_proof, price, 
                                offer, urgency, cta):
    """
    Add a campaign's details to the Qdrant vector store.
    """
    initialize_vector_store()  # Ensure collection is ready
    text = (f"{campaign_name}. {product_type}. {target_audience}. {target_problem}. {unique_solution}. "
            f"{reason_why_needed}. {main_benefits}. {social_proof}. {price}. {offer}. {urgency}. {cta}.")
    embedding = embedding_model.encode([text]).tolist()[0]
    
    qdrant_client.upsert(
        collection_name=COLLECTION_NAME,
        points=[
            models.PointStruct(
                id=campaign_id,
                vector=embedding,
                payload={
                    "campaign_name": campaign_name,
                    "product_type": product_type,
                    "target_audience": target_audience,
                    "target_problem": target_problem,
                    "unique_solution": unique_solution,
                    "reason_why_needed": reason_why_needed,
                    "main_benefits": main_benefits,
                    "social_proof": social_proof,
                    "price": price,
                    "offer": offer,
                    "urgency": urgency,
                    "cta": cta
                }
            )
        ]
    )
    print(f"Added campaign {campaign_id} to Qdrant vector store.")

def search_campaigns(query, top_k=3):
    """
    Search for the top-k most similar campaigns based on a query.
    """
    embedding = embedding_model.encode([query]).tolist()[0]
    try:
        search_result = qdrant_client.search(
            collection_name=COLLECTION_NAME,
            query_vector=embedding,
            limit=top_k
        )
        return [hit.payload for hit in search_result]
    except Exception as e:
        print(f"Error searching Qdrant: {e}")
        return []