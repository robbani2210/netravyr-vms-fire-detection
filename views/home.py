import streamlit as st
from datetime import datetime


# --- CSS STYLING ---
st.markdown("""
<style>
    div.block-container {
        padding-top: 1rem !important;
    }
    .main > div {
        padding-top: 0rem !important;
    }
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Inter', sans-serif;
    }
    .header-title {
        font-size: 2.3rem;
        font-weight: 600;
        margin-bottom: 0.3rem;
    }
    .header-sub {
        color: #6b7280;
        font-size: 0.95rem;
        margin-bottom: 1rem;
        line-height: 1.5;
    }

    /* STATUS CARD */
    .status-card {
        background: #f9fafb;
        border-radius: 14px;
        padding: 1.2rem 1.4rem;
        box-shadow: 0 2px 6px rgba(0,0,0,0.05);
        height: 100px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        text-align: center;
        transition: transform 0.15s ease;
        margin: 0.8rem 0rem;
    }
    .status-card:hover {
        transform: translateY(-3px);
    }
    .status-title {
        font-size: 0.85rem;
        color: #4b5563;
        margin-bottom: 0.4rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .status-value {
        font-size: 1.6rem;
        font-weight: 600;
        line-height: 1.1;
    }

    /* WARNA CARD */
    .card-blue { border-top: 4px solid #3b82f6; background-color: #e0f2fe; }
    .card-green { border-top: 4px solid #10b981; background-color: #dcfce7; }
    .card-red { border-top: 4px solid #ef4444; background-color: #fee2e2; }

    /* CAMERA CARD */
    .camera-card {
        position: relative;
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 3px 10px rgba(0,0,0,0.08);
        cursor: pointer;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        margin-bottom: 0.5rem;
    }
    .camera-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 6px 15px rgba(0,0,0,0.12);
    }
    .camera-card img {
        width: 100%;
        height: 250px;
        object-fit: cover;
    }
    .camera-overlay {
        position: absolute;
        bottom: 0;
        left: 0;
        width: 100%;
        padding: 1rem 1.2rem;
        background: rgba(0, 0, 0, 0.55);
        color: white;
        font-size: 15px;
        line-height: 1.4;
    }
    .camera-overlay b {
        font-size: 16px;
    }
    a.camera-link {
        text-decoration: none;
        color: inherit;
        display: block;
    }
    
    /* OVERRIDE STREAMLIT DEFAULT SPACING */
    .stHorizontalBlock {
        gap: 1rem !important;
    }
    
    div[data-testid="column"] {
        padding: 0.5rem !important;
    }
    
    /* COMPACT LAYOUT */
    .compact-row {
        margin-bottom: 0.5rem !important;
    }
</style>
""", unsafe_allow_html=True)

# --- JAM ---
now = datetime.now()
day_name = now.strftime("%A")
date_full = now.strftime("%d %B %Y")
time_24h = now.strftime("%H:%M:%S")

# --- STATUS BAR (DAY, DATE, TIME) ---
col1, col2, col3 = st.columns([1, 1.2, 1])
with col1:
    st.markdown(f"""
    <div class="status-card card-blue">
        <div class="status-value">{day_name}</div>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown(f"""
    <div class="status-card card-green">
        <div class="status-value">{date_full}</div>
    </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown(f"""
    <div class="status-card card-red">
        <div class="status-value">{time_24h}</div>
    </div>
    """, unsafe_allow_html=True)

# --- HEADER ---
st.markdown('<div class="header-title">Monitoring Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="header-sub">Pantau suhu dan aktivitas kamera secara real-time di seluruh area industri Anda.</div>', unsafe_allow_html=True)

# --- DATA KAMERA (4 kamera untuk grid 2x2) ---
cameras = [
    {"url": "https://media0.giphy.com/media/3oxHQwdn31M3ddjV3a/giphy.gif", "title": "Camera 1 - Corridor 7A", "temp": "45°C", "status": "Normal", "link": "/temperature_cam1"},
    {"url": "https://media0.giphy.com/media/RuhIAu5P0LO7u/giphy.gif", "title": "Camera 2 - Main Shaft", "temp": "46°C", "status": "Warning", "link": "/temperature_cam2"},
    {"url": "https://media3.giphy.com/media/UBYJ4k7FLULPq/giphy.gif", "title": "Camera 3 - Ventilation Duct", "temp": "47°C", "status": "Normal", "link": "/temperature_cam3"},
    {"url": "https://media1.giphy.com/media/l0HlGSD6Q0eKzowb6/giphy.gif", "title": "Camera 4 - Entrance Area", "temp": "44°C", "status": "Normal", "link": "/temperature_cam1"},
]

# --- GRID 2x2 DENGAN SPACING KOMPAK ---
# Baris pertama - 2 kamera
col1, col2 = st.columns(2)

with col1:
    cam1 = cameras[0]
    st.markdown(f"""
    <a class="camera-link" href="{cam1['link']}">
        <div class="camera-card">
            <img src="{cam1['url']}" alt="{cam1['title']}">
            <div class="camera-overlay">
                <b>{cam1['title']}</b><br>
                Temperature: {cam1['temp']} | Status: {cam1['status']}
            </div>
        </div>
    </a>
    """, unsafe_allow_html=True)

with col2:
    cam2 = cameras[1]
    st.markdown(f"""
    <a class="camera-link" href="{cam2['link']}">
        <div class="camera-card">
            <img src="{cam2['url']}" alt="{cam2['title']}">
            <div class="camera-overlay">
                <b>{cam2['title']}</b><br>
                Temperature: {cam2['temp']} | Status: {cam2['status']}
            </div>
        </div>
    </a>
    """, unsafe_allow_html=True)

# Baris kedua - 2 kamera  
col3, col4 = st.columns(2)

with col3:
    cam3 = cameras[2]
    st.markdown(f"""
    <a class="camera-link" href="{cam3['link']}">
        <div class="camera-card">
            <img src="{cam3['url']}" alt="{cam3['title']}">
            <div class="camera-overlay">
                <b>{cam3['title']}</b><br>
                Temperature: {cam3['temp']} | Status: {cam3['status']}
            </div>
        </div>
    </a>
    """, unsafe_allow_html=True)

with col4:
    cam4 = cameras[3]
    st.markdown(f"""
    <a class="camera-link" href="{cam4['link']}">
        <div class="camera-card">
            <img src="{cam4['url']}" alt="{cam4['title']}">
            <div class="camera-overlay">
                <b>{cam4['title']}</b><br>
                Temperature: {cam4['temp']} | Status: {cam4['status']}
            </div>
        </div>
    </a>
    """, unsafe_allow_html=True)