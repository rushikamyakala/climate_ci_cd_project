from pathlib import Path
import sys
import logging
import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ---------------------------------------------------------------------
# Project setup and imports
# ---------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from app.climate_api import get_weather
from app.database import init_db, get_all_records, get_anomalies

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="Climate Intelligence",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------
# Premium visual system: midnight navy, glass panels, teal highlights
# ---------------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

    :root {
      --bg: #070d19;
      --panel: rgba(16, 27, 46, .78);
      --panel2: rgba(21, 36, 58, .84);
      --stroke: rgba(135, 166, 203, .18);
      --muted: #8ea4bf;
      --text: #edf5ff;
      --teal: #50f0cc;
      --blue: #8b9dff;
      --amber: #ffc777;
    }

    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
    .stApp {
      background:
        radial-gradient(ellipse at 4% 0%, rgba(28, 160, 145, .17), transparent 32%),
        radial-gradient(ellipse at 90% 6%, rgba(92, 102, 225, .17), transparent 31%),
        radial-gradient(ellipse at 55% 100%, rgba(20, 87, 111, .12), transparent 36%),
        var(--bg);
      color: var(--text);
    }
    [data-testid="stHeader"] { background: rgba(7,13,25,.72); }
    [data-testid="stSidebar"] {
      background: linear-gradient(180deg, #0b1424 0%, #09111f 100%);
      border-right: 1px solid var(--stroke);
    }
    [data-testid="stSidebar"] > div { padding-top: 1.2rem; }
    [data-testid="stSidebar"] * { color: #dce9fa; }
    h1, h2, h3 { font-family: 'Space Grotesk', sans-serif !important; letter-spacing: -.035em; }
    h1 { font-size: 2.05rem !important; }
    h2 { font-size: 1.5rem !important; }
    h3 { font-size: 1.08rem !important; }
    p, label { color: #c4d2e5; }
    .brand-lockup { display:flex; align-items:center; gap:.75rem; margin:.1rem 0 .3rem; }
    .brand-mark {
      display:flex; align-items:center; justify-content:center; width:42px; height:42px;
      border-radius:14px; background:linear-gradient(145deg, rgba(80,240,204,.23), rgba(139,157,255,.2));
      border:1px solid rgba(80,240,204,.35); font-size:1.25rem;
      box-shadow:0 0 24px rgba(80,240,204,.08);
    }
    .brand-name { font-family:'Space Grotesk',sans-serif; font-size:1.05rem; font-weight:700; color:#f4f8ff; }
    .brand-caption { font-size:.65rem; color:#7f96b4; letter-spacing:.16em; text-transform:uppercase; margin-top:.1rem; }
    .hero {
      position:relative; overflow:hidden; padding:1.6rem 1.65rem 1.45rem; border-radius:24px;
      border:1px solid rgba(137,170,211,.24);
      background:linear-gradient(115deg, rgba(19,43,61,.96), rgba(15,27,47,.93) 54%, rgba(35,37,79,.87));
      box-shadow:0 18px 60px rgba(0,0,0,.18); margin-bottom:1.1rem;
    }
    .hero:after {
      content:""; position:absolute; width:290px; height:290px; right:-70px; top:-135px; border-radius:50%;
      border:1px solid rgba(80,240,204,.18); box-shadow:0 0 0 25px rgba(80,240,204,.025), 0 0 0 55px rgba(139,157,255,.025);
    }
    .eyebrow { font-family:'DM Mono',monospace; color:var(--teal); text-transform:uppercase; letter-spacing:.16em; font-size:.7rem; }
    .hero-title { font-family:'Space Grotesk',sans-serif; font-size:2.25rem; font-weight:700; letter-spacing:-.05em; line-height:1.1; margin:.45rem 0 .55rem; color:#f5f8ff; }
    .hero-sub { max-width:680px; color:#aebfd5; font-size:.95rem; line-height:1.6; }
    .hero-bottom { display:flex; flex-wrap:wrap; gap:.55rem; margin-top:1.15rem; }
    .pill { display:inline-flex; align-items:center; gap:.4rem; padding:.38rem .68rem; border-radius:999px; font-size:.72rem; font-weight:600; border:1px solid rgba(80,240,204,.23); color:#a7ffe9; background:rgba(80,240,204,.07); }
    .section-kicker { color:#7f96b4; font-family:'DM Mono',monospace; font-size:.68rem; text-transform:uppercase; letter-spacing:.15em; margin-bottom:.35rem; }
    .section-heading { font-family:'Space Grotesk',sans-serif; font-size:1.22rem; font-weight:650; color:#f1f6ff; letter-spacing:-.025em; }
    .section-note { color:#8197b2; font-size:.8rem; }
    .panel {
      padding:1.05rem 1.1rem; border:1px solid var(--stroke); border-radius:18px;
      background:linear-gradient(145deg, rgba(19,32,53,.83), rgba(12,22,39,.8));
      box-shadow:0 10px 28px rgba(0,0,0,.12); min-height:100%;
    }
    .panel-label { color:#8ea4bf; font-size:.76rem; letter-spacing:.025em; }
    .panel-value { color:#f4f8ff; font-family:'Space Grotesk',sans-serif; font-size:1.75rem; font-weight:700; line-height:1.35; margin-top:.35rem; }
    .panel-foot { color:#7f96b4; font-size:.72rem; margin-top:.25rem; }
    div[data-testid="stMetric"] {
      background:linear-gradient(145deg, rgba(20,35,57,.94), rgba(12,22,38,.94));
      border:1px solid var(--stroke); padding:1rem 1.05rem; border-radius:17px; min-height:116px;
      box-shadow:0 10px 26px rgba(0,0,0,.1);
    }
    div[data-testid="stMetricLabel"] { color:#9db1c9; font-size:.8rem; }
    div[data-testid="stMetricValue"] { color:#f3f7ff; font-family:'Space Grotesk',sans-serif; }
    div[data-testid="stMetricDelta"] { font-size:.75rem; }
    div[data-testid="stPlotlyChart"] { border:1px solid rgba(135,166,203,.13); border-radius:17px; padding:.25rem; background:rgba(13,23,40,.48); }
    div[data-testid="stDataFrame"] { border:1px solid var(--stroke); border-radius:14px; overflow:hidden; }
    div.stButton > button, div.stDownloadButton > button {
      border-radius:11px; font-weight:700; min-height:2.7rem; transition:all .18s ease;
      border:1px solid rgba(80,240,204,.4);
    }
    div.stButton > button[kind="primary"] { background:linear-gradient(110deg,#50f0cc,#7be9d9); color:#07151c; border:0; }
    div.stButton > button:hover, div.stDownloadButton > button:hover { border-color:#50f0cc; transform:translateY(-1px); }
    div[data-baseweb="input"] > div, div[data-baseweb="select"] > div { background:rgba(12,22,38,.92); border-color:var(--stroke); border-radius:11px; }
    [data-testid="stRadio"] label { padding:.2rem 0; }
    hr { border-color:rgba(135,166,203,.15); margin:1.3rem 0; }
    .live-dot { display:inline-block; width:7px; height:7px; background:#50f0cc; border-radius:50%; margin-right:.35rem; box-shadow:0 0 12px rgba(80,240,204,.8); }
    .footer { display:flex; justify-content:space-between; flex-wrap:wrap; gap:.7rem; color:#7186a2; font-size:.74rem; padding:.3rem 0 1rem; }
    @media (max-width: 800px) {
      .hero-title { font-size:1.7rem; }
      .hero { padding:1.15rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------
# Data helpers
# ---------------------------------------------------------------------
try:
    init_db()
except Exception as exc:
    logger.exception("Database initialization failed")
    st.error(f"Database initialization failed: {exc}")
    st.stop()

PLOTLY_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans, sans-serif", color="#dce8f8", size=12),
    margin=dict(l=18, r=18, t=58, b=18),
    hoverlabel=dict(bgcolor="#111d31", bordercolor="#334862", font_color="#eff7ff"),
)

def styled_chart(fig, height=350):
    fig.update_layout(**PLOTLY_LAYOUT, height=height)
    fig.update_xaxes(showgrid=False, zeroline=False, linecolor="rgba(135,166,203,.2)")
    fig.update_yaxes(gridcolor="rgba(145,166,195,.12)", zeroline=False)
    return fig

def load_records():
    return pd.DataFrame(
        get_all_records(),
        columns=["ID", "City", "Temperature (°C)", "Humidity (%)", "Wind (m/s)", "Timestamp"],
    )

def load_anomalies():
    return pd.DataFrame(
        get_anomalies(),
        columns=["ID", "City", "Current Temp (°C)", "Previous Temp (°C)", "Difference (°C)", "Timestamp"],
    )

# ---------------------------------------------------------------------
# Sidebar navigation
# ---------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        """
        <div class="brand-lockup">
          <div class="brand-mark">◈</div>
          <div><div class="brand-name">CLIMATE IQ</div><div class="brand-caption">Intelligence platform</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    st.markdown("**WORKSPACE SECTIONS**")
    st.caption("Overview · Climate Analytics · Anomaly Center · Data Explorer · System & CI/CD")
    st.caption("All sections are displayed on this page. Scroll to explore the complete dashboard.")
    st.markdown("<div style='height:.5rem'></div>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("**DATA SOURCES**")
    st.caption("◉  OpenWeather API")
    st.caption("◉  SQLite observations")
    st.markdown("---")
    st.markdown("**QUALITY GATE**")
    st.caption("GitHub Actions · pytest")
    st.caption("Coverage artifact")
    st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)
    st.caption("CLIMATE OBSERVABILITY / V1.0")

# ---------------------------------------------------------------------
# Hero header and city search
# ---------------------------------------------------------------------
st.markdown(
    """
    <div class="hero">
      <div class="eyebrow">Climate observability &nbsp; / &nbsp; Research workspace</div>
      <div class="hero-title">Understand the atmosphere.<br>Act on the signal.</div>
      <div class="hero-sub">A real-time climate monitoring workspace combining weather API telemetry, persisted observations, temperature anomaly detection and automated software quality checks. Use the left navigation to explore analytics, anomaly records, stored data and CI/CD.</div>
      <div class="hero-bottom">
        <span class="pill"><span class="live-dot"></span> WEATHER MONITORING</span>
        <span class="pill">PLOTLY ANALYTICS</span>
        <span class="pill">CI / CD QUALITY GATE</span>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

search_col, button_col, hint_col = st.columns([3.2, 1.2, 1.7], vertical_alignment="bottom")
with search_col:
    city = st.text_input(
        "LOCATION",
        value=st.session_state.get("selected_city", "Hyderabad"),
        placeholder="Search a city…",
        label_visibility="visible",
    )
with button_col:
    fetch_clicked = st.button("🚀 Fetch Climate Data", type="primary", use_container_width=True)
with hint_col:
    st.markdown(
        f"<div style='padding:.55rem 0 .6rem;color:#8ea4bf;font-size:.78rem'><span class='live-dot'></span> API-powered · {datetime.datetime.now().strftime('%d %b %Y')}</div>",
        unsafe_allow_html=True,
    )

if fetch_clicked:
    if not city.strip():
        st.warning("Enter a city name before fetching weather.")
    else:
        with st.spinner(f"Retrieving current conditions for {city.strip()}…"):
            try:
                result = get_weather(city.strip())
            except Exception as exc:
                logger.exception("Weather request failed")
                result = {"error": f"Weather request failed: {exc}"}
        if "error" in result:
            st.error(result["error"])
        else:
            st.session_state["selected_city"] = city.strip()
            st.session_state["latest_weather"] = result
            st.session_state["latest_weather_city"] = city.strip()
            st.session_state["latest_weather_time"] = datetime.datetime.now().strftime("%d %b %Y · %H:%M:%S")
            st.toast("Live climate data updated", icon="🌐")

weather = st.session_state.get("latest_weather")
weather_city = st.session_state.get("latest_weather_city", city.strip() or "Hyderabad")
updated_at = st.session_state.get("latest_weather_time", "No successful fetch this session")

# ---------------------------------------------------------------------
# Overview
# ---------------------------------------------------------------------
if True:  # Full dashboard: show overview and all sections below
    left_title, right_title = st.columns([3, 1])
    with left_title:
        st.markdown("<div class='section-kicker'>01 / CURRENT CONDITIONS</div><div class='section-heading'>Atmospheric snapshot</div>", unsafe_allow_html=True)
    with right_title:
        st.markdown(f"<div style='text-align:right;color:#8197b2;font-size:.75rem;padding-top:.45rem'>Last updated<br><b style='color:#dce8f8'>{updated_at}</b></div>", unsafe_allow_html=True)

    if weather:
        st.caption(f"Monitoring location · {weather_city.title()}")
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("🌡 TEMPERATURE", f"{float(weather['temperature']):.1f} °C")
        k2.metric("💧 HUMIDITY", f"{weather['humidity']}%")
        k3.metric("🌬 WIND SPEED", f"{weather['wind_speed']} m/s")
        k4.metric("⚡ API LATENCY", f"{weather['api_response_time']:.3f} s")

        st.markdown("<div style='height:.5rem'></div>", unsafe_allow_html=True)
        visual_col, condition_col = st.columns([1.45, 1])
        with visual_col:
            gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=float(weather["temperature"]),
                number={"suffix": " °C", "font": {"size": 34, "color": "#f3f7ff"}},
                title={"text": "TEMPERATURE INDEX", "font": {"size": 13, "color": "#9db1c9"}},
                gauge={
                    "axis": {"range": [-10, 50], "tickcolor": "#8ea4bf", "tickfont": {"color": "#8ea4bf"}},
                    "bar": {"color": "#50f0cc", "thickness": .23},
                    "bgcolor": "rgba(0,0,0,0)",
                    "borderwidth": 0,
                    "steps": [
                        {"range": [-10, 20], "color": "rgba(65,190,183,.13)"},
                        {"range": [20, 35], "color": "rgba(255,199,119,.15)"},
                        {"range": [35, 50], "color": "rgba(255,100,124,.18)"},
                    ],
                },
            ))
            st.plotly_chart(styled_chart(gauge, 280), use_container_width=True, config={"displayModeBar": False})
        with condition_col:
            st.markdown("<div class='panel'>", unsafe_allow_html=True)
            st.markdown("<div class='section-kicker'>LIVE WEATHER SIGNAL</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='font-family:Space Grotesk;font-size:1.7rem;font-weight:700;color:#f4f8ff;margin:.5rem 0'>{weather.get('weather', '—')}</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='color:#9db1c9;margin-bottom:1rem'>{weather.get('description', '').title()}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='panel-label'>CITY</div><div style='font-size:1.1rem;font-weight:600;margin:.25rem 0 1rem'>{weather_city.title()}</div>", unsafe_allow_html=True)
            if weather.get("anomaly"):
                st.warning("A temperature anomaly was flagged by the configured detector.")
            else:
                st.success("No anomaly flagged by this fetch.")
            st.markdown("<div class='panel-foot'>Weather values are returned by the configured API.</div></div>", unsafe_allow_html=True)
    else:
        st.info("Use **Fetch Climate Data** to load the latest API response. Historical analytics will appear once records exist in the database.")

    st.markdown("<div style='height:.5rem'></div>", unsafe_allow_html=True)
    st.markdown("<div class='section-kicker'>02 / OBSERVATION STREAM</div><div class='section-heading'>Climate history</div><div class='section-note'>Recorded measurements from your SQLite database.</div>", unsafe_allow_html=True)
    records = load_records()
    if not records.empty:
        recent = records.head(150).copy()
        recent["Timestamp"] = pd.to_datetime(recent["Timestamp"], errors="coerce")
        fig = px.line(
            recent.sort_values("Timestamp"),
            x="Timestamp", y="Temperature (°C)", color="City", markers=True,
            title="Temperature observations over time",
            color_discrete_sequence=["#50f0cc", "#8b9dff", "#ffc777", "#6dc5ff", "#ff7c9d"],
        )
        fig.update_traces(line=dict(width=2.7), marker=dict(size=6))
        st.plotly_chart(styled_chart(fig, 370), use_container_width=True)
        st.caption("Chart values come from stored observations; no synthetic history is generated.")
    else:
        st.markdown("<div class='panel'><div class='panel-label'>NO OBSERVATIONS YET</div><div style='color:#a8bbd2;margin-top:.45rem'>Fetch weather for a city to start building the historical record.</div></div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------
# Climate analytics
# ---------------------------------------------------------------------
if True:  # Climate analytics section
    st.markdown("---")
    st.markdown("<div class='section-kicker'>03 / ANALYTICS</div><div class='section-heading'>Climate patterns</div><div class='section-note'>Filter historical observations and explore temperature and humidity trends.</div>", unsafe_allow_html=True)
    records = load_records()
    if records.empty:
        st.info("No climate records yet. Fetch weather data first.")
    else:
        records["Timestamp"] = pd.to_datetime(records["Timestamp"], errors="coerce")
        options = sorted(records["City"].dropna().astype(str).unique().tolist())
        default_index = options.index(weather_city) if weather_city in options else 0
        chosen_city = st.selectbox("Select location", options, index=default_index)
        filtered = records[records["City"].astype(str) == chosen_city].sort_values("Timestamp")
        a, b, c, d = st.columns(4)
        a.metric("OBSERVATIONS", len(filtered))
        b.metric("MEAN TEMPERATURE", f"{filtered['Temperature (°C)'].mean():.1f} °C")
        c.metric("MEAN HUMIDITY", f"{filtered['Humidity (%)'].mean():.1f}%")
        d.metric("MEAN WIND", f"{filtered['Wind (m/s)'].mean():.1f} m/s")
        temp_fig = px.line(filtered, x="Timestamp", y="Temperature (°C)", markers=True, title=f"{chosen_city} · temperature timeline")
        temp_fig.update_traces(line=dict(color="#50f0cc", width=3), marker=dict(size=7))
        st.plotly_chart(styled_chart(temp_fig, 390), use_container_width=True)
        humidity_fig = px.area(filtered, x="Timestamp", y="Humidity (%)", title="Relative humidity timeline")
        humidity_fig.update_traces(line_color="#8b9dff", fillcolor="rgba(139,157,255,.16)")
        st.plotly_chart(styled_chart(humidity_fig, 320), use_container_width=True)
        st.caption("Sampling frequency depends on when weather data is fetched and saved.")

# ---------------------------------------------------------------------
# Anomaly center
# ---------------------------------------------------------------------
if True:  # Anomaly center section
    st.markdown("---")
    st.markdown("<div class='section-kicker'>04 / DETECTION</div><div class='section-heading'>Anomaly center</div><div class='section-note'>Review temperature changes recorded by the anomaly detector.</div>", unsafe_allow_html=True)
    anomalies = load_anomalies()
    if anomalies.empty:
        st.success("No anomaly records are currently stored.")
        st.caption("Records appear when the application's configured temperature-change rule is triggered.")
    else:
        a, b, c = st.columns(3)
        a.metric("RECORDED ANOMALIES", len(anomalies))
        b.metric("LARGEST CHANGE", f"{anomalies['Difference (°C)'].max():.1f} °C")
        c.metric("AFFECTED CITIES", anomalies["City"].nunique())
        anomalies["Timestamp"] = pd.to_datetime(anomalies["Timestamp"], errors="coerce")
        fig = px.scatter(
            anomalies, x="Timestamp", y="Current Temp (°C)", color="Difference (°C)", size="Difference (°C)",
            hover_data=["City", "Previous Temp (°C)"], title="Flagged temperature changes",
            color_continuous_scale=["#50f0cc", "#ffc777", "#ff647c"],
        )
        st.plotly_chart(styled_chart(fig, 420), use_container_width=True)
        st.dataframe(anomalies, use_container_width=True, hide_index=True)

# ---------------------------------------------------------------------
# Data explorer
# ---------------------------------------------------------------------
if True:  # Data explorer section
    st.markdown("---")
    st.markdown("<div class='section-kicker'>05 / DATA</div><div class='section-heading'>Observation explorer</div><div class='section-note'>Search, filter, inspect and export persisted climate records.</div>", unsafe_allow_html=True)
    records = load_records()
    if records.empty:
        st.info("No climate records are available yet.")
    else:
        filter_col, search_col = st.columns([1, 2])
        cities = ["All cities"] + sorted(records["City"].dropna().astype(str).unique().tolist())
        city_filter = filter_col.selectbox("City filter", cities)
        search = search_col.text_input("Search records", placeholder="Search city, timestamp or value")
        filtered = records.copy()
        if city_filter != "All cities":
            filtered = filtered[filtered["City"].astype(str) == city_filter]
        if search:
            mask = filtered.astype(str).apply(lambda col: col.str.contains(search, case=False, na=False)).any(axis=1)
            filtered = filtered[mask]
        st.caption(f"{len(filtered)} records match your filters")
        st.dataframe(filtered, use_container_width=True, hide_index=True)
        st.download_button(
            "↓  Export filtered records as CSV",
            data=filtered.to_csv(index=False).encode("utf-8"),
            file_name="climate_records.csv",
            mime="text/csv",
        )
        if not filtered.empty:
            st.markdown("#### Summary of filtered data")
            a, b, c, d = st.columns(4)
            a.metric("MEAN TEMP", f"{filtered['Temperature (°C)'].mean():.1f} °C")
            b.metric("MAX TEMP", f"{filtered['Temperature (°C)'].max():.1f} °C")
            c.metric("MEAN HUMIDITY", f"{filtered['Humidity (%)'].mean():.1f}%")
            d.metric("MEAN WIND", f"{filtered['Wind (m/s)'].mean():.1f} m/s")

# ---------------------------------------------------------------------
# System and CI/CD
# ---------------------------------------------------------------------
if True:  # System and CI/CD section
    st.markdown("---")
    st.markdown("<div class='section-kicker'>06 / ENGINEERING</div><div class='section-heading'>System health & delivery</div><div class='section-note'>Project capabilities and latest development verification.</div>", unsafe_allow_html=True)
    st.markdown("#### Quality snapshot")
    a, b, c = st.columns(3)
    a.metric("LATEST LOCAL TEST RUN", "27 passed")
    b.metric("MEASURED APP COVERAGE", "100%")
    c.metric("LATEST GITHUB CI", "Passing")
    st.warning("These are the latest results reported during development, not live values fetched from GitHub. Refresh them after running a new test suite.")
    st.markdown("#### Pipeline stages")
    stage_cols = st.columns(4)
    for col, label, detail in zip(
        stage_cols,
        ["Checkout", "Install", "Test + coverage", "Artifact"],
        ["Repository source", "Python dependencies", "pytest + coverage", "HTML report"],
    ):
        with col:
            st.markdown(f"<div class='panel'><div class='panel-label'>{label.upper()}</div><div style='font-weight:650;color:#eaf3ff;margin:.5rem 0'>{detail}</div><div class='panel-foot'>Configured in ci.yml</div></div>", unsafe_allow_html=True)
    st.markdown("#### Implemented components")
    st.markdown("- Streamlit dashboard with Plotly charts\n- OpenWeather API integration\n- SQLite climate and anomaly records\n- pytest automated tests and coverage reporting\n- GitHub Actions CI workflow with artifact upload")
    st.caption("Pipeline metrics shown here describe configured stages; this dashboard does not fetch live run data from GitHub.")

st.markdown("---")
st.markdown(
    f"<div class='footer'><span>◈ CLIMATE IQ &nbsp; · &nbsp; Python / Streamlit / SQLite / Plotly</span>"
    f"<span>Rendered {datetime.datetime.now().strftime('%d %b %Y · %H:%M:%S')}</span></div>",
    unsafe_allow_html=True,
)
