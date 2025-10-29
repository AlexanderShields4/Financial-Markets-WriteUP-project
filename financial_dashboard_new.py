import streamlit as st
import json
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import plotly.express as px

# Set page config
st.set_page_config(
    page_title="Daily Market Newsletter",
    page_icon="📈",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
        max-width: 1200px;
        margin: 0 auto;
    }
    .market-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E3D59;
        margin-bottom: 1.5rem;
    }
    .section-header {
        font-size: 1.8rem;
        color: #2E5077;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

# Load market data
try:
    with open('market_data.json', 'r') as f:
        market_data = json.load(f)
except FileNotFoundError:
    st.error("Market data file not found. Please run the data collection script first.")
    st.stop()

# Load the daily writeup
try:
    today = datetime.now().strftime("%Y-%m-%d")
    filepath = f"Daily_write_ups/{today}dailywriteup.txt"
    with open(filepath, 'r') as f:
        daily_writeup = f.read()
except FileNotFoundError:
    daily_writeup = "Daily writeup not available for today."

# Header
st.markdown('<p class="market-header">📊 Daily Market Newsletter</p>', unsafe_allow_html=True)
st.markdown(f"*{datetime.now().strftime('%B %d, %Y')}*")

# Daily Analysis Section
st.markdown('<p class="section-header">Today\'s Market Analysis</p>', unsafe_allow_html=True)
st.write(daily_writeup)

# News Headlines Section
st.markdown('<p class="section-header">News Highlights</p>', unsafe_allow_html=True)
news_data = market_data['newsstr'].split('\n')
for news_item in news_data[2:12]:  # Skip header and show top 10 headlines
    if news_item.strip():
        st.markdown(f"📰 {news_item}")
