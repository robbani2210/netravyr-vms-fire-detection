import sqlite3

db_path = "temperature.db"  # pastikan path ini benar

# Koneksi ke database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Hapus semua data di tabel temperature
cursor.execute("DELETE FROM temperature;")
conn.commit()

# Tampilkan jumlah data setelah dihapus
cursor.execute("SELECT COUNT(*) FROM temperature;")
count = cursor.fetchone()[0]
print(f"✅ Semua data dihapus. Sisa data sekarang: {count}")

conn.close()
