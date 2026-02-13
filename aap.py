import streamlit as st
import plotly.graph_objects as go
import requests
from datetime import datetime
import math

# ============================================
# PAGE CONFIG
# ============================================
st.set_page_config(
    page_title="FRED Economic Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================
# MODERN CSS STYLING
# ============================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;800;900&display=swap');

    /* Main Background */
    .stApp {
        background: linear-gradient(135deg, #0a0a1a 0%, #0d1117 50%, #0a0a1a 100%);
        font-family: 'Inter', sans-serif;
    }

    /* Hide Streamlit Defaults */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
        max-width: 100%;
    }

    /* Animated Header */
    .main-title {
        text-align: center;
        font-family: 'Orbitron', monospace;
        font-size: 42px;
        font-weight: 900;
        background: linear-gradient(90deg, #00d4ff, #7b2ff7, #ff2d55, #00d4ff);
        background-size: 300% 300%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: gradient-shift 4s ease infinite;
        padding: 15px 0 0 0;
        letter-spacing: 3px;
    }

    @keyframes gradient-shift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    .subtitle {
        text-align: center;
        color: #4a5568;
        font-size: 14px;
        font-weight: 400;
        letter-spacing: 4px;
        text-transform: uppercase;
        margin-bottom: 5px;
    }

    /* Glowing Line */
    .glow-line {
        width: 200px;
        height: 2px;
        background: linear-gradient(90deg, transparent, #00d4ff, transparent);
        margin: 10px auto 20px auto;
        border-radius: 2px;
        animation: glow-pulse 2s ease-in-out infinite;
    }

    @keyframes glow-pulse {
        0%, 100% { opacity: 0.5; width: 200px; }
        50% { opacity: 1; width: 300px; }
    }

    /* Status Badge */
    .status-badge {
        text-align: center;
        padding: 8px 20px;
        border-radius: 50px;
        display: inline-block;
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 1px;
        margin: 5px auto;
    }

    .status-live {
        background: rgba(0, 255, 136, 0.1);
        border: 1px solid rgba(0, 255, 136, 0.3);
        color: #00ff88;
    }

    .status-demo {
        background: rgba(255, 193, 7, 0.1);
        border: 1px solid rgba(255, 193, 7, 0.3);
        color: #ffc107;
    }

    /* Gauge Card */
    .gauge-card {
        background: linear-gradient(145deg, rgba(20, 25, 40, 0.9), rgba(15, 18, 30, 0.95));
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.06);
        padding: 15px 10px 10px 10px;
        margin: 8px 4px;
        box-shadow:
            0 8px 32px rgba(0, 0, 0, 0.4),
            inset 0 1px 0 rgba(255, 255, 255, 0.05);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }

    .gauge-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, var(--card-accent, #00d4ff), transparent);
        opacity: 0.6;
    }

    .gauge-card:hover {
        transform: translateY(-5px);
        border-color: rgba(255, 255, 255, 0.12);
        box-shadow:
            0 16px 48px rgba(0, 0, 0, 0.5),
            0 0 30px rgba(0, 212, 255, 0.08);
    }

    /* Value Display */
    .value-display {
        text-align: center;
        font-family: 'Orbitron', monospace;
        font-size: 28px;
        font-weight: 800;
        color: #ffffff;
        text-shadow: 0 0 20px rgba(255, 255, 255, 0.15);
        margin: 5px 0;
    }

    /* Change Indicator */
    .change-up {
        color: #00ff88;
        font-size: 13px;
        font-weight: 600;
        text-align: center;
    }

    .change-down {
        color: #ff4757;
        font-size: 13px;
        font-weight: 600;
        text-align: center;
    }

    /* Series Title */
    .series-title {
        text-align: center;
        color: #8892b0;
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-top: 5px;
        padding: 0 5px;
    }

    /* Date Badge */
    .date-badge {
        text-align: center;
        color: #4a5568;
        font-size: 10px;
        font-weight: 400;
        margin-top: 2px;
    }

    /* Section Title */
    .section-title {
        color: #00d4ff;
        font-family: 'Orbitron', monospace;
        font-size: 14px;
        font-weight: 700;
        letter-spacing: 3px;
        text-transform: uppercase;
        padding: 15px 0 5px 10px;
        border-left: 3px solid #00d4ff;
        margin: 20px 0 10px 0;
    }

    /* Footer */
    .footer {
        text-align: center;
        color: #2d3748;
        font-size: 11px;
        padding: 30px 0;
        letter-spacing: 1px;
    }

    .legend-bar {
        text-align: center;
        padding: 15px;
        background: rgba(255,255,255,0.02);
        border-radius: 15px;
        margin: 20px auto;
        max-width: 700px;
        border: 1px solid rgba(255,255,255,0.04);
    }

    .legend-item {
        display: inline-block;
        margin: 0 15px;
        font-size: 12px;
        color: #666;
    }

    /* Streamlit Button Override */
    .stButton > button {
        background: linear-gradient(135deg, #00d4ff, #7b2ff7) !important;
        color: white !important;
        border: none !important;
        border-radius: 50px !important;
        padding: 10px 30px !important;
        font-weight: 700 !important;
        font-size: 14px !important;
        letter-spacing: 1px !important;
        box-shadow: 0 4px 20px rgba(0, 212, 255, 0.3) !important;
        transition: all 0.3s ease !important;
    }

    .stButton > button:hover {
        box-shadow: 0 6px 30px rgba(0, 212, 255, 0.5) !important;
        transform: translateY(-2px) !important;
    }

    /* Divider */
    .modern-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.06), transparent);
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# API KEY
# ============================================
FRED_API_KEY = "demo"
try:
    FRED_API_KEY = st.secrets["FRED_API_KEY"]
except Exception:
    FRED_API_KEY = "demo"

BASE_URL = "https://api.stlouisfed.org/fred/series/observations"

# ============================================
# SERIES DEFINITIONS WITH CATEGORIES
# ============================================
CATEGORIES = {
    "💰 GROWTH & OUTPUT": ['GDP', 'PAYEMS', 'TOTALSA'],
    "📈 RATES & POLICY": ['FEDFUNDS', 'DGS10', 'MORTGAGE30US'],
    "🏷️ PRICES & INFLATION": ['CPIAUCSL', 'PPIACO', 'DEXUSEU'],
    "🏗️ MONEY & HOUSING": ['M2SL', 'HOUST', 'UNRATE'],
}

FRED_SERIES = {
    'GDP': {
        'id': 'GDP', 'title': 'GDP',
        'subtitle': 'Gross Domestic Product (Billions $)',
        'min': 0, 'max': 30000,
        'ranges': [10000, 20000, 30000],
        'color': '#00d4ff', 'icon': '💵',
        'format': ',.0f', 'suffix': 'B'
    },
    'UNRATE': {
        'id': 'UNRATE', 'title': 'UNEMPLOYMENT',
        'subtitle': 'Civilian Unemployment Rate',
        'min': 0, 'max': 15,
        'ranges': [3, 6, 15],
        'color': '#ff6b6b', 'icon': '👷',
        'format': '.1f', 'suffix': '%'
    },
    'CPIAUCSL': {
        'id': 'CPIAUCSL', 'title': 'CPI INDEX',
        'subtitle': 'Consumer Price Index',
        'min': 0, 'max': 350,
        'ranges': [150, 250, 350],
        'color': '#ffd93d', 'icon': '🏷️',
        'format': '.1f', 'suffix': ''
    },
    'FEDFUNDS': {
        'id': 'FEDFUNDS', 'title': 'FED RATE',
        'subtitle': 'Federal Funds Rate',
        'min': 0, 'max': 10,
        'ranges': [2, 5, 10],
        'color': '#ff2d55', 'icon': '🏦',
        'format': '.2f', 'suffix': '%'
    },
    'DGS10': {
        'id': 'DGS10', 'title': '10Y TREASURY',
        'subtitle': '10-Year Treasury Rate',
        'min': 0, 'max': 8,
        'ranges': [2, 4, 8],
        'color': '#bf5af2', 'icon': '📜',
        'format': '.2f', 'suffix': '%'
    },
    'M2SL': {
        'id': 'M2SL', 'title': 'M2 MONEY',
        'subtitle': 'M2 Money Stock (Billions $)',
        'min': 0, 'max': 25000,
        'ranges': [8000, 16000, 25000],
        'color': '#30d158', 'icon': '💰',
        'format': ',.0f', 'suffix': 'B'
    },
    'MORTGAGE30US': {
        'id': 'MORTGAGE30US', 'title': 'MORTGAGE 30Y',
        'subtitle': '30-Year Mortgage Rate',
        'min': 0, 'max': 12,
        'ranges': [3, 6, 12],
        'color': '#ff9f0a', 'icon': '🏠',
        'format': '.2f', 'suffix': '%'
    },
    'DEXUSEU': {
        'id': 'DEXUSEU', 'title': 'USD/EUR',
        'subtitle': 'Dollar to Euro Rate',
        'min': 0, 'max': 2,
        'ranges': [0.8, 1.2, 2.0],
        'color': '#64d2ff', 'icon': '💱',
        'format': '.4f', 'suffix': ''
    },
    'TOTALSA': {
        'id': 'TOTALSA', 'title': 'AUTO SALES',
        'subtitle': 'Total Vehicle Sales (Millions)',
        'min': 0, 'max': 25,
        'ranges': [10, 17, 25],
        'color': '#5e5ce6', 'icon': '🚗',
        'format': '.1f', 'suffix': 'M'
    },
    'HOUST': {
        'id': 'HOUST', 'title': 'HOUSING',
        'subtitle': 'Housing Starts (Thousands)',
        'min': 0, 'max': 2500,
        'ranges': [800, 1500, 2500],
        'color': '#ac8e68', 'icon': '🏗️',
        'format': ',.0f', 'suffix': 'K'
    },
    'PAYEMS': {
        'id': 'PAYEMS', 'title': 'PAYROLLS',
        'subtitle': 'Nonfarm Payrolls (Thousands)',
        'min': 100000, 'max': 160000,
        'ranges': [130000, 145000, 160000],
        'color': '#66d4cf', 'icon': '📋',
        'format': ',.0f', 'suffix': 'K'
    },
    'PPIACO': {
        'id': 'PPIACO', 'title': 'PPI INDEX',
        'subtitle': 'Producer Price Index',
        'min': 0, 'max': 350,
        'ranges': [150, 250, 350],
        'color': '#ff375f', 'icon': '🏭',
        'format': '.1f', 'suffix': ''
    }
}

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
# DATA FUNCTIONS
# ============================================
@st.cache_data(ttl=3600)
def get_fred_data(series_id):
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
                val = float(obs[0]['value'])
                return {'value': val, 'previous': val, 'date': obs[0]['date']}
    except Exception:
        pass
    return None

def get_data(key):
    info = FRED_SERIES[key]
    if FRED_API_KEY != "demo":
        result = get_fred_data(info['id'])
        if result:
            return result
    return DEMO_DATA.get(key, {'value': 0, 'previous': 0, 'date': 'N/A'})

# ============================================
# MODERN GAUGE CHART
# ============================================
def create_modern_gauge(title, value, min_val, max_val, ranges, color, date_str, previous_val, icon, suffix):
    
    percentage = ((value - min_val) / (max_val - min_val)) * 100
    percentage = max(0, min(100, percentage))
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        number={
            'font': {
                'size': 32,
                'color': 'white',
                'family': 'Inter, Arial Black'
            },
            'suffix': suffix if suffix in ['%', ''] else '',
        },
        delta={
            'reference': previous_val,
            'increasing': {'color': '#00ff88', 'symbol': '▲ '},
            'decreasing': {'color': '#ff4757', 'symbol': '▼ '},
            'font': {'size': 14, 'family': 'Inter'},
            'position': 'bottom'
        },
        title={
            'text': "",
            'font': {'size': 1}
        },
        gauge={
            'axis': {
                'range': [min_val, max_val],
                'tickwidth': 1,
                'tickcolor': "rgba(255,255,255,0.2)",
                'tickfont': {'color': 'rgba(255,255,255,0.4)', 'size': 8, 'family': 'Inter'},
                'tickmode': 'auto',
                'nticks': 6,
            },
            'bar': {
                'color': color,
                'thickness': 0.35,
                'line': {'width': 0}
            },
            'bgcolor': "rgba(255,255,255,0.03)",
            'borderwidth': 0,
            'steps': [
                {
                    'range': [min_val, ranges[0]],
                    'color': 'rgba(0, 255, 136, 0.08)'
                },
                {
                    'range': [ranges[0], ranges[1]],
                    'color': 'rgba(255, 214, 0, 0.08)'
                },
                {
                    'range': [ranges[1], ranges[2]],
                    'color': 'rgba(255, 45, 85, 0.08)'
                }
            ],
            'threshold': {
                'line': {
                    'color': color,
                    'width': 3
                },
                'thickness': 0.85,
                'value': value
            }
        }
    ))

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': 'white', 'family': 'Inter'},
        height=220,
        margin=dict(l=25, r=25, t=30, b=15),
    )

    return fig

# ============================================
# HEADER
# ============================================
st.markdown('<div class="main-title">📊 FRED DASHBOARD</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Federal Reserve Economic Data</div>', unsafe_allow_html=True)
st.markdown('<div class="glow-line"></div>', unsafe_allow_html=True)

# Status & Refresh
c1, c2, c3 = st.columns([3, 2, 3])
with c2:
    if st.button("⚡ REFRESH DATA", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

if FRED_API_KEY != "demo":
    badge_class = "status-badge status-live"
    badge_text = "● LIVE DATA"
else:
    badge_class = "status-badge status-demo"
    badge_text = "● DEMO MODE"

now_str = datetime.now().strftime("%b %d, %Y • %H:%M UTC")
st.markdown(f'''
<div style="text-align:center; margin: 10px 0 5px 0;">
    <span class="{badge_class}">{badge_text}</span>
</div>
<div style="text-align:center; color:#4a5568; font-size:11px; letter-spacing:1px;">{now_str}</div>
''', unsafe_allow_html=True)

st.markdown('<div class="modern-divider"></div>', unsafe_allow_html=True)

# ============================================
# RENDER GAUGES BY CATEGORY
# ============================================
for category_name, series_keys in CATEGORIES.items():
    st.markdown(f'<div class="section-title">{category_name}</div>', unsafe_allow_html=True)

    cols = st.columns(len(series_keys))

    for i, key in enumerate(series_keys):
        series = FRED_SERIES[key]
        data = get_data(key)
        val = data['value']
        prev = data['previous']
        change = val - prev
        change_pct = (change / prev * 100) if prev != 0 else 0

        with cols[i]:
            # Card Start
            st.markdown(f'<div class="gauge-card" style="--card-accent: {series["color"]};">', unsafe_allow_html=True)

            # Icon + Title
            st.markdown(f'''
                <div style="text-align:center; font-size:24px; margin-bottom:2px;">{series["icon"]}</div>
                <div style="text-align:center; color:{series["color"]}; font-family:Orbitron,monospace; font-size:12px; font-weight:700; letter-spacing:2px;">{series["title"]}</div>
            ''', unsafe_allow_html=True)

            # Gauge
            fig = create_modern_gauge(
                title=series['title'],
                value=val,
                min_val=series['min'],
                max_val=series['max'],
                ranges=series['ranges'],
                color=series['color'],
                date_str=data['date'],
                previous_val=prev,
                icon=series['icon'],
                suffix=series.get('suffix', '')
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

            # Change Indicator
            if change >= 0:
                arrow = "▲"
                ch_class = "change-up"
            else:
                arrow = "▼"
                ch_class = "change-down"

            st.markdown(f'''
                <div class="{ch_class}">{arrow} {abs(change):.2f} ({abs(change_pct):.1f}%)</div>
                <div class="series-title">{series["subtitle"]}</div>
                <div class="date-badge">📅 {data["date"]}</div>
            ''', unsafe_allow_html=True)

            # Card End
            st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# LEGEND & FOOTER
# ============================================
st.markdown('<div class="modern-divider"></div>', unsafe_allow_html=True)

st.markdown('''
<div class="legend-bar">
    <span class="legend-item">🟢 <span style="color:#00ff88">Low Zone</span></span>
    <span class="legend-item">🟡 <span style="color:#ffd600">Medium Zone</span></span>
    <span class="legend-item">🔴 <span style="color:#ff2d55">High Zone</span></span>
    <span class="legend-item">▲ <span style="color:#00ff88">Increase</span></span>
    <span class="legend-item">▼ <span style="color:#ff4757">Decrease</span></span>
</div>
''', unsafe_allow_html=True)

st.markdown('''
<div class="footer">
    FRED ECONOMIC DASHBOARD • DATA SOURCE: FEDERAL RESERVE BANK OF ST. LOUIS<br>
    BUILT WITH STREAMLIT & PLOTLY • REAL-TIME ECONOMIC INDICATORS
</div>
''', unsafe_allow_html=True)
