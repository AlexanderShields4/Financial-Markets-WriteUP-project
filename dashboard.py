import streamlit as st
import json

st.set_page_config(page_title="Finance Dashboard", layout="wide")
st.title("📈 Daily Financial Market Dashboard")

# Load data from JSON file
with open("dashboard_data.json", "r") as f:
    data = json.load(f)

tenyrtwoyr = data.get("tenyrtwoyr", [])
indice_data_str = data.get("indice_data_str", "")
ticker_data = data.get("ticker_data", "")
daily_releases = data.get("daily_releases", "")
newsstr = data.get("newsstr", "")

# 10-Year Minus 2-Year Treasury Yield Spread
st.header("10-Year Minus 2-Year Treasury Yield Spread (Last 5 Days)")
for entry in tenyrtwoyr:
    st.write(entry)

# Major Stock Indices
st.header("Major U.S. Stock Indices (Open & Close)")
st.write(indice_data_str)

# Magnificent 7 Stock Prices
st.header("Magnificent 7 Stock Prices (Open & Close)")
st.write(ticker_data)

# Scheduled Economic Releases
st.header("Scheduled Economic Releases")
st.write(daily_releases)

# Daily Market News Headlines
st.header("📰 Daily Market News Headlines")
st.write(newsstr)
