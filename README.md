# 🚀 AI-Powered Multi-Agent Web Scraping & Data Analysis Platform
An end-to-end AI platform that **scrapes structured data from any website** and then **analyzes it using natural language queries** — all from a single unified interface. Built with **Streamlit**, **ScrapeGraphAI**, and **DuckDB AI Agents**, this project demonstrates the power of combining multiple AI agents in one workflow.

## ✨ Features
### 📤 Data Ingestion
- **Web Scraping Agent**: Extract structured data (tables, lists, product details, etc.) from any public webpage.
- **File Upload Support**: Upload CSV or Excel files for instant analysis.
- **Automatic Data Normalization**: Cleans, detects types, and stores data in CSV + Parquet formats.

### 🤖 AI Agents
- **Scraping Agent**: Powered by [ScrapeGraphAI](https://github.com/VinciGit00/Scrapegraph-ai) and OpenAI LLMs.
- **Analysis Agent**: Uses DuckDB + OpenAI to convert **natural language** into SQL queries, run them, and return answers.

### 📊 Data Analysis
- Generate charts and statistical summaries.
- Filter, sort, and group data interactively.
- Preview saved datasets and re-run analysis anytime.

### 🖥 Multi-Agent Web Scraping & Data Analysis Platform
- Built with **Streamlit** for an easy-to-use, responsive UI.
- Single API key setup for both agents.
- Save & manage multiple scraped or uploaded datasets.

## 🛠 Tech Stack
- **Frontend/UI**: [Streamlit](https://streamlit.io/)
- **Scraping Agent**: [ScrapeGraphAI](https://github.com/VinciGit00/Scrapegraph-ai)
- **Analysis Agent**: [DuckDB](https://duckdb.org/) + [Agno AI Agent](https://pypi.org/project/agno/)
- **LLMs**: OpenAI GPT-3.5 / GPT-4
- **Data Formats**: CSV, Parquet
- **Language**: Python 3.10+
  
## 🙌 Welcome & Contributing

## 📦 Installation
```bash
# 1️⃣ Clone this repository
git clonehttps://github.com/sumits234/AI-Agent-Web-Scraping-Data-Analysis-Platform.git
cd <AI-Agent-Web-Scraping-Data-Analysis-Platform>

# 2️⃣ Create & activate virtual environment
python -m venv .venv
.venv\Scripts\activate      # Windows

# 3️⃣ Install dependencies
pip install -r requirements.txt

# 4️⃣ Install Playwright for ScrapeGraphAI
playwright install

# 5️⃣ Add your OpenAI API key to .env
 OPENAI_API_KEY="your_key_here" > .env

# 6️⃣ Run the app
streamlit run app.py

