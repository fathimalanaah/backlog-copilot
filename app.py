import os
import streamlit as st

st.set_page_config(page_title="Backlog Copilot", layout="wide")
st.title("Backlog Copilot")
st.caption("Workshop notes → reviewed backlog")

st.write("LLM mode:", os.getenv("LLM_PROVIDER", "not set"))
st.write("Supabase URL set:", bool(os.getenv("SUPABASE_URL")))
