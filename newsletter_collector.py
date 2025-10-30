#!/usr/bin/env python3

import pandas as pd 
import numpy as np 
import json 
import requests 
from io import StringIO 
from bs4 import BeautifulSoup 
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import chromedriver_autoinstaller
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import yfinance as yf
from datetime import datetime, timedelta
import os 
from fredapi import Fred
from google import genai
from dotenv import load_dotenv
#test
def main():
    load_dotenv()
    # Initialize Chrome options for headless operation
    options = Options()
    options.add_argument("--headless")  # Run in headless mode
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    # Ensure chromedriver is installed
    chromedriver_autoinstaller.install()
    
    # Initialize FRED API
    fred = Fred(api_key=os.getenv("fred_api_key"))
    
    # Get dates
    today = datetime.now().date()
    start_date = today - timedelta(days=7)
    
    # Get Treasury spread data
    series_10yr = fred.get_series('DGS10', observation_start=start_date, observation_end=today)
    series_2yr = fred.get_series('DGS2', observation_start=start_date, observation_end=today)
    spread = series_10yr - series_2yr
    tenyrtwoyr = []
    for date, value in spread.items():
        if pd.notnull(value):
            tenyrtwoyr.append(f"{date.strftime('%Y-%m-%d')}: {value:.2f}")
    
    # Get economic indicators
    economic_indicators = {
        'Initial Jobless Claims': 'ICSA',
        'CPI': 'CPIAUCSL',
        'PPI': 'PPIACO',
        'Retail Sales': 'RSAFS',
        'Manufacturing PMI': 'MPMUGR',
        'Services PMI': 'SPMUGR'
    }
    
    latest_economic_data = {}
    for indicator_name, series_id in economic_indicators.items():
        try:
            series = fred.get_series(series_id, observation_start=start_date, observation_end=today)
            if not series.empty:
                latest_date = series.index[-1]
                latest_value = series.iloc[-1]
                latest_economic_data[indicator_name] = f"{latest_date.strftime('%Y-%m-%d')}: {latest_value:.2f}"
        except Exception as e:
            print(f"Error fetching {series_id}: {e}")
    
    # # Get FRED releases
    # driver = webdriver.Chrome(options=options)
    # try:
    #     driver.get("https://fred.stlouisfed.org/")
    #     driver.maximize_window()
        
    #     release_calendar = driver.find_element(By.XPATH, '//*[@id="subheader-navbar"]/li[1]')
    #     release_calendar.click()
    #     dropdown = driver.find_element(By.XPATH, '//*[@id="rc-views"]')
    #     dropdown.click()
    #     monthly_click = dropdown.find_element(By.XPATH, '//*[@id="rc-view-month"]')
    #     monthly_click.click()
    #     today_btn = driver.find_element(By.XPATH, '//*[@id="calendar"]/div[1]/div[1]/button')
    #     today_btn.click()
    #     weekly_click = dropdown.find_element(By.XPATH, '//*[@id="rc-view-week"]')
    #     weekly_click.click()
    #     releases = driver.find_element(By.XPATH, '//*[@id="release-dates-pager"]/div/table/tbody')
    #     releases = releases.find_elements(By.TAG_NAME, 'tr')
    #     Releases = [release.text for release in releases]
    # finally:
    #     driver.quit()
    
    # Get stock data
    tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA"]
    data = yf.download(tickers, start=start_date, end=today + timedelta(days=1), interval="1d", group_by='ticker')
    ticker_data = ""
    for ticker in tickers:
        if ticker in data:
            df = data[ticker]
            for idx, row in df.iterrows():
                if idx.weekday() < 5:
                    open_price = row['Open']
                    close_price = row['Close']
                    date_str = idx.strftime('%Y-%m-%d')
                    ticker_data += f"{ticker} {date_str}: Open: ${open_price:.2f} Close: ${close_price:.2f}. "
    
    # Get market indices
    indices = [
        "^GSPC", "^DJI", "^IXIC", "^RUT",
        "^VIX",
        "CL=F", "BZ=F",
        "GC=F",
        "DX-Y.NYB"
    ]
    
    data = yf.download(indices, start=today, end=today + timedelta(days=1), interval="1d", group_by='ticker')
    
    symbol_names = {
        "^GSPC": "S&P 500",
        "^DJI": "Dow Jones",
        "^IXIC": "NASDAQ",
        "^RUT": "Russell 2000",
        "^VIX": "VIX",
        "CL=F": "WTI Crude",
        "BZ=F": "Brent Crude",
        "GC=F": "Gold",
        "DX-Y.NYB": "US Dollar Index"
    }
    
    indice_data_str = ""
    for index in indices:
        try:
            open_price = data[index]['Open'][0]
            close_price = data[index]['Close'][0]
            name = symbol_names.get(index, index)
            indice_data = f"{name}: Open: {open_price:.2f} Close: {close_price:.2f}"
            indice_data_str += indice_data + '. '
        except (KeyError, IndexError) as e:
            print(f"Error getting data for {index}: {e}")
    
    # Get news
    API_KEY = os.getenv("NewsApikey")
    yesterday = today - timedelta(days=1)
    url = "https://newsapi.org/v2/everything"
    
    queries = [
        "stock market OR equities OR shares OR S&P 500 OR NASDAQ OR Dow Jones",
        "Apple OR Microsoft OR Google OR Amazon OR Nvidia OR Meta OR Tesla",
        "inflation OR CPI OR PPI OR interest rates OR Federal Reserve",
        "recession OR GDP OR economy OR job market OR payrolls",
        "oil prices OR crude OR energy OR commodities OR gold",
        "housing market OR mortgage OR real estate OR home sales"
    ]
    
    base_params = {
        "from": yesterday.isoformat(),
        "to": today.isoformat(),
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": 100,
        "apiKey": API_KEY
    }
    
    all_articles = []
    newsstr = f"\n📰 Broad Market News for {today}:\n"
    
    for query in queries:
        print(f"Fetching news for query: {query}")
        params = base_params.copy()
        params["q"] = query
        
        response = requests.get(url, params=params)
        if response.status_code != 200:
            print(f"Error {response.status_code} for query '{query}':", response.json().get("message"))
            continue
            
        data = response.json()
        if data.get("status") == "ok":
            articles = data.get("articles", [])
            all_articles.extend(articles)
        else:
            print(f"Failed to fetch articles for query '{query}':", data.get("message"))
    
    for i, article in enumerate(all_articles):
        title = article['title']
        source = article['source']['name']
        url = article['url']
        newsstr += f"{i}. {title}   Source: {source}  URL: {url}\n"
        if i >= 40:
            break
    
    # Save market data
    market_data = {
        'tenyrtwoyr': tenyrtwoyr,
        'indice_data_str': indice_data_str,
        'ticker_data': ticker_data,
        'newsstr': newsstr,
        'economic_indicators': latest_economic_data
    }
    
    with open('market_data.json', 'w') as f:
        json.dump(market_data, f)
    
    # Generate daily writeup
    message = (
        f"You are an experienced economist and financial analyst specializing in market dynamics, bond markets, and Treasury yields. Format your response in plain text only, avoiding any special formatting or markdown.\n\n"
        f"You are the author of a daily PM financial newsletter that summarizes the key market developments of the day. "
        f"The market brief should be titled 'PM Market Brief by Gemini' in plain text. You should not use any markdown or speciial formattiing \n\n "
        f"Your goal is to highlight the most important news, notable market movements, and any meaningful economic signals. "
        f"If the date corresponds to a weekend, do not include market tickers or Magnificent 7 stock data.\n\n"
        f"Your task is to analyze and interpret the following financial data:\n"
        f"• The 10-Year minus 2-Year Treasury yield spread\n"
        f"• Major stock indices (daily open and close)\n"
        f"• Market Volatility (VIX)\n"
        f"• Commodities (WTI Crude, Brent Crude, Gold)\n"
        f"• Currency Markets (US Dollar Index)\n"
        f"• The Magnificent 7 stock prices (daily open and close, last seven days)\n"
        f"• Recent and scheduled economic releases\n"
        f"• Key market news headlines from the last 24 hours\n\n"
        f"Please organize your analysis into these sections:\n"
        f"1. Market Summary\n"
        f"   - Major Indices Performance\n"
        f"   - VIX and Market Sentiment\n"
        f"2. Fixed Income & Macro\n"
        f"   - Treasury Spreads Analysis\n"
        f"   - Dollar Index Movements\n"
        f"3. Commodities & Energy\n"
        f"   - Oil Markets (WTI/Brent)\n"
        f"   - Gold Price Action\n"
        f"4. Economic Data\n"
        f"   - Today's Releases\n"
        f"   - Forward Calendar\n"
        f"5. Key Takeaways & Outlook\n\n"
        f"Also include a neatly formatted table summarizing key numerical data (excluding news headlines).\n\n"
        f"Data for analysis (Date: {today}):\n"
        f"— Last 5 days of 10-Year minus 2-Year Treasury yield spread: {tenyrtwoyr}\n"
        f"— Market indices and indicators: {indice_data_str}\n"
        f"— Magnificent 7 stock prices (last seven days, daily open and close): {ticker_data}\n"
        f"— Economic releases from FRED: \n"
        f"— Market news headlines (past 24h): {newsstr}\n"
        f"create a nicely formatted table summarizing key numerical data (excluding news headlines).\n\n"

    )
    
    client = genai.Client(api_key=os.getenv("GOOGLE_KEY"))
    response = client.models.generate_content(
        model="gemini-2.5-pro",
        contents=message
    )
    
    folder = "Daily_write_ups"
    if not os.path.exists(folder):
        os.makedirs(folder)
        
    filename = f"{today}dailywriteup.txt"
    filepath = os.path.join(folder, filename)
    
    with open(filepath, "w") as f:
        f.write(response.text)

if __name__ == "__main__":
    main()