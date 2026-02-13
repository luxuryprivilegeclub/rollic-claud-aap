import streamlit as st
import plotly.graph_objects as go
import requests
from datetime import datetime

# ============================================
# PAGE CONFIGURATION
# ============================================
st.set_page_config(
    page_title="FRED Economic Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================
# CUSTOM CSS STYLING
# ============================================
st.markdown("""
<style>
    /* Dark Theme */
    .stApp {
        background-color: #0a0a1a;
    }

    /* Header Styling */
    .main-header {
        text-align: center;
        color: #00d4ff;
        font-size: 36px;
        font-weight: bold;
        text-shadow: 0 0 20px rgba(0, 212, 255, 0.5);
        padding: 20px 0 5px 0;
    }

    .sub-header {
        text-align: center;
        color: #888;
        font-size: 14px;
        margin-bottom: 20px;
    }

    /* Card Styling */
    .gauge-card {
        background-color: rgba(255,255,255,0.03);
        border-radius: 15px;
        border: 1px solid rgba(255,255,255,0.08);
        padding: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        margin: 5px;
    }

    .description-text {
        text-align: center;
        color: #555;
        font-size: 11px;
        margin-top: -10px;
        padding-bottom: 10px;
    }

    /* Footer */
    .footer-text {
        text-align: center;
        color: #444;
        font-size: 12px;
        padding: 20px;
    }

    /* Legend */
    .legend-text {
        text-align: center;
        color: #666;
        font-size: 13px;
    }

    /* Hide Streamlit defaults */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# FRED API CONFIGURATION
# ============================================
FRED_API_KEY = st.secrets.get("FRED_API_KEY", "demo")
BASE_URL = "https://api.stlouisfed.org/fred/series/observations"

# ============================================
# FRED SERIES DEFINITIONS
# ============================================
FRED_SERIES = {
    'GDP': {
        'id': 'GDP',
        'title': 'GDP (Billions $)',
        'min': 0, 'max': 30000,
        'ranges': [10000, 20000, 30000],
        'color': '#1f77b4',
        'description': 'Gross Domestic Product'
    },
    'UNRATE': {
        'id': 'UNRATE',
        'title': 'Unemployment Rate (%)',
        'min': 0, 'max': 15,
        'ranges': [3, 6, 15],
        'color': '#ff7f0e',
        'description': 'Civilian Unemployment Rate'
    },
    'CPIAUCSL': {
        'id': 'CPIAUCSL',
        'title': 'Consumer Price Index',
        'min': 0, 'max': 350,
        'ranges': [150, 250, 350],
        'color': '#2ca02c',
        'description': 'CPI for All Urban Consumers'
    },
    'FEDFUNDS': {
        'id': 'FEDFUNDS',
        'title': 'Federal Funds Rate (%)',
        'min': 0, 'max': 10,
        'ranges': [2, 5, 10],
        'color': '#d62728',
        'description': 'Effective Federal Funds Rate'
    },
    'DGS10': {
        'id': 'DGS10',
        'title': '10-Year Treasury Rate (%)',
        'min': 0, 'max': 8,
        'ranges': [2, 4, 8],
        'color': '#9467bd',
        'description': '10-Year Treasury Constant Maturity'
    },
    'M2SL': {
        'id': 'M2SL',
        'title': 'M2 Money Supply (Billions $)',
        'min': 0, 'max': 25000,
        'ranges': [8000, 16000, 25000],
        'color': '#8c564b',
        'description': 'M2 Money Stock'
    },
    'MORTGAGE30US': {
        'id': 'MORTGAGE30US',
        'title': '30-Yr Mortgage Rate (%)',
        'min': 0, 'max': 12,
        'ranges': [3, 6, 12],
        'color': '#e377c2',
        'description': '30-Year Fixed Rate Mortgage'
    },
    'DEXUSEU': {
        'id': 'DEXUSEU',
        'title': 'USD/EUR Exchange Rate',
        'min': 0, 'max': 2,
        'ranges': [0.8, 1.2, 2.0],
        'color': '#7f7f7f',
        'description': 'US Dollar to Euro Rate'
    },
    'TOTALSA': {
        'id': 'TOTALSA',
        'title': 'Vehicle Sales (Millions)',
        'min': 0, 'max': 25,
        'ranges': [10, 17, 25],
        'color': '#bcbd22',
        'description': 'Total Vehicle Sales'
    },
    'HOUST': {
        'id': 'HOUST',
        'title': 'Housing Starts (Thousands)',
        'min': 0, 'max': 2500,
        'ranges': [800, 1500, 2500],
        'color': '#17becf',
        'description': 'New Housing Units Started'
    },
    'PAYEMS': {
        'id': 'PAYEMS',
        'title': 'Nonfarm Payrolls (Thousands)',
        'min': 100000, 'max': 160000,
        'ranges': [130000, 145000, 160000],
        'color': '#ff5733',
        'description': 'Total Nonfarm Employment'
    },
    'PPIACO': {
        'id': 'PPIACO',
        'title': 'Producer Price Index',
        'min': 0, 'max': 350,
        'ranges': [150, 250, 350],
        'color': '#33ff57',
        'description': 'PPI All Commodities'
    }
}

# ============================================
# DEMO DATA (Backup)
# ============================================
DEMO_DATA = {
    'GDP': {'value': 27357.0, 'previous': 26972.0, 'date': '2024-01-01'},
    'UNRATE': {'value': 4.1, 'previous': 3.9, 'date': '2024-06-01'},
    'CPIAUCSL': {'value': 314.2, 'previous': 312.1, 'date': '2024-06-01'},
    'FEDFUNDS': {'value': 5.33, 'previous': 5.33, 'date': '2024-06-01'},
    'DGS10': {'value': 4.25, 'previous': 4.50, 'date': '2024-06-01'},
    'M2SL': {'value': 20870.0, 'previous': 20750.0, 'date': '2024-05-01'},
    'MORTGAGE30US': {'value': 6.95, 'previous': 7.03, 'date': '2024-06-01'},
    'DEXUSEU': {'value': 1.07, 'previous': 1.08, 'date': '2024-06-01'},
    'TOTALSA': {'value': 15.8, 'previous': 15.6, 'date': '2024-06-01'},
    'HOUST': {'value': 1277.0, 'previous': 1352.0, 'date': '2024-06-01'},
    'PAYEMS': {'value': 158291.0, 'previous': 157898.0, 'date': '2024-06-01'},
    'PPIACO': {'value': 253.5, 'previous': 251.8, 'date': '2024-06-01'},
}

# ============================================
# DATA FETCH FUNCTION
# ============================================
@st.cache_data(ttl=3600)
def get_fred_data(series_id):
    """FRED API se data fetch karta hai"""
    try:
        params = {
            'series_id': series_id,
            'api_key': FRED_API_KEY,
            'file_type': 'json',
            'sort_order': 'desc',
            'limit': 10
        }
        response = requests.get(BASE_URL, params=params, timeout=10)
        data = response.json()

        if 'observations' in data:
            obs = [o for o in data['observations'] if o['value'] != '.']
            if len(obs) >= 2:
                return {
                    'value': float(obs[0]['value']),
                    'previous': float(obs[1]['value']),
                    'date': obs[0]['date']
                }
            elif len(obs) == 1:
                return {
                    'value': float(obs[0]['value']),
                    'previous': float(obs[0]['value']),
                    'date': obs[0]['date']
                }
    except Exception as e:
        st.write("")  # Silent fail

    return None


def get_data(series_key):
    """Data fetch karo - API ya Demo"""
    series_info = FRED_SERIES[series_key]
    if FRED_API_KEY != "demo":
        result = get_fred_data(series_info['id'])
        if result:
            return result
    return DEMO_DATA.get(series_key, {'value': 0, 'previous': 0, 'date': 'N/A'})

# ============================================
# GAUGE CHART FUNCTION
# ============================================
def create_gauge(title, value, min_val, max_val, ranges, color, date_str, previous_val):
    """Meter/Gauge chart banata hai"""

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        number={
            'font': {'size': 26, 'color': 'white', 'family': 'Arial Black'},
        },
        delta={
            'reference': previous_val,
            'increasing': {'color': '#00ff88'},
            'decreasing': {'color': '#ff4444'},
            'font': {'size': 13}
        },
        title={
            'text': f"<b>{title}</b><br><span style='font-size:10px;color:#888'>{date_str}</span>",
            'font': {'size': 13, 'color': 'white'}
        },
        gauge={
            'axis': {
                'range': [min_val, max_val],
                'tickwidth': 2,
                'tickcolor': "white",
                'tickfont': {'color': 'white', 'size': 9}
            },
            'bar': {'color': color, 'thickness': 0.3},
            'bgcolor': "rgba(0,0,0,0)",
            'borderwidth': 2,
            'bordercolor': "rgba(255,255,255,0.3)",
            'steps': [
                {'range': [min_val, ranges[0]], 'color': 'rgba(0, 255, 0, 0.15)'},
                {'range': [ranges[0], ranges[1]], 'color': 'rgba(255, 255, 0, 0.15)'},
                {'range': [ranges[1], ranges[2]], 'color': 'rgba(255, 0, 0, 0.15)'}
            ],
            'threshold': {
                'line': {'color': "white", 'width': 3},
                'thickness': 0.8,
                'value': value
            }
        }
    ))

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': 'white'},
        height=250,
        margin=dict(l=20, r=20, t=70, b=20),
    )

    return fig

# ============================================
# MAIN DASHBOARD
# ============================================

# Header
st.markdown('<div class="main-header">📊 FRED ECONOMIC DASHBOARD</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Federal Reserve Economic Data - Live Meter Gauges</div>', unsafe_allow_html=True)

# Refresh Button
col_left, col_center, col_right = st.columns([4, 2, 4])
with col_center:
    refresh = st.button("🔄 Refresh Data", use_container_width=True)

if refresh:
    st.cache_data.clear()

# Status
data_source = "🟢 Live FRED API" if FRED_API_KEY != "demo" else "🟡 Demo Data (Add API key for live data)"
st.markdown(f'<div class="sub-header">{data_source} | Updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>', unsafe_allow_html=True)

# ============================================
# RENDER GAUGES IN GRID (4 columns)
# ============================================
series_keys = list(FRED_SERIES.keys())

for row_start in range(0, len(series_keys), 4):
    row_keys = series_keys[row_start:row_start + 4]
    cols = st.columns(len(row_keys))

    for i, key in enumerate(row_keys):
        series = FRED_SERIES[key]
        data = get_data(key)

        with cols[i]:
            st.markdown('<div class="gauge-card">', unsafe_allow_html=True)

            fig = create_gauge(
                title=series['title'],
                value=data['value'],
                min_val=series['min'],
                max_val=series['max'],
                ranges=series['ranges'],
                color=series['color'],
                date_str=data['date'],
                previous_val=data['previous']
            )

            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

            st.markdown(f'<div class="description-text">{series["description"]}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# FOOTER
# ============================================
st.markdown("---")
st.markdown('<div class="legend-text">🟢 Green Zone = Low | 🟡 Yellow Zone = Medium | 🔴 Red Zone = High</div>', unsafe_allow_html=True)
st.markdown('<div class="footer-text">Data Source: Federal Reserve Bank of St. Louis (FRED) | Built with Streamlit & Plotly</div>', unsafe_allow_html=True)
