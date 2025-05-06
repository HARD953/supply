import matplotlib.pyplot as plt
import pandas as pd
import requests
import seaborn as sns
import numpy as np
from datetime import datetime
import os

# Configuration
API_URL = "http://localhost:8000/api/statistiques/"
TOKEN = "your_jwt_token_here"  # Remplace par un token JWT valide
OUTPUT_DIR = "stats_plots"

def fetch_stats(endpoint, period='month', params=None):
    headers = {"Authorization": f"Bearer {TOKEN}"}
    params = params or {}
    params['period'] = period
    response = requests.get(f"{API_URL}{endpoint}", params=params, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch data: {response.text}")
    return response.json()

def plot_orders_by_period(data, period='month'):
    df = pd.DataFrame(data['orders_by_period'])
    df['period'] = pd.to_datetime(df['period'])
    plt.figure(figsize=(10, 6))
    plt.plot(df['period'], df['count'], marker='o', label='Nombre de commandes')
    plt.plot(df['period'], df['total_value'], marker='s', label='Valeur totale (€)')
    # Prévision (moyenne mobile)
    df['count_ma'] = df['count'].rolling(window=3).mean()
    plt.plot(df['period'], df['count_ma'], linestyle='--', label='Moyenne mobile (commandes)')
    plt.title(f"Évolution des commandes par {'mois' if period == 'month' else 'jour' if period == 'day' else 'année'}")
    plt.xlabel("Période")
    plt.ylabel("Valeur")
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/orders_by_{period}.png")
    plt.close()

def plot_shops_by_type(data):
    df = pd.DataFrame(data['shops_by_type'])
    plt.figure(figsize=(8, 8))
    plt.pie(df['count'], labels=df['type'], autopct='%1.1f%%', startangle=140)
    centre_circle = plt.Circle((0, 0), 0.70, fc='white')
    fig = plt.gcf()
    fig.gca().add_artist(centre_circle)
    plt.title("Répartition des boutiques par type")
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/shops_by_type_donut.png")
    plt.close()

def plot_shops_heatmap(data):
    df = pd.DataFrame([
        {'latitude': shop['latitude'], 'longitude': shop['longitude'], 'count': shop['count']}
        for shop in data['shops_by_zone']
    ])
    plt.figure(figsize=(10, 8))
    sns.kdeplot(data=df, x='longitude', y='latitude', weights='count', cmap='Reds', fill=True)
    plt.title("Heatmap des boutiques par zone géographique")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/shops_heatmap.png")
    plt.close()

if __name__ == "__main__":
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    # Commandes par période
    order_data = fetch_stats("orders/", period='month')
    plot_orders_by_period(order_data, period='month')
    # Répartition des boutiques
    shop_data = fetch_stats("shops/")
    plot_shops_by_type(shop_data)
    # Heatmap géographique
    plot_shops_heatmap(shop_data)