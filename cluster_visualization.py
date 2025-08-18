# Visualize chatlog clusters in 2D with customer names and messages
# Requirements: pip install matplotlib scikit-learn pandas nltk

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import mysql.connector
import nltk
from nltk.corpus import stopwords
import re
import os
nltk.download('stopwords', quiet=True)
STOPWORDS = set(stopwords.words('english'))

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', '', text)
    tokens = text.split()
    tokens = [t for t in tokens if t not in STOPWORDS]
    return ' '.join(tokens)

def fetch_chatlog_msgs_for_business(business_id):
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='prism_ai_database_new'
    )
    query = '''
        SELECT ch.customerId, cu.fName, ch.customer_msg
        FROM chatlog ch
        LEFT JOIN customer cu ON ch.customerId = cu.customerId
        JOIN campaign ca ON ch.CampaignId = ca.campaignId
        WHERE ch.customer_msg IS NOT NULL AND ch.customer_msg != '' AND ca.businessId = %s
    '''
    df = pd.read_sql(query, conn, params=(business_id,))
    conn.close()
    return df

def fetch_all_chatlog_msgs():
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='prismaimaster'
    )
    query = '''
        SELECT ch.customerId, cu.fName, ch.customer_msg
        FROM chatlog ch
        LEFT JOIN customer cu ON ch.customerId = cu.customerId
        WHERE ch.customer_msg IS NOT NULL AND ch.customer_msg != ''
    '''
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def cluster_and_reduce(df, n_clusters=5):
    df['clean_msg'] = df['customer_msg'].apply(clean_text)
    vectorizer = TfidfVectorizer(max_features=200)
    X = vectorizer.fit_transform(df['clean_msg'])
    n_samples = X.shape[0]
    if n_samples < 2:
        # Not enough data to cluster
        return None
    n_clusters = min(n_clusters, n_samples)
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    df['cluster'] = kmeans.fit_predict(X)
    pca = PCA(n_components=2)
    coords = pca.fit_transform(X.toarray())
    df['x'] = coords[:,0]
    df['y'] = coords[:,1]
    return df

def save_cluster_plot(df, img_path):
    plt.figure(figsize=(12,8))
    colors = plt.cm.get_cmap('tab10', df['cluster'].nunique())
    for cluster in sorted(df['cluster'].unique()):
        cluster_df = df[df['cluster'] == cluster]
        plt.scatter(cluster_df['x'], cluster_df['y'], label=f'Cluster {cluster}', alpha=0.6, s=80, color=colors(cluster))
        for _, row in cluster_df.iterrows():
            label = f"{row['fName'] or 'Unknown'}: {row['customer_msg'][:25]}"
            plt.text(row['x'], row['y'], label, fontsize=8, alpha=0.8)
    plt.title('Customer Message Clusters')
    plt.xlabel('PCA 1')
    plt.ylabel('PCA 2')
    plt.legend()
    plt.tight_layout()
    plt.savefig(img_path)
    plt.close()

# If run as script, show plot for any business_id
if __name__ == '__main__':
    business_id = int(input('Enter businessId: '))
    df = fetch_chatlog_msgs_for_business(business_id)
    if df.empty:
        print('No customer messages found.')
    else:
        df = cluster_and_reduce(df, n_clusters=5)
        if df is not None:
            save_cluster_plot(df, 'sales_clusters.png')
            print('Cluster plot saved as sales_clusters.png')
        else:
            print('Not enough data to perform clustering.')
