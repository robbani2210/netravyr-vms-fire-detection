# import streamlit as st
# import pandas as pd
# import altair as alt
# import sqlite3
# import time
# from datetime import datetime, timedelta

# # === KONFIGURASI DASAR ===
# st.title("Thermal Monitoring")
# # st.caption("Menampilkan video RTSP + grafik suhu ROI — cache 1 hari, tampil data beberapa menit terakhir (auto-hide ROI jika tidak update 10 detik).")

# DB_FILE = r"C:\Users\ROBBANI\Downloads\netraMVA\Camera Hanwha\Dashboard\Design_2\temperature.db"
# REFRESH_INTERVAL = 5  # detik
# ACTIVE_TIMEOUT_SECONDS = 10  # ROI dianggap tidak aktif jika >10 detik tanpa data

# # ============================================================
# # 🔹 Fungsi: Baca data 1 hari terakhir dari SQLite
# # ============================================================
# def load_recent_data():
#     try:
#         conn = sqlite3.connect(DB_FILE)
#         query = """
#             SELECT timestamp, roi_index, area_name, avg_temp, min_temp, max_temp
#             FROM temperature
#             WHERE timestamp >= datetime('now', '-1 day')
#             ORDER BY timestamp ASC
#         """
#         df = pd.read_sql_query(query, conn)
#         conn.close()

#         if not df.empty:
#             df["timestamp"] = pd.to_datetime(df["timestamp"])
#         return df
#     except Exception as e:
#         st.error(f"Error loading data: {e}")
#         return pd.DataFrame()

# # ============================================================
# # 🔹 Fungsi: Dapatkan ROI aktif dalam 10 detik terakhir
# # ============================================================
# def get_active_rois(df):
#     if df.empty:
#         return []
#     now = datetime.now()
#     valid_rois = []
#     for roi_index, roi_df in df.groupby("roi_index"):
#         roi_df = roi_df.dropna(subset=["avg_temp", "min_temp", "max_temp"], how="all")
#         if roi_df.empty:
#             continue
#         last_timestamp = roi_df["timestamp"].max()
#         if (now - last_timestamp) <= timedelta(seconds=ACTIVE_TIMEOUT_SECONDS):
#             valid_rois.append(roi_index)
#     return sorted(valid_rois)

# # ============================================================
# # 🔹 Dropdown kamera dan durasi fokus grafik
# # ============================================================
# col_opt1, col_opt2 = st.columns([2, 1])
# with col_opt1:
#     camera_choice = st.selectbox("Pilih Kamera:", ["Camera 1", "Camera 2", "Camera 3"])
# with col_opt2:
#     duration_choice = st.selectbox("Durasi Fokus Grafik (menit):", [1, 3, 5, 30, 60], index=1)

# # st.write(f"Menampilkan data untuk **{camera_choice}**, fokus **{duration_choice} menit terakhir**.")

# # ============================================================
# # 🔹 Video Stream di atas
# # ============================================================
# # st.subheader("🎥 Live Video Stream")

# VIDEO_URLS = {
#     "Camera 1": "http://admin:P@ssw0rd@192.168.100.118:554/profile2/media.smp",
#     "Camera 2": "http://admin:P@ssw0rd@192.168.100.119:554/profile2/media.smp",
#     "Camera 3": "http://admin:P@ssw0rd@192.168.100.120:554/profile2/media.smp"
# }
# VIDEO_URL = VIDEO_URLS.get(camera_choice, "")

# try:
#     st.video(VIDEO_URL)
# except Exception as e:
#     st.error(f"Tidak dapat menampilkan video stream: {e}")
#     st.info("Pastikan koneksi jaringan dan kredensial RTSP benar")

# st.markdown("---")

# # ============================================================
# # 🔹 Grafik Suhu per ROI
# # ============================================================
# # st.subheader("📈 Grafik Suhu per ROI")

# graph_placeholder = st.empty()

# # 🔁 Loop refresh setiap REFRESH_INTERVAL detik
# while True:
#     with graph_placeholder.container():
#         df = load_recent_data()

#         if df.empty:
#             st.warning("Belum ada data di database (temperature.db).")
#             time.sleep(REFRESH_INTERVAL)
#             st.rerun()

#         latest_time = df["timestamp"].max()
#         st.caption(f"🕓 Data terakhir: {latest_time.strftime('%Y-%m-%d %H:%M:%S')} | Auto-refresh: {REFRESH_INTERVAL}s")

#         active_rois = get_active_rois(df)
#         if not active_rois:
#             st.warning("Tidak ada ROI aktif (tidak ada data 10 detik terakhir).")
#             time.sleep(REFRESH_INTERVAL)
#             st.rerun()

#         # 🔹 Buat tab untuk setiap ROI aktif
#         tab_labels = []
#         for roi_index in active_rois:
#             try:
#                 area_name = df.loc[df["roi_index"] == roi_index, "area_name"].dropna().iloc[-1]
#             except IndexError:
#                 area_name = "?"
#             tab_labels.append(f"ROI {roi_index} ({area_name})")

#         tabs = st.tabs(tab_labels)

#         for tab, roi_index in zip(tabs, active_rois):
#             with tab:
#                 roi_df = df[df["roi_index"] == roi_index].copy()
#                 roi_df = roi_df.dropna(subset=["avg_temp", "min_temp", "max_temp"], how="all")

#                 if roi_df.empty:
#                     st.warning(f"Tidak ada data valid untuk ROI {roi_index}")
#                     continue

#                 area_name = roi_df["area_name"].dropna().iloc[-1] if not roi_df["area_name"].isnull().all() else "Unknown"

#                 # 🔹 Fokus ke durasi pilihan (mis. 1, 3, 5, 30, 60 menit)
#                 cutoff_time = datetime.now() - timedelta(minutes=duration_choice)
#                 roi_recent = roi_df[roi_df["timestamp"] >= cutoff_time]
#                 if roi_recent.empty:
#                     roi_recent = roi_df.tail(50)

#                 # 🔹 MONITOR SUHU DI ATAS GRAFIK
#                 latest = roi_recent.iloc[-1]
#                 cols = st.columns(3)
#                 cols[0].metric("Rata-rata", f"{latest['avg_temp']:.1f}°C" if pd.notna(latest['avg_temp']) else "N/A")
#                 cols[1].metric("Minimum", f"{latest['min_temp']:.1f}°C" if pd.notna(latest['min_temp']) else "N/A")
#                 cols[2].metric("Maksimum", f"{latest['max_temp']:.1f}°C" if pd.notna(latest['max_temp']) else "N/A")

#                 # 🔹 Grafik suhu
#                 chart_df = roi_df.melt(
#                     id_vars=["timestamp"],
#                     value_vars=["avg_temp", "min_temp", "max_temp"],
#                     var_name="Tipe",
#                     value_name="Suhu"
#                 ).dropna(subset=["Suhu"])

#                 if not chart_df.empty:
#                     y_min = max(20, chart_df["Suhu"].min() - 2)
#                     y_max = min(60, chart_df["Suhu"].max() + 2)

#                     chart = (
#                         alt.Chart(chart_df)
#                         .mark_line(point=True, size=2)
#                         .encode(
#                             x=alt.X(
#                                 "timestamp:T",
#                                 title="Waktu",
#                                 axis=alt.Axis(format="%H:%M:%S", labelAngle=-45),
#                                 scale=alt.Scale(domain=[roi_recent["timestamp"].min(), roi_recent["timestamp"].max()])
#                             ),
#                             y=alt.Y("Suhu:Q", scale=alt.Scale(domain=[y_min, y_max]), title="Suhu (°C)"),
#                             color=alt.Color(
#                                 "Tipe:N",
#                                 title="Jenis Suhu",
#                                 scale=alt.Scale(
#                                     domain=["avg_temp", "min_temp", "max_temp"],
#                                     range=["#1f77b4", "#ff7f0e", "#d62728"]
#                                 )
#                             ),
#                             tooltip=["timestamp:T", "Tipe:N", "Suhu:Q"]
#                         )
#                         .properties(width="container", height=350)
#                         .interactive()
#                     )

#                     st.altair_chart(chart, use_container_width=True)

#     time.sleep(REFRESH_INTERVAL)
#     st.rerun()


import streamlit as st
import pandas as pd
import altair as alt
import sqlite3
import threading
import time
from datetime import datetime, timedelta

# === KONFIGURASI DASAR ===
DB_FILE = r"C:\Users\ROBBANI\Downloads\netraMVA\Camera Hanwha\Dashboard\Design_2\temperature.db"
REFRESH_INTERVAL = 5  # detik
BATCH_SIZE = 10       # ambil 10 data baru per interval

# ============================================================
# 🔹 Fungsi ambil data dari database
# ============================================================
def load_data(start_index=0, limit=BATCH_SIZE):
    try:
        conn = sqlite3.connect(DB_FILE)
        query = f"""
            SELECT timestamp, roi_index, area_name, avg_temp, min_temp, max_temp
            FROM temperature
            ORDER BY timestamp ASC
            LIMIT {limit} OFFSET {start_index}
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        if not df.empty:
            df["timestamp"] = pd.to_datetime(df["timestamp"])
        return df
    except Exception as e:
        st.error(f"Error membaca DB: {e}")
        return pd.DataFrame()

# ============================================================
# 🔹 Inisialisasi session_state
# ============================================================
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame()
if "offset" not in st.session_state:
    st.session_state.offset = 0
if "running" not in st.session_state:
    st.session_state.running = True

# ============================================================
# 🔹 Thread background untuk update data tiap beberapa detik
# ============================================================
def background_updater():
    while st.session_state.running:
        new_df = load_data(st.session_state.offset, BATCH_SIZE)
        if not new_df.empty:
            st.session_state.data = pd.concat([st.session_state.data, new_df], ignore_index=True)
            st.session_state.offset += len(new_df)
        time.sleep(REFRESH_INTERVAL)

# Jalankan thread sekali saja
if "thread_started" not in st.session_state:
    thread = threading.Thread(target=background_updater, daemon=True)
    thread.start()
    st.session_state.thread_started = True

# ============================================================
# 🔹 UI Streamlit
# ============================================================

st.title("📊 Real-Time Temperature Monitor")

if st.session_state.data.empty:
    st.warning("Menunggu data dari database...")
else:
    df = st.session_state.data.copy()

    # Ambil ROI unik
    all_rois = sorted(df["roi_index"].unique())
    tabs = st.tabs([f"ROI {r}" for r in all_rois])

    for tab, roi_index in zip(tabs, all_rois):
        with tab:
            roi_df = df[df["roi_index"] == roi_index]
            if roi_df.empty:
                st.info("Belum ada data untuk ROI ini.")
                continue

            latest = roi_df.iloc[-1]
            cols = st.columns(3)
            cols[0].metric("Rata-rata", f"{latest['avg_temp']:.1f}°C" if pd.notna(latest['avg_temp']) else "N/A")
            cols[1].metric("Minimum", f"{latest['min_temp']:.1f}°C" if pd.notna(latest['min_temp']) else "N/A")
            cols[2].metric("Maksimum", f"{latest['max_temp']:.1f}°C" if pd.notna(latest['max_temp']) else "N/A")

            # Grafik
            chart_df = roi_df.melt(
                id_vars=["timestamp"],
                value_vars=["avg_temp", "min_temp", "max_temp"],
                var_name="Tipe",
                value_name="Suhu"
            ).dropna(subset=["Suhu"])

            if not chart_df.empty:
                chart = (
                    alt.Chart(chart_df)
                    .mark_line(point=True, size=2)
                    .encode(
                        x=alt.X("timestamp:T", title="Waktu"),
                        y=alt.Y("Suhu:Q", title="Suhu (°C)"),
                        color="Tipe:N",
                        tooltip=["timestamp:T", "Tipe:N", "Suhu:Q"]
                    )
                    .properties(width="container", height=350)
                )
                st.altair_chart(chart, use_container_width=True)

# ============================================================
# 🔹 Tombol Stop
# ============================================================
if st.button("🛑 Hentikan Update"):
    st.session_state.running = False
    st.success("Background update dihentikan.")





