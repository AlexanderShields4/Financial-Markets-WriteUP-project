import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json
from datetime import datetime
import plotly.express as px
import re

# Page config
st.set_page_config(
    page_title="Financial Markets Dashboard",
    page_icon="📈",
    layout="wide"
)

# Custom CSS to improve appearance
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stPlotlyChart {
        background-color: #ffffff;
        border-radius: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.title("📊 Financial Markets Daily Dashboard")
st.markdown(f"*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")

# Load data
try:
    with open('market_data.json', 'r') as f:
        data = json.load(f)
except FileNotFoundError:
    st.error("Data file not found. Please run the notebook first to generate the data.")
    st.stop()

col1, col2 = st.columns(2)

with col1:
    # Treasury Yield Spread
    st.header("10Y-2Y Treasury Spread")
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

# Main content layout
col1, col2 = st.columns([2, 1])

with col1:
    # Daily Analysis Section
    st.markdown('<p class="section-header">Today\'s Market Analysis</p>', unsafe_allow_html=True)
    st.write(daily_writeup)

with col2:
    # Key Market Indicators
    st.markdown('<p class="section-header">Key Market Indicators</p>', unsafe_allow_html=True)
    
    # Process 10Y-2Y spread data
    spread_data = []
    for entry in market_data['tenyrtwoyr']:
        date, value = entry.split(': ')
        spread_data.append({'Date': datetime.strptime(date, '%Y-%m-%d'), 'Spread': float(value)})
    spread_df = pd.DataFrame(spread_data)
    
    # Create 10Y-2Y spread chart
    fig_spread = px.line(spread_data, 
                        x='Date', 
                        y='Spread',
                        title='10Y-2Y Treasury Spread',
                        labels={'Spread': 'Spread (%)', 'Date': 'Date'})
    fig_spread.update_layout(height=300)
    st.plotly_chart(fig_spread, use_container_width=True)

# Major Indices Section
st.markdown('<p class="section-header">Major Market Indices</p>', unsafe_allow_html=True)
indices_col1, indices_col2 = st.columns(2)

with indices_col1:
    # Display indices data in a clean format
    st.markdown("### Current Index Values")
    indices_data = market_data['indice_data_str'].split('. ')
    for index in indices_data:
        if index:  # Skip empty strings
            st.markdown(f"**{index}**")

# Economic Releases Section
st.markdown('<p class="section-header">Economic Calendar</p>', unsafe_allow_html=True)
releases_data = market_data['weekly_releases']
if releases_data:
    for release in releases_data[:5]:  # Show only top 5 releases
        st.markdown(f"• {release}")

# News Headlines Section
st.markdown('<p class="section-header">Latest Market News</p>', unsafe_allow_html=True)
news_data = market_data['newsstr'].split('\n')
for news_item in news_data[2:7]:  # Skip header and show top 5 headlines
    if news_item.strip():
        st.markdown(f"📰 {news_item}")

# Magnificent 7 Section
st.markdown('<p class="section-header">Magnificent 7 Performance</p>', unsafe_allow_html=True)
mag7_data = market_data['ticker_data'].split('. ')
col1, col2 = st.columns(2)
for i, stock_data in enumerate(mag7_data):
    if stock_data.strip():
        if i % 2 == 0:
            col1.markdown(f"**{stock_data}**")
        else:
            col2.markdown(f"**{stock_data}**")
        spread_data = pd.DataFrame([
            tuple(item.split(': ')) for item in data['tenyrtwoyr']
        ], columns=['Date', 'Spread'])
        spread_data['Spread'] = spread_data['Spread'].astype(float)
    fig = px.line(spread_data, x='Date', y='Spread',
             title='10Y-2Y Treasury Spread Trend')
    fig.update_layout(yaxis_title='Spread (%)')
    st.plotly_chart(fig, use_container_width=True, key="spread_trend")

with col2:
    # Major Indices Performance (robust parsing using regex)
    st.header("Major Indices Performance")
    if 'indice_data_str' in data:
        indices_str = data['indice_data_str'].strip()
        # split on sentences ending with a period
        indices_list = [s.strip() for s in re.split(r'\.\s*', indices_str) if s.strip()]
        indices_data = []
        index_names = {
            '^GSPC': 'S&P 500',
            '^DJI': 'Dow Jones',
            '^IXIC': 'NASDAQ',
            '^RUT': 'Russell 2000'
        }

        # regex: symbol : Open: <num> Close: <num>
        idx_re = re.compile(r'(?P<symbol>\^\w+)\s*:\s*Open:\s*(?P<open>[\d,\.]+)\s*Close:\s*(?P<close>[\d,\.]+)', re.IGNORECASE)
        for idx in indices_list:
            m = idx_re.search(idx)
            if not m:
                st.warning(f"Could not parse index line: {idx}")
                continue
            symbol = m.group('symbol')
            open_price = float(m.group('open').replace(',', ''))
            close_price = float(m.group('close').replace(',', ''))
            change_pct = ((close_price - open_price) / open_price) * 100
            display_name = index_names.get(symbol, symbol)
            indices_data.append({
                'Index': display_name,
                'Open': open_price,
                'Close': close_price,
                'Change %': change_pct
            })

        if indices_data:
            df_indices = pd.DataFrame(indices_data)
            fig = go.Figure(data=[
                go.Bar(name='Change %',
                      x=df_indices['Index'],
                      y=df_indices['Change %'],
                      marker_color=['red' if x < 0 else 'green' for x in df_indices['Change %']])
            ])
            fig.update_layout(title='Daily Performance (%)')
            st.plotly_chart(fig, use_container_width=True, key="indices_change_chart")
        else:
            st.info("No index data available to display.")

# Magnificent 7 Performance (robust regex parsing)
st.header("Magnificent 7 Performance")
if 'ticker_data' in data:
    ticker_str = data['ticker_data'].strip()
    # split into sentences (each stock entry ends with a period)
    stock_lines = [s.strip() for s in re.split(r'\.\s*', ticker_str) if s.strip()]
    mag7_data = []

    # regex: SYMBOL YYYY-MM-DD: Open: $<num> Close: $<num>
    stock_re = re.compile(
        r'(?P<symbol>[A-Z0-9\.\-]+)\s+(?P<date>\d{4}-\d{2}-\d{2})\s*:\s*Open:\s*\$(?P<open>[\d,\.]+)\s*Close:\s*\$(?P<close>[\d,\.]+)',
        re.IGNORECASE
    )

    for stock in stock_lines:
        m = stock_re.search(stock)
        if not m:
            # warn but don't break the page
            st.warning(f"Could not parse ticker line: {stock}")
            continue
        symbol = m.group('symbol').upper()
        open_price = float(m.group('open').replace(',', ''))
        close_price = float(m.group('close').replace(',', ''))
        change_pct = ((close_price - open_price) / open_price) * 100
        mag7_data.append({
            'Stock': symbol,
            'Open': open_price,
            'Close': close_price,
            'Change %': change_pct
        })

    if mag7_data:
        df_mag7 = pd.DataFrame(mag7_data)
        fig = go.Figure(data=[
            go.Bar(name='Change %',
                   x=df_mag7['Stock'],
                   y=df_mag7['Change %'],
                   marker_color=['red' if x < 0 else 'green' for x in df_mag7['Change %']])
        ])
        fig.update_layout(title='Daily Performance (%)')
        st.plotly_chart(fig, use_container_width=True, key="mag7_change_chart")
    else:
        st.info("No ticker data parsed.")

# Economic Releases
st.header("Economic Releases")
if 'weekly_releases' in data:
    # weekly_releases might be a list; join to a string with line breaks
    if isinstance(data['weekly_releases'], list):
        releases_text = '\n'.join(data['weekly_releases'])
    else:
        releases_text = str(data['weekly_releases'])
    # Replace '  ' or '. ' if you want double spacing; keep it readable
    st.markdown(releases_text.replace('. ', '  \n'))

# News Headlines
st.header("📰 Latest Market News")
if 'newsstr' in data:
    # split into lines, skip empty lines and any non-item header
    news_lines = [line.strip() for line in data['newsstr'].splitlines() if line.strip()]
    # remove a header line if present (like "📐 Broad Market News ...")
    if news_lines and ('Broad Market News' in news_lines[0] or news_lines[0].startswith('•') is False):
        # keep everything from the first actual numbered/interesting item
        # we'll display all lines but you can filter further if you want
        pass
    for item in news_lines:
        st.markdown(f"• {item}")
