import streamlit as st
import pandas as pd
import sqlite3
import time
from datetime import datetime, timedelta
import altair as alt
import os
import base64

DB_FILE = r"C:\Users\ROBBANI\Downloads\netraMVA\Camera Hanwha\Dashboard\Design_2\temperature.db"
VIDEO_FOLDER = r"C:\Users\ROBBANI\Downloads\netraMVA\Camera Hanwha\Dashboard\Design_2\Demo"
REFRESH_INTERVAL = 3  # detik
BATCH_SIZE = 10  # Jumlah data yang diload per batch

# ============================================================
# 🔹 Fungsi untuk mendapatkan semua ID yang ada
# ============================================================
def get_all_ids():
    try:
        conn = sqlite3.connect(DB_FILE)
        query = "SELECT id FROM temperature ORDER BY id ASC"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df['id'].tolist()
    except Exception as e:
        print(f"[ERROR] Gagal get all IDs: {e}")
        return []

# ============================================================
# 🔹 Fungsi untuk mendapatkan ID berikutnya yang valid
# ============================================================
def get_next_valid_id(current_id):
    try:
        all_ids = get_all_ids()
        if not all_ids:
            return None
            
        # Cari index dari current_id
        if current_id in all_ids:
            current_index = all_ids.index(current_id)
            if current_index + 1 < len(all_ids):
                return all_ids[current_index + 1]
        else:
            # Jika current_id tidak ada, cari ID terkecil yang lebih besar
            next_ids = [id for id in all_ids if id > current_id]
            if next_ids:
                return min(next_ids)
        
        return None
    except Exception as e:
        print(f"[ERROR] Gagal get next valid ID: {e}")
        return None

# ============================================================
# 🔹 Fungsi untuk load data berikutnya
# ============================================================
def load_next_batch():
    try:
        if st.session_state.camera1_data.empty:
            # Load batch pertama
            conn = sqlite3.connect(DB_FILE)
            query = """
                SELECT id, timestamp, roi_index, area_name, avg_temp, min_temp, max_temp
                FROM temperature
                ORDER BY id ASC
                LIMIT ?
            """
            df = pd.read_sql_query(query, conn, params=(BATCH_SIZE,))
            conn.close()
            return df
        
        # Cari ID berikutnya yang valid
        last_loaded_id = st.session_state.camera1_data.iloc[-1]['id']
        next_valid_id = get_next_valid_id(last_loaded_id)
        
        if next_valid_id is None:
            print(f"[LOAD] Tidak ada ID valid setelah {last_loaded_id}")
            return pd.DataFrame()
        
        print(f"[LOAD] Loading dari ID {next_valid_id}")
        
        # Load data mulai dari ID berikutnya
        conn = sqlite3.connect(DB_FILE)
        query = """
            SELECT id, timestamp, roi_index, area_name, avg_temp, min_temp, max_temp
            FROM temperature
            WHERE id >= ?
            ORDER BY id ASC
            LIMIT ?
        """
        df = pd.read_sql_query(query, conn, params=(next_valid_id, BATCH_SIZE))
        conn.close()
        
        print(f"[LOAD] Ditemukan: {len(df)} records")
        if not df.empty:
            print(f"[LOAD] ID range: {df.iloc[0]['id']} - {df.iloc[-1]['id']}")
        
        return df
        
    except Exception as e:
        print(f"[ERROR] Gagal load data: {e}")
        return pd.DataFrame()

# ============================================================
# 🔹 Fungsi untuk mendapatkan statistik ID
# ============================================================
def get_id_statistics():
    try:
        conn = sqlite3.connect(DB_FILE)
        
        # Min, Max, Count
        query_stats = """
            SELECT 
                MIN(id) as min_id,
                MAX(id) as max_id, 
                COUNT(*) as total_count,
                COUNT(DISTINCT id) as distinct_ids
            FROM temperature
        """
        stats = pd.read_sql_query(query_stats, conn).iloc[0]
        
        # Cek gap
        query_gap = """
            WITH gaps AS (
                SELECT id, LAG(id) OVER (ORDER BY id) as prev_id
                FROM temperature
            )
            SELECT COUNT(*) as gap_count 
            FROM gaps 
            WHERE prev_id IS NOT NULL AND id != prev_id + 1
        """
        gap_result = pd.read_sql_query(query_gap, conn)
        
        conn.close()
        
        return {
            'min_id': stats['min_id'],
            'max_id': stats['max_id'],
            'total_count': stats['total_count'],
            'distinct_ids': stats['distinct_ids'],
            'gap_count': gap_result.iloc[0]['gap_count'] if not gap_result.empty else 0
        }
    except Exception as e:
        print(f"[ERROR] Gagal get statistics: {e}")
        return None

# ============================================================
# 🔹 Fungsi untuk grafik - menggunakan data dari session_state
# ============================================================
def get_graph_data():
    """Menggunakan data dari session_state untuk grafik"""
    if st.session_state.camera1_data.empty:
        return pd.DataFrame()
    
    # Convert timestamp to datetime jika belum
    df = st.session_state.camera1_data.copy()
    if 'timestamp' in df.columns and df['timestamp'].dtype == 'object':
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    return df

# ============================================================
# 🔹 Fungsi untuk mendapatkan ROI aktif yang VALID
# ============================================================
def get_valid_rois_with_data(df, time_window_minutes=1):
    """Mendapatkan ROI yang memiliki data valid dalam waktu tertentu"""
    if df.empty:
        return []
    
    # Definisikan kolom suhu yang akan dicek
    temp_columns = ['avg_temp', 'min_temp', 'max_temp']
    
    # Urutkan ROI berdasarkan index secara ascending
    cutoff_time = datetime.now() - timedelta(minutes=time_window_minutes)
    recent_data = df[df['timestamp'] >= cutoff_time]
    
    valid_rois = []
    
    # Cek setiap ROI yang ada
    all_rois = sorted(df['roi_index'].unique().tolist())
    
    for roi_index in all_rois:
        roi_data = df[df['roi_index'] == roi_index].copy()
        
        # Filter data untuk ROI ini dalam time window
        roi_recent = roi_data[roi_data['timestamp'] >= cutoff_time]
        
        # Cek apakah ada data valid (minimal satu data point dengan suhu)
        has_valid_data = False
        
        # Cek data recent terlebih dahulu
        if not roi_recent.empty:
            for col in temp_columns:
                if col in roi_recent.columns and not roi_recent[col].isna().all():
                    has_valid_data = True
                    break
        
        # Jika tidak ada data recent, cek data keseluruhan
        if not has_valid_data and not roi_data.empty:
            for col in temp_columns:
                if col in roi_data.columns and not roi_data[col].isna().all():
                    has_valid_data = True
                    break
        
        if has_valid_data:
            valid_rois.append(roi_index)
    
    return valid_rois

# ============================================================
# 🔹 Mapping ROI index ke huruf
# ============================================================
def get_roi_letter(roi_index):
    """Mengkonversi ROI index ke huruf (A, B, C, dst.)"""
    roi_letters = {
        1: "A", 2: "B", 3: "C", 4: "D", 5: "E",
        6: "F", 7: "G", 8: "H", 9: "I", 10: "J"
    }
    return roi_letters.get(roi_index, f"ROI {roi_index}")

# ============================================================
# 🔹 Inisialisasi session_state UNTUK CAMERA 1
# ============================================================
if "camera1_data" not in st.session_state:
    st.session_state.camera1_data = pd.DataFrame()

if "camera1_last_update" not in st.session_state:
    st.session_state.camera1_last_update = datetime.now()

if "camera1_auto_refresh" not in st.session_state:
    st.session_state.camera1_auto_refresh = True

if "camera1_all_ids" not in st.session_state:
    st.session_state.camera1_all_ids = get_all_ids()

# 🔹 STATE BARU: Durasi grafik yang tersinkronisasi UNTUK CAMERA 1
if "camera1_graph_duration" not in st.session_state:
    st.session_state.camera1_graph_duration = 5  # menit default

# Load data awal jika kosong
if st.session_state.camera1_data.empty:
    initial_data = load_next_batch()
    if not initial_data.empty:
        st.session_state.camera1_data = initial_data

# ============================================================
# 🔹 Fungsi untuk auto update data UNTUK CAMERA 1
# ============================================================
def auto_update_data():
    if st.session_state.camera1_auto_refresh:
        current_time = datetime.now()
        time_diff = (current_time - st.session_state.camera1_last_update).total_seconds()
        
        if time_diff >= REFRESH_INTERVAL:
            # Refresh list ID
            st.session_state.camera1_all_ids = get_all_ids()
            
            if not st.session_state.camera1_data.empty:
                last_loaded_id = st.session_state.camera1_data.iloc[-1]['id']
                next_valid_id = get_next_valid_id(last_loaded_id)
                
                if next_valid_id is not None:
                    # Ada data berikutnya, load batch
                    new_data = load_next_batch()
                    if not new_data.empty:
                        st.session_state.camera1_data = pd.concat([st.session_state.camera1_data, new_data], ignore_index=True)
                        st.session_state.camera1_last_update = current_time
                        print(f"[CAMERA1 AUTO] Tambah {len(new_data)} data baru. ID terakhir: {st.session_state.camera1_data.iloc[-1]['id']}")
                        return True
                    else:
                        print(f"[CAMERA1 AUTO] Tidak ada data baru yang ditemukan")
                else:
                    print(f"[CAMERA1 AUTO] Sudah mencapai akhir data")
            
            st.session_state.camera1_last_update = current_time
    
    return False

# ============================================================
# 🔹 TAMPILAN UTAMA CAMERA 1
# ============================================================
st.title("Temperature Monitoring")

# ============================================================
# 🔹 LAYOUT SEJAJAR: Video dan Grafik
# ============================================================
col_video, col_graph = st.columns([1, 1])

with col_video:
    st.subheader("🎥 Streaming Video Thermal")
    
    video_path = os.path.join(VIDEO_FOLDER, "Demo.mp4")
    
    if video_path and os.path.exists(video_path):
        with open(video_path, "rb") as f:
            video_bytes = f.read()
        video_base64 = base64.b64encode(video_bytes).decode("utf-8")

        video_html = f"""
            <div style="display:flex; justify-content:center; margin-bottom: 1rem;">
                <video autoplay muted loop playsinline
                    style="width:100%; max-width:900px; aspect-ratio: 4 / 3; border-radius:10px; box-shadow:0 0 8px rgba(0,0,0,0.25); object-fit: cover;">
                    <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">
                    Browser Anda tidak mendukung video tag.
                </video>
            </div>
        """

        st.markdown(video_html, unsafe_allow_html=True)
        
        # Info ukuran video
        st.caption("📏 Ukuran video: 768 × 576 pixels")
        
    else:
        st.warning(f"Video demo tidak ditemukan di: {video_path}")

with col_graph:
    st.subheader("📈 Grafik Suhu per ROI")
    
    # Durasi grafik
    duration_choice = st.selectbox(
        "Durasi Tampilan Grafik:",
        options=[1, 3, 5, 10, 30, 60],
        index=[1, 3, 5, 10, 30, 60].index(st.session_state.camera1_graph_duration) if st.session_state.camera1_graph_duration in [1, 3, 5, 10, 30, 60] else 2,
        format_func=lambda x: f"{x} menit",
        key="camera1_graph_duration_selector"
    )

    # Update state durasi grafik
    st.session_state.camera1_graph_duration = duration_choice

    # Load data untuk grafik dari session_state
    df_graph = get_graph_data()

    if df_graph.empty:
        st.info("Menunggu data suhu...")
    else:
        # Pastikan timestamp dalam format datetime
        if 'timestamp' in df_graph.columns and df_graph['timestamp'].dtype == 'object':
            df_graph['timestamp'] = pd.to_datetime(df_graph['timestamp'])
        
        latest_time = df_graph["timestamp"].max() if not df_graph.empty else "N/A"
        st.caption(f"Data terakhir: {latest_time} | Total: {len(df_graph)} data")

        # 🔹 Hanya ambil ROI yang memiliki data valid
        if duration_choice == "Semua":
            time_window = 60 * 24  # 24 jam untuk "Semua"
        else:
            time_window = duration_choice
            
        valid_rois = get_valid_rois_with_data(df_graph, time_window_minutes=time_window)
        
        if not valid_rois:
            st.info("Menunggu data ROI...")
        else:
            # 🔹 Buat tab labels dengan huruf untuk ROI yang valid
            tab_labels = []
            roi_info = []  # Untuk menyimpan info ROI
            
            for roi_index in valid_rois:
                try:
                    # Cari area_name untuk ROI ini
                    roi_data = df_graph[df_graph["roi_index"] == roi_index]
                    if not roi_data.empty:
                        area_name = roi_data["area_name"].dropna().iloc[-1] if not roi_data["area_name"].isnull().all() else "Unknown"
                        roi_letter = get_roi_letter(roi_index)
                        
                        tab_labels.append(f"ROI {roi_letter}")
                        roi_info.append({
                            'index': roi_index,
                            'letter': roi_letter,
                            'area_name': area_name
                        })
                except (IndexError, KeyError):
                    continue

            # Buat tabs hanya untuk ROI yang valid
            if tab_labels:
                tabs = st.tabs(tab_labels)

                for tab, info in zip(tabs, roi_info):
                    with tab:
                        roi_index = info['index']
                        roi_letter = info['letter']
                        area_name = info['area_name']
                        
                        # Filter data untuk ROI ini
                        roi_df = df_graph[df_graph["roi_index"] == roi_index].copy()
                        roi_df = roi_df.dropna(subset=["avg_temp", "min_temp", "max_temp"], how="all")

                        if roi_df.empty:
                            continue

                        # 🔹 Fokus ke durasi pilihan
                        if duration_choice == "Semua":
                            roi_recent = roi_df
                        else:
                            cutoff_time = datetime.now() - timedelta(minutes=duration_choice)
                            roi_recent = roi_df[roi_df["timestamp"] >= cutoff_time]
                        
                        # Jika tidak ada data recent, gunakan data terakhir (max 20 data points)
                        if roi_recent.empty:
                            roi_recent = roi_df.tail(min(20, len(roi_df)))

                        # 🔹 MONITOR SUHU DI ATAS GRAFIK
                        if not roi_recent.empty:
                            latest = roi_recent.iloc[-1]
                            
                            # 🔹 Grafik suhu - gunakan roi_recent untuk data terbaru
                            chart_df = roi_recent.melt(
                                id_vars=["timestamp"],
                                value_vars=["avg_temp", "min_temp", "max_temp"],
                                var_name="Tipe",
                                value_name="Suhu"
                            ).dropna(subset=["Suhu"])

                            if not chart_df.empty:
                                # Atur range y-axis
                                y_min = max(20, chart_df["Suhu"].min() - 2)
                                y_max = min(60, chart_df["Suhu"].max() + 2)

                                chart = (
                                    alt.Chart(chart_df)
                                    .mark_line(point=True, size=1.5)
                                    .encode(
                                        x=alt.X(
                                            "timestamp:T",
                                            title="Waktu",
                                            axis=alt.Axis(format="%H:%M:%S", labelAngle=-45)
                                        ),
                                        y=alt.Y("Suhu:Q", scale=alt.Scale(domain=[y_min, y_max]), title="Suhu (°C)"),
                                        color=alt.Color(
                                            "Tipe:N",
                                            title="Jenis Suhu",
                                            scale=alt.Scale(
                                                domain=["avg_temp", "min_temp", "max_temp"],
                                                range=["#1f77b4", "#ff7f0e", "#d62728"]
                                            ),
                                            legend=alt.Legend(title="Keterangan:")
                                        ),
                                        tooltip=["timestamp:T", "Tipe:N", "Suhu:Q"]
                                    )
                                    .properties(
                                        width="container", 
                                        height=250,
                                        title=f"ROI {roi_letter} - {area_name}"
                                    )
                                    .interactive()
                                )

                                st.altair_chart(chart, use_container_width=True)
                                
                                # Tampilkan metrics di bawah grafik
                                cols = st.columns(3)
                                cols[0].metric(
                                    "Rata-rata", 
                                    f"{latest['avg_temp']:.1f}°C" if pd.notna(latest['avg_temp']) else "N/A"
                                )
                                cols[1].metric(
                                    "Minimum", 
                                    f"{latest['min_temp']:.1f}°C" if pd.notna(latest['min_temp']) else "N/A"
                                )
                                cols[2].metric(
                                    "Maksimum", 
                                    f"{latest['max_temp']:.1f}°C" if pd.notna(latest['max_temp']) else "N/A"
                                )

# ============================================================
# 🔹 Auto update dan refresh
# ============================================================
# Jalankan auto update di main thread
data_updated = auto_update_data()

# Jika data terupdate, trigger rerun
if data_updated:
    st.rerun()

# Auto refresh UI
try:
    from streamlit_autorefresh import st_autorefresh
    st_autorefresh(interval=REFRESH_INTERVAL * 1000, key="camera1_data_refresh")
except ImportError:
    if st.session_state.camera1_auto_refresh:
        time.sleep(REFRESH_INTERVAL)