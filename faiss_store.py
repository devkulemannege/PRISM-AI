"""
Module to create and manage a simple vector store for campaign details using FAISS and sentence-transformers.
"""
import os
import pickle
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np


#
VECTOR_DB_PATH = os.path.join(os.path.dirname(__file__), 'campaign_vector.index')
META_DB_PATH = os.path.join(os.path.dirname(__file__), 'campaign_vector_meta.pkl')



# Load or initialize the embedding model
EMBEDDING_MODEL = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')

# Helper to load or create FAISS index and metadata

def load_vector_store():
    """"Load the vector store from disk or create a new one if it doesn't exist."""
    if os.path.exists(VECTOR_DB_PATH) and os.path.exists(META_DB_PATH):
        index = faiss.read_index(VECTOR_DB_PATH)
        with open(META_DB_PATH, 'rb') as f:
            meta = pickle.load(f)
    else:
        index = faiss.IndexFlatL2(EMBEDDING_MODEL.get_sentence_embedding_dimension())# Create a new index
        meta = []
    return index, meta

def save_vector_store(index, meta):
    faiss.write_index(index, VECTOR_DB_PATH)
    with open(META_DB_PATH, 'wb') as f:
        pickle.dump(meta, f)

def add_campaign_to_vector_store(campaign_id, campaign_name, product_type, target_audience,target_problem,unique_solution,reason_why_needed,main_benefits,social_proof,price,offer,urgency,cta):
    """
    Add a campaign's details to the vector store.
    extra_fields: dict of any additional fields to concatenate for embedding.
    """
    index, meta = load_vector_store()
    # Concatenate all text fields for embedding
    text = f"{campaign_name}. {product_type}. {target_audience}. {target_problem}. {unique_solution}. {reason_why_needed}. {main_benefits}. {social_proof}. {price}. {offer}. {urgency}. {cta}."
    embedding = EMBEDDING_MODEL.encode([text])
    index.add(embedding)
    meta.append({
        'campaign_id': campaign_id,
        'campaign_name': campaign_name,
        'product_type': product_type,
        'target_audience': target_audience,
        'target_problem': target_problem,
        'unique_solution': unique_solution,
        'reason_why_needed': reason_why_needed,
        'main_benefits': main_benefits,
        'social_proof': social_proof,
        'price': price,
        'offer': offer,
        'urgency': urgency,
        'cta': cta
    })
    save_vector_store(index, meta)
    print(f"Added campaign {campaign_id} to vector store.")

def search_campaigns(query, top_k=3):
    index, meta = load_vector_store()
    embedding = EMBEDDING_MODEL.encode([query])
    if index.ntotal == 0:
        return []
    D, I = index.search(embedding, top_k)
    return [meta[i] for i in I[0] if i < len(meta)]

def find_relevant_campaign(text, faiss_index_path="Master/campaign_vector.index", meta_path="Master/campaign_vector_meta.pkl"):
    # Robust: Check if index file exists
    if not os.path.exists(faiss_index_path) or not os.path.exists(meta_path):
        print(f"[FAISS] Index or meta file not found: {faiss_index_path}, {meta_path}")
        return None  # Or return a default value, or raise a user-friendly error
    # Load FAISS index and metadata
    faiss_index = faiss.read_index(faiss_index_path)
    with open(meta_path, "rb") as f:
        print(f)
        campaign_meta = pickle.load(f)  # List of dicts or objects

    # Use the global embedding model for consistency
    user_vec = EMBEDDING_MODEL.encode([text])
    if user_vec.ndim == 1:
        user_vec = np.expand_dims(user_vec, axis=0)  # Ensure user_vec is 2D

    # Search for the most similar campaign
    D, I = faiss_index.search(user_vec, k=1)
    best_idx = I[0][0]
    best_dist = D[0][0]
    print(f"Best campaign index: {best_idx}, distance: {best_dist}")
    # Set a reasonable threshold for L2 distance (tune as needed)
    threshold = 4.0
    if best_idx < len(campaign_meta) and best_dist < threshold:
        print("Best campaign meta:", campaign_meta[best_idx]['campaign_id'])
        return campaign_meta[best_idx]['campaign_id']
    
text="I want mangoes"
campaign_id = find_relevant_campaign(text, "Master/campaign_vector.index", "Master/campaign_vector_meta.pkl") 
print(f"Most relevant campaign found: {campaign_id}")