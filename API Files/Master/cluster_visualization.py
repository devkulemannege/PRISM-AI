# Visualize chatlog clusters in 2D with customer names and messages
# Requirements: pip install matplotlib scikit-learn pandas nltk

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import mysql.connector
import nltk
from nltk.corpus import stopwords
import re

nltk.download('stopwords')
STOPWORDS = set(stopwords.words('english'))

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', '', text)
    tokens = text.split()
    tokens = [t for t in tokens if t not in STOPWORDS]
    return ' '.join(tokens)

def fetch_chatlog_msgs():
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='prism_ai_database_new'
    )
    df = pd.read_sql("""
        SELECT ch.customerId, cu.fName, ch.customer_msg
        FROM chatlog ch
        LEFT JOIN customer cu ON ch.customerId = cu.customerId
        WHERE ch.customer_msg IS NOT NULL AND ch.customer_msg != ''
    """, conn)
    conn.close()
    return df

def cluster_and_reduce(df, n_clusters=5):
    df['clean_msg'] = df['customer_msg'].apply(clean_text)
    vectorizer = TfidfVectorizer(max_features=200)
    X = vectorizer.fit_transform(df['clean_msg'])
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    df['cluster'] = kmeans.fit_predict(X)
    # Reduce to 2D for visualization
    pca = PCA(n_components=2)
    coords = pca.fit_transform(X.toarray())
    df['x'] = coords[:,0]
    df['y'] = coords[:,1]
    return df, kmeans

def plot_clusters(df):
    plt.figure(figsize=(12,8))
    colors = plt.cm.get_cmap('tab10', df['cluster'].nunique())
    for cluster in sorted(df['cluster'].unique()):
        cluster_df = df[df['cluster'] == cluster]
        plt.scatter(cluster_df['x'], cluster_df['y'], label=f'Cluster {cluster}', alpha=0.6, s=80, color=colors(cluster))
        for _, row in cluster_df.iterrows():
            label = f"{row['fName'] or 'Unknown'}: {row['customer_msg'][:25]}"  # Name and short msg
            plt.text(row['x'], row['y'], label, fontsize=8, alpha=0.8)
    plt.title('Customer Message Clusters')
    plt.xlabel('PCA 1')
    plt.ylabel('PCA 2')
    plt.legend()
    plt.tight_layout()
    plt.show()

def main():
    df = fetch_chatlog_msgs()
    if df.empty:
        print('No customer messages found.')
        return
    clustered_df, kmeans = cluster_and_reduce(df, n_clusters=5)
    plot_clusters(clustered_df)

if __name__ == '__main__':
    main()
