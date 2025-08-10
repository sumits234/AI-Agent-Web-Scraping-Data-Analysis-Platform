import os
import time
import csv
import uuid
import streamlit as st
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

# Load .env if present
load_dotenv()

# Prepare data dir
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

# Page config
st.set_page_config(page_title=" Scrape → Analyze", layout="wide")
st.title("🕵️‍♂️ AI-Powered Multi-Agent Web Scraping & Data Analysis Platform")
st.markdown("Scrape data from the web **or** upload files, then analyze them with natural language queries.")

# ================= GLOBAL API KEY =================
api_key_global = st.text_input("🔑 Enter your OpenAI API Key", type="password", value=os.getenv("OPENAI_APIKEY", ""))
if not api_key_global:
    st.warning("Please enter your OpenAI API key to continue.")

# Helper: save dataframe to CSV + Parquet
def save_df(df, base_name):
    csv_path = os.path.join(DATA_DIR, f"{base_name}.csv")
    parquet_path = os.path.join(DATA_DIR, f"{base_name}.parquet")
    try:
        df.to_csv(csv_path, index=False, quoting=csv.QUOTE_ALL, encoding="utf-8")
    except Exception:
        df.to_csv(csv_path, index=False, encoding="utf-8")
    try:
        df.to_parquet(parquet_path, index=False)
    except Exception:
        pass
    return csv_path, parquet_path

# ================= SCRAPE TAB =================
with st.expander("🌐 Scrape a website", expanded=True):
    st.markdown("**Enter the URL and what you want extracted.**")
    url = st.text_input("Website URL to scrape")
    user_prompt = st.text_area("Extraction prompt", value="Extract product name, price, rating, description as table rows.")
    scrape_model = st.selectbox("LLM model for scraping", ["gpt-3.5-turbo", "gpt-4"], index=0)

    try:
        from scrapegraphai.graphs import SmartScraperGraph
        scraper_available = True
    except Exception:
        scraper_available = False
        SmartScraperGraph = None

    if st.button("🚀 Run Scraper"):
        if not api_key_global:
            st.error("Please enter your API key above.")
        elif not url.strip():
            st.error("Please enter a URL.")
        elif not scraper_available:
            st.error("`scrapegraphai` not installed. Run: pip install scrapegraphai")
        else:
            st.info("Running SmartScraperGraph... please wait.")
            graph_config = {
                "llm": {
                    "api_key": api_key_global,
                    "model": scrape_model,
                },
                "verbose": False,
                "headless": True,
            }
            try:
                smart_scraper = SmartScraperGraph(prompt=user_prompt, source=url, config=graph_config)
                raw_result = smart_scraper.run()

                if isinstance(raw_result, (list, dict)):
                    try:
                        df = pd.json_normalize(raw_result)
                    except Exception:
                        df = pd.DataFrame([raw_result])
                else:
                    df = pd.DataFrame({"raw": [str(raw_result)]})

                base_name = f"scrape_{int(time.time())}_{uuid.uuid4().hex[:6]}"
                csv_path, parquet_path = save_df(df, base_name)

                st.success(f"✅ Scrape finished — saved to `{csv_path}`")
                st.dataframe(df.head(200))
                st.info("You can now analyze this dataset below.")
            except Exception as e:
                st.exception(e)

# ================= UPLOAD TAB =================
with st.expander("📂 Upload CSV / Excel", expanded=False):
    uploaded = st.file_uploader("Upload CSV / Excel", type=["csv", "xlsx", "xls"])
    if uploaded:
        try:
            if uploaded.name.endswith(".csv"):
                df = pd.read_csv(uploaded, encoding="utf-8", na_values=["NA", "N/A", "missing"])
            else:
                df = pd.read_excel(uploaded)

            for col in df.select_dtypes(include=["object"]).columns:
                df[col] = df[col].astype(str).replace({r'"': '""'}, regex=True)

            for col in df.columns:
                if "date" in col.lower():
                    df[col] = pd.to_datetime(df[col], errors="coerce")
                else:
                    try:
                        df[col] = pd.to_numeric(df[col])
                    except Exception:
                        pass

            base_name = f"upload_{int(time.time())}_{uuid.uuid4().hex[:6]}"
            csv_path, parquet_path = save_df(df, base_name)
            st.success(f"✅ Saved dataset to `{csv_path}`")
            st.dataframe(df.head(200))
        except Exception as e:
            st.error(f"Error processing file: {e}")

# ================= ANALYZE TAB =================
with st.expander("📊 Analyze datasets", expanded=True):
    csv_files = sorted([f for f in os.listdir(DATA_DIR) if f.endswith(".csv")], reverse=True)
    if not csv_files:
        st.info("No saved datasets yet. Scrape or upload one above.")
    else:
        selected = st.selectbox("Choose dataset CSV", csv_files)
        if selected:
            selected_path = os.path.join(DATA_DIR, selected)
            try:
                sample_df = pd.read_csv(selected_path, nrows=200)
            except Exception:
                sample_df = pd.DataFrame({"info": ["Preview not available"]})
            st.write(f"Preview of `{selected}` (first 200 rows):")
            st.dataframe(sample_df)

            model = st.selectbox("Model for analysis", ["gpt-4", "gpt-3.5-turbo"], index=0)
            user_query = st.text_area("Ask your question about the data", value="")

            if st.button("🔍 Run Analysis"):
                if not api_key_global:
                    st.error("Please enter your API key above.")
                elif not user_query.strip():
                    st.warning("Please enter a query.")
                else:
                    try:
                        from agno.models.openai import OpenAIChat
                        from agno.agent.duckdb import DuckDbAgent
                        from agno.tools.pandas import PandasTools
                        agent_available = True
                    except Exception as e:
                        agent_available = False
                        st.error("Required packages (`agno`) not installed.")
                        st.exception(e)

                    if agent_available:
                        try:
                            semantic_model = {
                                "tables": [
                                    {
                                        "name": "uploaded_data",
                                        "description": "Dataset uploaded or scraped by user.",
                                        "path": selected_path,
                                    }
                                ]
                            }
                            duckdb_agent = DuckDbAgent(
                                model=OpenAIChat(model=model, api_key=api_key_global),
                                semantic_model=__import__("json").dumps(semantic_model),
                                tools=[PandasTools()],
                                markdown=True,
                                add_history_to_messages=False,
                                followups=False,
                                read_tool_call_history=False,
                                system_prompt="You are an expert data analyst. Generate SQL queries to solve the user's query and return results.",
                            )

                            with st.spinner("Agent running..."):
                                response_obj = duckdb_agent.run(user_query)

                            if hasattr(response_obj, "content"):
                                st.subheader("Agent response")
                                st.markdown(response_obj.content)
                            else:
                                st.subheader("Agent response")
                                st.markdown(str(response_obj))

                        except Exception as e:
                            st.exception(e)

# ================= DATASETS LIST =================
with st.expander("📁 Saved datasets", expanded=False):
    files = sorted(os.listdir(DATA_DIR), reverse=True)
    for f in files:
        path = os.path.join(DATA_DIR, f)
        cols = st.columns([8,1,1])
        cols[0].write(f)
        if cols[1].button(f"Preview##{f}"):
            try:
                if f.endswith(".csv"):
                    st.dataframe(pd.read_csv(path).head(200))
                elif f.endswith(".parquet"):
                    st.dataframe(pd.read_parquet(path).head(200))
            except Exception as e:
                st.error(f"Preview failed: {e}")
        if cols[2].button(f"Delete##{f}"):
            try:
                os.remove(path)
                st.success(f"Deleted {f}")
                st.experimental_rerun()
            except Exception as e:
                st.error(f"Delete failed: {e}")

# Sidebar info
st.sidebar.header("ℹ️ Tips")
st.sidebar.write("• Enter API key once at the top — both scraper and analyzer use it.")

