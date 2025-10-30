import streamlit as st
import json
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import plotly.express as px
import re

# Set page config
st.set_page_config(
    page_title="Daily Market Newsletter",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
        max-width: 1400px;
        margin: 0 auto;
    }
    .market-header {
        font-size: 2.8rem;
        font-weight: bold;
        background: linear-gradient(45deg, #1E3D59, #2E5077);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1.5rem;
        text-align: center;
    }
    .section-header {
        font-size: 1.8rem;
        color: #2E5077;
        margin-top: 2rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #e6e6e6;
        padding-bottom: 0.5rem;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 0.5rem;
    }
    .news-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #2E5077;
        margin-bottom: 0.8rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    .highlight {
        color: #2E5077;
        font-weight: bold;
    }
    .ticker-up {
        color: #28a745;
        font-weight: bold;
    }
    .ticker-down {
        color: #dc3545;
        font-weight: bold;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
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

# Header with Animation
st.markdown('<p class="market-header">📊 Market Intelligence Dashboard</p>', unsafe_allow_html=True)
st.markdown(f"<h3 style='text-align: center; color: #666;'>{datetime.now().strftime('%B %d, %Y')}</h3>", unsafe_allow_html=True)

# Create columns for the layout
col1, col2 = st.columns([2, 1])

with col1:
    # Main Analysis Section
    st.markdown('<p class="section-header">📈 Market Analysis</p>', unsafe_allow_html=True)
    st.write(daily_writeup)

with col2:
    # Key Metrics Section
    st.markdown('<p class="section-header">🎯 Key Market Indicators</p>', unsafe_allow_html=True)
    
    # Parse and display market indices
    indices_data = market_data['indice_data_str'].split('.')
    for idx in indices_data:
        if 'S&P 500' in idx or 'VIX' in idx or 'Gold' in idx:
            parts = idx.strip().split(':')
            if len(parts) >= 2:
                name = parts[0]
                values = parts[1].split('Close')
                if len(values) >= 2:
                    close_val = float(values[1].strip())
                    st.metric(
                        label=name,
                        value=f"${close_val:,.2f}" if 'VIX' not in name else f"{close_val:.2f}",
                        delta=None  # You could calculate daily change here
                    )

    # Treasury Spread Visualization
    st.markdown('<p class="section-header">📉 Treasury Spread</p>', unsafe_allow_html=True)
    spread_data = market_data['tenyrtwoyr']
    dates = []
    values = []
    for item in spread_data:
        date_str, value_str = item.split(':')
        dates.append(pd.to_datetime(date_str))
        values.append(float(value_str))
    
    df = pd.DataFrame({'Date': dates, 'Spread': values})
    fig = px.line(df, x='Date', y='Spread', 
                  title='10Y-2Y Treasury Spread',
                  template='plotly_white')
    fig.update_traces(line_color='#2E5077', line_width=2)
    fig.update_layout(
        height=300,
        margin=dict(l=0, r=0, t=30, b=0),
        plot_bgcolor='white'
    )
    st.plotly_chart(fig, use_container_width=True, key='treasury_spread')

# News Headlines Section with enhanced styling
st.markdown('<p class="section-header">📰 Latest Market News</p>', unsafe_allow_html=True)
news_data = market_data['newsstr'].split('\n')

# Create three columns for news
news_cols = st.columns(3)
col_idx = 0

for news_item in news_data[2:11]:  # Show top 9 headlines
    if news_item.strip():
        # Extract the news number, title, and source using regex
        match = re.match(r'(\d+)\.\s(.*?)\s+Source:\s(.*?)\s+URL:', news_item)
        if match:
            num, title, source = match.groups()
            with news_cols[col_idx % 3]:
                st.markdown(f"""
                    <div class="news-card">
                        <small style="color: #666;">{source}</small>
                        <p style="margin: 0.5rem 0;">{title}</p>
                    </div>
                """, unsafe_allow_html=True)
            col_idx += 1

# Economic Indicators Section
st.markdown('<p class="section-header">📊 Economic Indicators</p>', unsafe_allow_html=True)
if 'economic_indicators' in market_data:
    indicator_cols = st.columns(4)
    for idx, (indicator, value) in enumerate(market_data['economic_indicators'].items()):
        with indicator_cols[idx % 4]:
            st.markdown(f"""
                <div class="metric-card">
                    <h4 style="margin: 0; color: #666;">{indicator}</h4>
                    <p style="font-size: 1.2rem; margin: 0.5rem 0; color: #2E5077;">{value.split(':')[1]}</p>
                    <small style="color: #999;">{value.split(':')[0]}</small>
                </div>
            """, unsafe_allow_html=True)

# Footer
st.markdown("""
    <div style="text-align: center; margin-top: 2rem; padding: 1rem; background: #f8f9fa; border-radius: 10px;">
        <small style="color: #666;">Data updated daily at market close (4:45 PM ET)</small>
    </div>
""", unsafe_allow_html=True)
