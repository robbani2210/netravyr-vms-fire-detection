import streamlit as st
from datetime import datetime
from babel.dates import format_datetime
from streamlit_js_eval import streamlit_js_eval
from streamlit_autorefresh import st_autorefresh

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="NetraFyr Dashboard",
    layout="wide",
)

# --- CSS UNTUK SIDEBAR & JAM ---
st.markdown("""
    <style>
        div.block-container {
            padding-top: 1rem !important;
        }
        section[data-testid="stSidebar"] {
            background-color: #fafafa;
            border-right: 1px solid #e6e6e6;
            padding: 1.5rem 1rem 5rem 1rem;
            position: relative;
            height: 100vh;
            overflow-y: auto;
        }
        .sidebar-footer {
            position: fixed;
            bottom: 1rem;
            left: 0;
            width: 15rem;
            text-align: center;
            font-size: 0.9rem;
            color: #333;
            background-color: #fafafa;
            padding: 0.6rem 0.3rem;
        }
        .sidebar-footer strong {
            display: block;
            font-weight: 600;
        }
        .sidebar-footer time {
            font-size: 1.3rem;
            font-weight: 700;
            color: #d03a00;
        }
    </style>
""", unsafe_allow_html=True)


# --- NAVIGASI HALAMAN ---
home_page = st.Page(page="views/home.py", title="Home", icon="🏠", default=True)

temp_cam1 = st.Page(page="views/temperature/camera1.py", title="Camera 1", icon=":material/videocam:", url_path="temperature_cam1")
temp_cam2 = st.Page(page="views/temperature/camera2.py", title="Camera 2", icon=":material/videocam:", url_path="temperature_cam2")
temp_cam3 = st.Page(page="views/temperature/camera3.py", title="Camera 3", icon=":material/videocam:", url_path="temperature_cam3")

fire_cam1 = st.Page(page="views/fire_detection/camera1.py", title="Camera 1", icon=":material/local_fire_department:", url_path="fire_cam1")
fire_cam2 = st.Page(page="views/fire_detection/camera2.py", title="Camera 2", icon=":material/local_fire_department:", url_path="fire_cam2")
fire_cam3 = st.Page(page="views/fire_detection/camera3.py", title="Camera 3", icon=":material/local_fire_department:", url_path="fire_cam3")

report_page = st.Page(page="views/alerts.py", title="Report", icon="📃", url_path="report")
account_page = st.Page(page="views/account.py", title="System Configuration", icon="👨‍💻", url_path="account")

pg = st.navigation({
    "NetraFyr Dashboard": [home_page],
    "📈 Temperature Monitoring": [temp_cam1, temp_cam2, temp_cam3],
    "🔥 Flame Detection": [fire_cam1, fire_cam2, fire_cam3],
    "⚙️ Settings": [report_page, account_page],
})


# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # Jalankan autorefresh setiap 1 detik (1000 ms)
    st_autorefresh(interval=1000, key="clock_refresh")

    # Ambil waktu dari browser agar mengikuti zona waktu lokal
    js_time = streamlit_js_eval(js_expressions="new Date().toLocaleString('id-ID')", key="get_time")

    if js_time:
        try:
            # Parsing hasil JS (bisa pakai '.' sebagai pemisah waktu)
            now = datetime.strptime(js_time, "%d/%m/%Y %H.%M.%S")
        except Exception:
            now = datetime.now()

        waktu_id = format_datetime(now, "EEEE, d MMMM yyyy HH:mm:ss", locale="id_ID")
        tanggal, waktu = waktu_id.rsplit(" ", 1)

        st.markdown(
            f"""
            <div class="sidebar-footer">
                <strong>{tanggal}</strong>
                <time>{waktu}</time>
            </div>
            """,
            unsafe_allow_html=True
        )


# --- JALANKAN HALAMAN YANG DIPILIH ---
pg.run()
