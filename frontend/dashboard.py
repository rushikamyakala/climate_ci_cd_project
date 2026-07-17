from pathlib import Path
import sys
import logging
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))
import streamlit as st
import pandas as pd
import datetime
import plotly.express as px
import plotly.graph_objects as go
import random

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

from app.climate_api import get_weather
from app.database import (
    init_db,
    get_all_records,
    get_anomalies,
    get_last_7_records
)

# ===============================
# PAGE CONFIG
# ===============================
st.set_page_config(
    page_title="Climate Intelligence Enterprise Dashboard",
    layout="wide"
)

try:
    init_db()
    logger.info("Database initialized successfully.")
except Exception as e:
    logger.error(f"Database initialization failed: {e}")
    st.stop()

# ===============================
# 🔥 Animated Glowing Header
# ===============================
st.markdown("""
<style>
@keyframes glow {
  0% { text-shadow: 0 0 5px #00C9A7; }
  50% { text-shadow: 0 0 20px #845EC2; }
  100% { text-shadow: 0 0 5px #00C9A7; }
}

.glow-title {
  font-size: 52px;
  text-align: center;
  font-weight: bold;
  background: linear-gradient(to right, #00C9A7, #845EC2);
  -webkit-background-clip: text;
  color: transparent;
  animation: glow 3s infinite;
}
</style>

<h1 class="glow-title">🌍 Climate Intelligence Monitoring System</h1>
""", unsafe_allow_html=True)

st.markdown("### Real-Time Climate • DevOps Metrics • CI/CD Observability")
st.markdown("---")

# ===============================
# INPUT + FULL WIDTH MODE
# ===============================
col1, col2 = st.columns([3,1])
city = col1.text_input("Enter City Name:", "Hyderabad").strip()
full_width = col2.toggle("Full Width Graph Mode")

# ===============================
# FETCH DATA
# ===============================
if st.button("🚀 Fetch Data"):

    if not city:
        st.warning("Please enter a city name.")
        st.stop()

    with st.spinner("Fetching climate data..."):
        weather = get_weather(city)

    logger.info(f"Weather requested for {city}")

    if "error" in weather:
        logger.error(weather["error"])
        st.error(weather["error"])
    else:

        # ==========================
        # Smooth KPI Cards
        # ==========================
        st.subheader("📊 Live KPIs")

        k1, k2, k3, k4 = st.columns(4)

        k1.metric("🌡 Temperature", f"{weather['temperature']} °C")
        k2.metric("💧 Humidity", f"{weather['humidity']} %")
        k3.metric("🌬 Wind Speed", f"{weather['wind_speed']} m/s")
        k4.metric("⚡ API Time", f"{weather['api_response_time']} s")

        st.markdown("---")

        # ==========================
        # Gauge
        # ==========================
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=weather["temperature"],
            title={'text': "Temperature Level"},
            gauge={
                'axis': {'range': [-10, 50]},
                'bar': {'color': "#00C9A7"},
            }
        ))

        fig_gauge.update_layout(template="plotly_dark")

        if full_width:
            st.plotly_chart(fig_gauge, use_container_width=True)
        else:
            g1, g2 = st.columns(2)
            g1.plotly_chart(fig_gauge, use_container_width=True)

        # ==========================
        # Real-Time Trend
        # ==========================
        if "history" not in st.session_state:
            st.session_state.history = []

        st.session_state.history.append({
            "time": datetime.datetime.now(),
            "temperature": weather["temperature"]
        })

        df_live = pd.DataFrame(st.session_state.history)
        history = get_last_7_records(city)

if history:
    df_history = pd.DataFrame(
        history,
        columns=["Temperature", "Timestamp"]
    )

    st.subheader("📈 Last 7 Stored Records")
    st.dataframe(df_history, use_container_width=True)

fig_live = px.area(
    df_live,
    x="time",
    y="temperature",
    color_discrete_sequence=["#845EC2"],
    title="Real-Time Temperature Trend"
)

fig_live.update_layout(template="plotly_dark")

st.plotly_chart(fig_live, use_container_width=True)

# ===============================
# 📦 CI/CD METRICS PREVIEW
# ===============================
st.markdown("## 📦 CI/CD Pipeline Metrics (Preview)")

# Demo data (replace later with real pipeline logs)
pipeline_data = pd.DataFrame({
    "Build": range(1, 11),
    "Execution_Time": [random.uniform(20, 60) for _ in range(10)],
    "Test_Coverage": [random.uniform(75, 98) for _ in range(10)]
})

fig_exec = px.line(
    pipeline_data,
    x="Build",
    y="Execution_Time",
    title="Pipeline Execution Time Trend",
    color_discrete_sequence=["#00C9A7"]
)

fig_cov = px.line(
    pipeline_data,
    x="Build",
    y="Test_Coverage",
    title="Test Coverage Trend",
    color_discrete_sequence=["#845EC2"]
)

fig_exec.update_layout(template="plotly_dark")
fig_cov.update_layout(template="plotly_dark")

st.plotly_chart(fig_exec, use_container_width=True)
st.plotly_chart(fig_cov, use_container_width=True)

# ===============================
# STORED RECORDS + EXPORT
# ===============================
st.markdown("## 🗄 Stored Records")

records = get_all_records()

if records:
    df_records = pd.DataFrame(
        records,
        columns=["ID","City","Temperature","Humidity","Wind","Timestamp"]
    )

    st.dataframe(df_records, use_container_width=True)

    # Export Button
    csv = df_records.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="⬇ Download Records as CSV",
        data=csv,
        file_name="climate_records.csv",
        mime="text/csv"
    )
    logger.info("Climate records exported as CSV.")

# ===============================
# ANOMALY SECTION
# ===============================
st.markdown("## ⚠️ Anomaly Records")

anomalies = get_anomalies()

if anomalies:
    st.error(f"🚨 Total Anomalies: {len(anomalies)}")
    df_anom = pd.DataFrame(
        anomalies,
        columns=["ID","City","Current Temp","Previous Temp","Difference","Timestamp"]
    )
    st.dataframe(df_anom, use_container_width=True)
else:
    st.success("No anomalies detected.")
    logger.info("Dashboard loaded successfully.")
    st.markdown("---")
    st.caption(f"Last Updated: {datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")