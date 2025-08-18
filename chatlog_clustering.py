# Unsupervised clustering of users based on chatlog customer_msg texts
# Requirements: pip install scikit-learn pandas nltk
# For better results: pip install sentence-transformers

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import mysql.connector
import nltk
from nltk.corpus import stopwords
import re

# Uncomment if using BERT embeddings
# from sentence_transformers import SentenceTransformer

nltk.download('stopwords')
STOPWORDS = set(stopwords.words('english'))

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', '', text)
    tokens = text.split()
    tokens = [t for t in tokens if t not in STOPWORDS]
    return ' '.join(tokens)

def fetch_chatlog_msgs():
    # Update with your DB credentials
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='prismaimaster'
    )
    df = pd.read_sql("SELECT customerId, customer_msg FROM chatlog WHERE customer_msg IS NOT NULL AND customer_msg != ''", conn)
    conn.close()
    return df

def cluster_messages(df, n_clusters=5):
    df['clean_msg'] = df['customer_msg'].apply(clean_text)
    # TF-IDF vectorization
    vectorizer = TfidfVectorizer(max_features=200)
    X = vectorizer.fit_transform(df['clean_msg'])
    # For BERT embeddings, use:
    # model = SentenceTransformer('all-MiniLM-L6-v2')
    # X = model.encode(df['customer_msg'].tolist())
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    df['cluster'] = kmeans.fit_predict(X)
    return df, kmeans

def main():
    df = fetch_chatlog_msgs()
    if df.empty:
        print('No customer messages found.')
        return
    clustered_df, kmeans = cluster_messages(df, n_clusters=5)
    print('Clustered messages:')
    print(clustered_df[['customerId', 'customer_msg', 'cluster']].head(20))
    # To analyze what each cluster is about:
    for i in range(5):
        print(f'\nCluster {i} example messages:')
        print(clustered_df[clustered_df['cluster'] == i]['customer_msg'].head(5).to_list())

if __name__ == '__main__':
    main()
