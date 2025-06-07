"""
Module to create and manage a simple vector store for campaign details using FAISS and sentence-transformers.
"""
import os
import pickle
from sentence_transformers import SentenceTransformer
import faiss


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
        index = faiss.IndexFlatL2(EMBEDDING_MODEL.get_sentence_embedding_dimension())
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
