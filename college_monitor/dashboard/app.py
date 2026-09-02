"""
Streamlit Dashboard for College Monitor
Run: streamlit run dashboard/app.py
"""
import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import os

st.set_page_config(page_title="College Monitor Dashboard", layout="wide")
st.title("College People Monitoring Dashboard")

DB_PATH = "data/attendance.db"

# Sidebar
st.sidebar.header("Filters")
date_filter = st.sidebar.date_input("Date", datetime.now())
session_filter = st.sidebar.selectbox("Session", ["All", "morning", "afternoon"])

# Main Content
if os.path.exists(DB_PATH):
    conn = sqlite3.connect(DB_PATH)
    
    query = "SELECT * FROM attendance WHERE date = ?"
    params = [date_filter.strftime("%Y-%m-%d")]
    
    if session_filter != "All":
        query += " AND session = ?"
        params.append(session_filter)
    
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()

    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Present", len(df["person_name"].unique()) if not df.empty else 0)
    col2.metric("Total Records", len(df))
    col3.metric("Zones Active", len(df["zone"].unique()) if not df.empty else 0)
    col4.metric("Sessions", len(df["session"].unique()) if not df.empty else 0)

    # Attendance table
    st.subheader("Attendance Records")
    if not df.empty:
        st.dataframe(df[["person_name", "timestamp", "zone", "session"]], use_container_width=True)
    else:
        st.info("No records for selected date/session.")

    # Hourly distribution
    st.subheader("Hourly Distribution")
    if not df.empty:
        df["hour"] = pd.to_datetime(df["timestamp"]).dt.hour
        hourly = df.groupby("hour").size()
        st.bar_chart(hourly)

else:
    st.warning("Database not found. Run the monitor first to generate data.")
    st.code("python main.py")

# Heatmap Gallery
st.subheader("Saved Heatmaps")
heatmap_dir = "data/heatmaps"
if os.path.exists(heatmap_dir):
    heatmaps = sorted(os.listdir(heatmap_dir), reverse=True)[:6]
    if heatmaps:
        cols = st.columns(3)
        for i, hm in enumerate(heatmaps):
            with cols[i % 3]:
                st.image(os.path.join(heatmap_dir, hm), caption=hm)
    else:
        st.info("No heatmaps saved yet. Press 's' while monitoring to save.")
else:
    st.info("Heatmap directory not created yet.")
