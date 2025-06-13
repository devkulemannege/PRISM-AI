import faiss
import pickle
from sentence_transformers import SentenceTransformer
import numpy as np


def find_relevant_campaign(text, faiss_index_path="Master/campaign_vector.index", meta_path="Master/campaign_vector_meta.pkl"):
    # Load FAISS index and metadata
    faiss_index = faiss.read_index(faiss_index_path)
    with open(meta_path, "rb") as f:
        campaign_meta = pickle.load(f)  # List of dicts or objects

    # Encode the user message
    model = SentenceTransformer('all-mpnet-base-v2')
    user_vec = model.encode([text])
    if user_vec.ndim == 1:
        user_vec = np.expand_dims(user_vec, axis=0)
    print("Query vector shape:", user_vec.shape)
    print("FAISS index dimension:", faiss_index.d)

    # Search for the most similar campaign
    D, I = faiss_index.search(user_vec, k=1)
    best_idx = I[0][0]
    best_campaign = campaign_meta[best_idx]
    return best_campaign

if __name__ == "__main__":
    text = input("Enter a user message: ")
    campaign = find_relevant_campaign(text, "Master/campaign_vector.index", "Master/campaign_vector_meta.pkl")
    print("Most relevant campaign found:")
    print(campaign)


#