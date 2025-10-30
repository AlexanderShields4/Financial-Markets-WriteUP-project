import streamlit as st
import json
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import plotly.express as px

# Theme configurations
THEMES = {
    "Classic": {
        "primary": "#1E3D59",
        "secondary": "#2E5077",
        "background": "#FFFFFF",
        "text": "#000000",
        "accent": "#FF6B6B"
    },
    "Dark Mode": {
        "primary": "#BB86FC",
        "secondary": "#03DAC6",
        "background": "#121212",
        "text": "#FFFFFF",
        "accent": "#CF6679"
    },
    "Forest": {
        "primary": "#2D5A27",
        "secondary": "#4A8744",
        "background": "#F5F9F5",
        "text": "#1C1C1C",
        "accent": "#FF7F50"
    },
    "Ocean": {
        "primary": "#006994",
        "secondary": "#0099CC",
        "background": "#F0F8FF",
        "text": "#00334E",
        "accent": "#FF8C00"
    }
}

# Set page config
st.set_page_config(
    page_title="Daily Market Newsletter",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar for customization
with st.sidebar:
    st.title("💠 Dashboard Settings")
    
    # Theme selection
    selected_theme = st.selectbox(
        "Select Theme",
        options=list(THEMES.keys()),
        index=0
    )
    
    # Font size adjustment
    font_scale = st.slider(
        "Text Size",
        min_value=0.8,
        max_value=1.4,
        value=1.0,
        step=0.1
    )
    
    # Layout options
    st.subheader("Layout Options")
    show_timestamps = st.checkbox("Show Timestamps", value=True)
    compact_mode = st.checkbox("Compact Mode", value=False)
    show_news_sources = st.checkbox("Show News Sources", value=True)
    
    # News filter
    st.subheader("News Filters")
    news_categories = st.multiselect(
        "Filter News Categories",
        ["Markets", "Economy", "Companies", "Commodities", "Currencies"],
        default=["Markets", "Economy"]
    )
    
    max_headlines = st.slider(
        "Number of Headlines",
        min_value=5,
        max_value=20,
        value=10
    )

# Generate dynamic CSS based on selected theme
theme = THEMES[selected_theme]
st.markdown(f"""
    <style>
    :root {{
        --primary-color: {theme["primary"]};
        --secondary-color: {theme["secondary"]};
        --background-color: {theme["background"]};
        --text-color: {theme["text"]};
        --accent-color: {theme["accent"]};
        --font-scale: {font_scale};
    }}
    
    .main {{
        padding: 2rem;
        max-width: {1200 if not compact_mode else 800}px;
        margin: 0 auto;
        background-color: var(--background-color);
        color: var(--text-color);
    }}
    
    .market-header {{
        font-size: calc(2.5rem * var(--font-scale));
        font-weight: bold;
        color: var(--primary-color);
        margin-bottom: 1.5rem;
        padding: 1rem;
        border-bottom: 3px solid var(--accent-color);
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }}
    
    .section-header {{
        font-size: calc(1.8rem * var(--font-scale));
        color: var(--secondary-color);
        margin-top: 2rem;
        margin-bottom: 1rem;
        padding: 0.5rem 0;
        border-bottom: 2px solid var(--secondary-color);
    }}
    
    .news-item {{
        padding: 0.8rem;
        margin: 0.5rem 0;
        border-left: 3px solid var(--accent-color);
        background: {"rgba(0,0,0,0.05)" if selected_theme != "Dark Mode" else "rgba(255,255,255,0.05)"};
        transition: all 0.3s ease;
    }}
    
    .news-item:hover {{
        transform: translateX(5px);
        border-left-width: 5px;
    }}
    
    .timestamp {{
        font-size: calc(0.8rem * var(--font-scale));
        color: var(--secondary-color);
        font-style: italic;
    }}
    
    .source-tag {{
        display: inline-block;
        padding: 2px 8px;
        border-radius: 12px;
        background-color: var(--secondary-color);
        color: var(--background-color);
        font-size: calc(0.7rem * var(--font-scale));
        margin-left: 8px;
    }}
    
    .market-content {{
        font-size: calc(1rem * var(--font-scale));
        line-height: 1.6;
        padding: 1rem;
        background: {"rgba(0,0,0,0.02)" if selected_theme != "Dark Mode" else "rgba(255,255,255,0.02)"};
        border-radius: 8px;
    }}
    </style>
    """, unsafe_allow_html=True)

# Load market data
@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_market_data():
    try:
        with open('market_data.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return None

@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_daily_writeup():
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        filepath = f"Daily_write_ups/{today}dailywriteup.txt"
        with open(filepath, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return None

market_data = load_market_data()
if not market_data:
    st.error("Market data file not found. Please run the data collection script first.")
    st.stop()

daily_writeup = load_daily_writeup()
if not daily_writeup:
    daily_writeup = "Daily writeup not available for today."

# Main content container
with st.container():
    # Header with dynamic date display
    current_time = datetime.now()
    st.markdown(
        f'<p class="market-header">📊 Daily Market Newsletter</p>',
        unsafe_allow_html=True
    )
    
    if show_timestamps:
        st.markdown(
            f'<p class="timestamp">Last updated: {current_time.strftime("%B %d, %Y %I:%M %p")}</p>',
            unsafe_allow_html=True
        )

    # Daily Analysis and Yield Curves in a two-column layout
    col1, col2 = st.columns([3, 2])
    
    with col1:
        # Daily Analysis in a collapsible section
        with st.expander("📝 Today's Market Analysis", expanded=True):
            st.markdown('<div class="market-content">', unsafe_allow_html=True)
            st.write(daily_writeup)
            st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        # Yield Curve Graphs
        st.markdown('<p class="section-header">📈 Yield Curves</p>', unsafe_allow_html=True)
        
        # Convert yield data to DataFrame for plotting
        yield_data = market_data.get('yield_data', {})
        spread_data = market_data.get('yield_spreads', {})
        
        # 1. Current Yield Curve
        tenors = ['3M', '6M', '1Y', '2Y', '3Y', '5Y', '7Y', '10Y', '20Y', '30Y']
        
        # Get the most recent date's yields
        dates = set()
        for tenor_data in yield_data.values():
            dates.update(tenor_data.keys())
        latest_date = max(dates) if dates else None
        
        current_yields = {}
        if latest_date:
            for tenor in tenors:
                if tenor in yield_data and latest_date in yield_data[tenor]:
                    current_yields[tenor] = yield_data[tenor][latest_date]
                    
        yields = [current_yields.get(tenor, None) for tenor in tenors]
        
        fig_curve = go.Figure()
        fig_curve.add_trace(go.Scatter(
            x=tenors,
            y=yields,
            mode='lines+markers',
            name=f'Yield Curve ({latest_date})',
            line=dict(color=theme['primary'], width=2),
            marker=dict(size=8)
        ))
        fig_curve.update_layout(
            title={
                'text': 'U.S. Treasury Yield Curve',
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            },
            xaxis_title='Maturity',
            yaxis_title='Yield (%)',
            template='plotly_white',
            height=300,
            margin=dict(l=40, r=40, t=40, b=40),
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            ),
            plot_bgcolor='rgba(0,0,0,0.02)' if selected_theme != "Dark Mode" else 'rgba(255,255,255,0.02)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        fig_curve.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
        fig_curve.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
        st.plotly_chart(fig_curve, use_container_width=True, key='yield_curve')
        
        # 2. Key Spread Charts
        spreads_to_plot = {
            '10Y-2Y Spread': '10Y-2Y',
            '10Y-3M Spread': '10Y-3M',
            '5Y-2Y Spread': '5Y-2Y',
            '30Y-5Y Spread': '30Y-5Y'
        }
        
        for title, key in spreads_to_plot.items():
            if key in spread_data:
                dates = [datetime.strptime(d, '%Y-%m-%d') for d in spread_data[key].keys()]
                values = list(spread_data[key].values())
                
                # Calculate min and max for annotation
                latest_value = values[-1] if values else 0
                
                fig_spread = go.Figure()
                fig_spread.add_trace(go.Scatter(
                    x=dates,
                    y=values,
                    mode='lines',
                    name=title,
                    line=dict(color=theme['primary'], width=2)
                ))
                fig_spread.add_hline(
                    y=0, 
                    line_color=theme['accent'],
                    line_dash='dash',
                    annotation_text="Inversion Line",
                    annotation_position="bottom right"
                )
                
                # Add latest value annotation
                fig_spread.add_annotation(
                    x=dates[-1],
                    y=latest_value,
                    text=f"Latest: {latest_value:.2f}%",
                    showarrow=True,
                    arrowhead=1,
                    ax=40,
                    ay=-40 if latest_value > 0 else 40,
                    font=dict(size=10, color=theme['text']),
                    bgcolor='rgba(255, 255, 255, 0.8)'
                )
                
                fig_spread.update_layout(
                    title={
                        'text': title,
                        'y':0.95,
                        'x':0.5,
                        'xanchor': 'center',
                        'yanchor': 'top'
                    },
                    xaxis_title='Date',
                    yaxis_title='Spread (%)',
                    template='plotly_white',
                    height=250,
                    margin=dict(l=40, r=40, t=40, b=40),
                    showlegend=False,
                    plot_bgcolor='rgba(0,0,0,0.02)' if selected_theme != "Dark Mode" else 'rgba(255,255,255,0.02)',
                    paper_bgcolor='rgba(0,0,0,0)'
                )
                fig_spread.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
                fig_spread.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
                st.plotly_chart(fig_spread, use_container_width=True, key=f'spread_{key}')

    # News Headlines Section with filtering
    st.markdown('<p class="section-header">📰 News Highlights</p>', unsafe_allow_html=True)
    news_data = market_data['newsstr'].split('\n')[2:]  # Skip header
    
    # Simple news categorization (you can enhance this based on your needs)
    def categorize_news(headline):
        categories = []
        keywords = {
            "Markets": ["stock", "market", "index", "S&P", "Dow", "Nasdaq"],
            "Economy": ["GDP", "inflation", "economy", "Fed", "rates"],
            "Companies": ["Inc", "Corp", "Company", "CEO"],
            "Commodities": ["oil", "gold", "commodity", "crude"],
            "Currencies": ["dollar", "currency", "forex", "USD"]
        }
        
        for category, words in keywords.items():
            if any(word.lower() in headline.lower() for word in words):
                categories.append(category)
        return categories if categories else ["Other"]

    # Filter and display news
    filtered_news = []
    for news_item in news_data:
        if news_item.strip():
            # Extract source if available
            parts = news_item.split("Source:", 1)
            headline = parts[0].strip()
            source = parts[1].split("URL:")[0].strip() if len(parts) > 1 else "Unknown"
            
            # Categorize news
            categories = categorize_news(headline)
            
            # Check if news matches selected categories
            if any(cat in news_categories for cat in categories):
                filtered_news.append((headline, source, categories))
    
    # Display filtered news with enhanced formatting
    for i, (headline, source, categories) in enumerate(filtered_news[:max_headlines]):
        if not headline.strip():
            continue
            
        news_html = f"""
        <div class="news-item">
            <div>{headline}</div>
            {f'<span class="source-tag">{source}</span>' if show_news_sources else ''}
            {' '.join(f'<span class="source-tag">{cat}</span>' for cat in categories)}
        </div>
        """
        st.markdown(news_html, unsafe_allow_html=True)
