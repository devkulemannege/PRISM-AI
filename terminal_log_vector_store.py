import subprocess
import threading
import time
import os
import faiss
import pickle
from sentence_transformers import SentenceTransformer
import numpy as np
from datetime import datetime

# Vector store paths
VECTOR_DB_PATH = os.path.join(os.path.dirname(__file__), 'terminal_log_vector.index')
META_DB_PATH = os.path.join(os.path.dirname(__file__), 'terminal_log_vector_meta.pkl')

EMBEDDING_MODEL = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')

# Load or create FAISS index and metadata
def load_vector_store():
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

def embed_and_store(message, msg_type, index, meta):
    embedding = EMBEDDING_MODEL.encode([message])
    index.add(np.array(embedding, dtype=np.float32))
    meta.append({
        'timestamp': datetime.now().isoformat(),
        'type': msg_type,
        'message': message
    })
    save_vector_store(index, meta)

def stream_and_vectorize(cmd):
    index, meta = load_vector_store()
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)

    def handle_stream(stream, msg_type):
        for line in iter(stream.readline, ''):
            print(line, end='')  # Still print to this terminal
            embed_and_store(line.strip(), msg_type, index, meta)
        stream.close()

    threads = [
        threading.Thread(target=handle_stream, args=(process.stdout, 'stdout')),
        threading.Thread(target=handle_stream, args=(process.stderr, 'stderr')),
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    process.wait()

if __name__ == '__main__':
    print("[Terminal Log Vector Store] Launching app.py and tracking all terminal output...")
    stream_and_vectorize(['python', 'app.py'])
    print("[Terminal Log Vector Store] Finished.")
