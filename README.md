"""Update README: full project summary, run/deploy notes, config and troubleshooting"""

# Financial-Markets-WriteUP-project

This repo is my automated, end-of-day market newsletter and dashboard. It collects market data, economic releases, earnings calendar items and news, synthesizes the inputs with a Gemini LLM prompt, and produces a concise PM market brief every trading day (typically generated around 4:45 PM ET).

The goal: a single, focused afternoon briefing that highlights the most important moves in equities, fixed income, commodities, FX, and macro data — and explains what they mean.

Live demo (deployed on Streamlit App Service):

https://financial-markets-writeup.streamlit.app/ (daily update ~4:45 PM ET)

---

## What this project contains

- `NewsletterDataCollection.ipynb` — the main data-gathering notebook. Collects:
	- Treasury yields and the 10Y–2Y spread (FRED)
	- Major indices, VIX, WTI/Brent, Gold, Dollar Index (yfinance)
	- Magnificent 7 price history (yfinance)
	- Economic calendar / weekly releases (FRED via Selenium scraping)
	- Headlines (NewsAPI)
	- Earnings for a list of important tickers (yfinance)
	- Additional FRED indicators (CPI, PPI, Retail Sales, Jobless Claims, PMI)
	- Assembles `market_data.json` and writes the daily Gemini writeup to `Daily_write_ups/{YYYY-MM-DD}dailywriteup.txt`.

- `newsletter_dashboard.py` — streamlined Streamlit dashboard that presents the daily writeup and a compact set of indicators. The dashboard is intentionally prose-first (newsletter-style) with only one small chart for the 10Y–2Y spread.

- `market_data.json` — generated snapshot of the most recent data used by the dashboard.

- `requirements.txt` — pinned (essential) Python packages for this project.

- `.gitignore` — ignores venvs, temporary files, JSON data and daily writeups.

---

## How it works (quick summary)

1. Run the notebook (`ScriptYfinance.ipynb`) or let your scheduled job run it each day. The notebook:
	 - pulls market data from yfinance and FRED,
	 - scrapes the FRED release calendar for scheduled releases,
	 - fetches headlines from NewsAPI,
	 - queries Gemini (via the `google-genai` client) to produce an authored PM writeup, and
	 - saves the structured snapshot to `market_data.json` and the writeup text file to `Daily_write_ups/`.

2. The Streamlit dashboard reads `market_data.json` and displays the most recent available writeup. The deployed dashboard keeps showing the last generated writeup until a new one appears (the authoring job runs around 4:45 PM ET). This prevents empty pages when the market is open but the writeup hasn't been created yet.

3. The dashboard is intentionally focused on text analysis with a compact 10Y–2Y chart; it can be extended to include more visuals if desired.

---

## Run locally

Create a venv, install dependencies, then either (A) run the notebook to generate data or (B) run the Streamlit app to view the latest writeup.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

To run the Streamlit dashboard locally:

```bash
source .venv/bin/activate
streamlit run financial_dashboard_new.py
```

To regenerate the data and the writeup, run the notebook `ScriptYfinance.ipynb` (execute cells in order). The notebook writes JSON and the daily writeup files used by the dashboard.

---

## Deployment notes

- The app is deployed on Streamlit App Service. The UI is designed to show the last available writeup until a new writeup file appears in `Daily_write_ups/`.
- The authoring step (Gemini LLM call) is expected to run as a scheduled job or cron that executes the notebook around 4:45 PM ET.

---

## Configuration & Secrets

Do NOT commit API keys. Put them in environment variables or a local `.env` file (and add `.env` to `.gitignore`). Keys used in the project include:

- FRED API key (`FRED_API_KEY`) — used by `fredapi`
- NewsAPI key (`NEWSAPI_KEY`) — used for headlines
- Google GenAI / Gemini API key (`GOOGLE_API_KEY`) — used to generate the daily writeup

Example (use your preferred secrets manager or export in shell):

```bash
export FRED_API_KEY="your_fred_key"
export NEWSAPI_KEY="your_newsapi_key"
export GOOGLE_API_KEY="your_gemini_key"
```

If you prefer a `.env` file, load it at runtime in the notebook or scripts (e.g., using `python-dotenv`).

---

## Adding or tweaking indicators

- The notebook already pulls several indicators via FRED using series IDs. To add CPI/PPI/Retail/PMI etc., add the FRED series ID to the `economic_indicators` mapping in the notebook. Example keys used in the notebook:
	- CPI: `CPIAUCSL`
	- PPI: `PPIACO`
	- Retail Sales: `RSAFS`
	- Initial Jobless Claims: `ICSA`
	- Manufacturing PMI / Services PMI: (example series IDs used in notebook)

- Earnings: the notebook queries yfinance for a short list of important tickers and stores `earnings` in `market_data.json`. To expand the list, edit `important_tickers` in the earnings cell.

If you need a full market-wide earnings calendar (S&P 500 or exchange-wide), consider using a dedicated earnings API (IEX, Nasdaq, or a paid provider) or scraping an earnings calendar — yfinance is convenient but limited for large-scale calendars.

---

## Behavior: keep last day's message until new one

The deployed dashboard intentionally preserves the last generated daily writeup until a new writeup file is detected in `Daily_write_ups/`. This is controlled by the dashboard logic and ensures readers always see a complete PM brief even before the daily generation job runs around 4:45 PM ET.

If you move the authoring job time, update the scheduler and the README accordingly.

---

## Troubleshooting

- If the dashboard shows "Market data file not found", run the notebook to regenerate `market_data.json` or ensure the notebook has write permissions.
- If yfinance returns incomplete data for certain tickers (common for indices or symbols with exchange suffixes), check the symbol mapping in the notebook and adjust the symbol (e.g., `DX-Y.NYB` for dollar index may require an alternate symbol provider).
- If the Gemini/GenAI call fails, check your `GOOGLE_API_KEY` and network connectivity.

---

## Automation with Cron

The project can be automated using cron jobs on Linux/Unix systems. Here's how to set it up:

1. First, ensure the shell script is executable:
   ```bash
   chmod +x /path/to/Finance/run_newsletter.sh
   ```

2. Open your crontab for editing:
   ```bash
   crontab -e
   ```

3. Add a cron job to run at 4:45 PM ET (adjust time zone as needed):
   ```bash
   # For Eastern Time (ET)
   45 16 * * 1-5 /path/to/Finance/run_newsletter.sh >> /path/to/Finance/cron.log 2>&1
   ```
   
   This cron schedule means:
   - 45: Run at minute 45
   - 16: Of hour 16 (4 PM)
   - \*: Every day of the month
   - \*: Every month
   - 1-5: Monday through Friday only
   
   Note: Adjust the hour based on your timezone. For example:
   - ET (UTC-4): 16:45
   - CT (UTC-5): 15:45
   - MT (UTC-6): 14:45
   - PT (UTC-7): 13:45

4. The script will:
   - Activate the Python virtual environment
   - Run the newsletter collector
   - Log any errors to cron.log
   - Deactivate the virtual environment

Troubleshooting Cron Jobs:
- Check cron.log for any errors
- Ensure all paths in run_newsletter.sh are absolute paths
- Verify environment variables are properly set in your .env file
- Test the shell script manually before setting up cron
- Make sure the cron user has necessary permissions

## Contributing

Open a PR with small, focused changes. Prefer defensive parsing for external data and add tests for any parsing logic you modify.

