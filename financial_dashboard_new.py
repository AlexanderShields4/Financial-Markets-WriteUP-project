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
    with open(f"{today}dailywriteup.txt", 'r') as f:
        daily_writeup = f.read()
except FileNotFoundError:
    daily_writeup = "Daily writeup not available for today."

# Header
st.markdown('<p class="market-header">📊 Daily Market Newsletter</p>', unsafe_allow_html=True)
st.markdown(f"*{datetime.now().strftime('%B %d, %Y')}*")

# Daily Analysis Section
st.markdown('<p class="section-header">Today\'s Market Analysis</p>', unsafe_allow_html=True)
st.write(daily_writeup)

# Major Indices Section
st.markdown('<p class="section-header">Major Market Indices</p>', unsafe_allow_html=True)
indices_data = market_data['indice_data_str'].split('. ')
for index in indices_data:
    if index:  # Skip empty strings
        st.markdown(f"**{index}**")

# Economic Indicators Section
if 'economic_indicators' in market_data:
    st.markdown('<p class="section-header">Economic Indicators</p>', unsafe_allow_html=True)
    for indicator, value in market_data['economic_indicators'].items():
        st.markdown(f"**{indicator}:** {value}")

# News Headlines Section
st.markdown('<p class="section-header">Latest Market News</p>', unsafe_allow_html=True)
news_data = market_data['newsstr'].split('\n')
for news_item in news_data[2:7]:  # Skip header and show top 5 headlines
    if news_item.strip():
        st.markdown(f"📰 {news_item}")
