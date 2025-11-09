import requests
import time
import sqlite3
from datetime import datetime
from requests.auth import HTTPDigestAuth

# === KONFIGURASI ===
CAMERA_IP = "192.168.100.118"
ENDPOINT = f"http://{CAMERA_IP}/stw-cgi/eventsources.cgi?msubmenu=boxtemperaturedetection&action=check"

USERNAME = "admin"
PASSWORD = "P@ssw0rd"

ROI_RANGE = range(1, 11)   # 1..10
INTERVAL = 3               # detik
DB_FILE = "temperature.db"


# === Helper: Mapping index ke huruf A, B, C... ===
def index_to_letter(idx):
    """Map 1 -> 'A', 2 -> 'B', ..., 26 -> 'Z'. Jika >26, gunakan 'ROI{idx}'."""
    if 1 <= idx <= 26:
        return chr(ord("A") + idx - 1)
    else:
        return f"ROI{idx}"


# === 1) Inisialisasi database SQLite ===
def init_database():
    """Buat database dan tabel jika belum ada."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS temperature (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME,
            roi_index INTEGER,
            area_name TEXT,
            avg_temp REAL,
            min_temp REAL,
            max_temp REAL
        )
    """)
    conn.commit()
    conn.close()


# === 2) Ambil data suhu dari kamera ===
def get_temperature_data():
    """Ambil data suhu dari kamera Hanwha. area_name selalu terisi A,B,C... jika kamera tidak mengirim."""
    try:
        response = requests.get(
            ENDPOINT,
            auth=HTTPDigestAuth(USERNAME, PASSWORD),
            timeout=5
        )
        response.raise_for_status()
        data = response.json()

        rois = data["BoxTemperatureDetection"][0].get("ROIsTemperature", [])
        roi_dict = {roi.get("ROIIndex"): roi for roi in rois if "ROIIndex" in roi}

        result = []
        for idx in ROI_RANGE:
            roi_data = roi_dict.get(idx)
            # jika kamera mengirim area_name gunakan itu, jika kosong gunakan A,B,...
            if roi_data:
                # periksa nama yang dikirim; jika kosong/None, gunakan mapping
                sent_name = roi_data.get("AreaName")
                area_name = sent_name if sent_name not in (None, "", "NULL") else index_to_letter(idx)

                result.append({
                    "roi_index": idx,
                    "area_name": area_name,
                    "avg_temp": roi_data.get("AvgTemperature"),
                    "min_temp": roi_data.get("MinTemperature"),
                    "max_temp": roi_data.get("MaxTemperature")
                })
            else:
                # ROI tidak dikirim → beri nama A,B,... tapi suhu None
                result.append({
                    "roi_index": idx,
                    "area_name": index_to_letter(idx),
                    "avg_temp": None,
                    "min_temp": None,
                    "max_temp": None
                })

        return result

    except Exception as e:
        print(f"❌ Gagal mengambil data dari kamera: {e}")
        return None


# === 3) Simpan hasilnya ke database ===
def save_to_database(timestamp, temps):
    """Simpan hasil pembacaan suhu ke SQLite database."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # gunakan named parameters sesuai nama kolom di DB
        records = [
            {
                "timestamp": timestamp,
                "roi_index": t["roi_index"],
                "area_name": t["area_name"],
                "avg_temp": t["avg_temp"],
                "min_temp": t["min_temp"],
                "max_temp": t["max_temp"]
            }
            for t in temps
        ]

        cursor.executemany("""
            INSERT INTO temperature (timestamp, roi_index, area_name, avg_temp, min_temp, max_temp)
            VALUES (:timestamp, :roi_index, :area_name, :avg_temp, :min_temp, :max_temp)
        """, records)

        conn.commit()
        conn.close()
        print(f"✅ {timestamp} | {len(temps)} data disimpan ke database.")

    except Exception as e:
        print(f"⚠️ Gagal menyimpan data ke database: {e}")


# === 4) Main Loop ===
if __name__ == "__main__":
    print("🚀 Memulai pengambilan data suhu dari kamera Hanwha...")
    init_database()

    while True:
        temps = get_temperature_data()
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if temps:
            save_to_database(current_time, temps)
        else:
            print("⚠️ Tidak ada data diterima, mengisi dengan ROI kosong (nama tetap A,B,...)")
            empty_data = [
                {
                    "roi_index": idx,
                    "area_name": index_to_letter(idx),
                    "avg_temp": None,
                    "min_temp": None,
                    "max_temp": None
                }
                for idx in ROI_RANGE
            ]
            save_to_database(current_time, empty_data)

        time.sleep(INTERVAL)
