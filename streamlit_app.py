import streamlit as st
import json
from datetime import datetime, date, timedelta
from typing import Dict, List, Any
import pandas as pd
import plotly.graph_objects as go
from zoneinfo import ZoneInfo
from streamlit_gsheets import GSheetsConnection # <-- Impor baru

# ==============================================================================
# KELAS LOGIKA BISNIS (TERHUBUNG KE GOOGLE SHEETS)
# ==============================================================================
class SugarTracker:
    def __init__(self):
        self.kemenkes_limit = 50
        self.aha_limits = {'pria_dewasa': 36, 'wanita_dewasa': 25, 'anak': 25}
        self._initialize_database()
        self.daily_intake: List[Dict] = []
        self.user_profile: Dict = {}
        
        # --- KONEKSI BARU KE GOOGLE SHEETS ---
        self.conn = st.connection("gsheets", type=GSheetsConnection)
        self.history = self._load_history()

    def _load_history(self) -> Dict:
        """Memuat riwayat dari Google Sheets."""
        try:
            df = self.conn.read(worksheet="history", usecols=[0, 1], ttl=5)
            df = df.dropna(how="all") # Hapus baris kosong
            history_data = {row['date']: json.loads(row['data']) for index, row in df.iterrows()}
            return history_data
        except Exception as e:
            st.error(f"Gagal memuat riwayat dari Google Sheets: {e}")
            return {}

    def _save_history(self):
        """Menyimpan seluruh riwayat ke Google Sheets."""
        try:
            # Ubah dictionary history menjadi DataFrame
            df_to_save = pd.DataFrame(self.history.items(), columns=['date', 'data'])
            # Ubah kolom data dari dictionary menjadi string JSON
            df_to_save['data'] = df_to_save['data'].apply(json.dumps)
            # Hapus semua data lama dan tulis ulang dengan data terbaru
            self.conn.clear(worksheet="history")
            self.conn.update(worksheet="history", data=df_to_save)
        except Exception as e:
            st.error(f"Gagal menyimpan riwayat ke Google Sheets: {e}")

    # ... Sisa kelas (archive_and_reset_day, database makanan, dll.) tetap sama persis ...
    def archive_and_reset_day(self):
        total_gula = self.calculate_daily_sugar()
        if total_gula > 0 and self.user_profile:
            today_str = date.today().strftime('%Y-%m-%d')
            limits = self.get_recommended_limit()
            aha_limit_value = limits.get('aha') if isinstance(limits.get('aha'), (int, float)) else 0
            self.history[today_str] = {'total_gula': round(total_gula, 2), 'limit_kemenkes': limits.get('kemenkes'), 'limit_aha': aha_limit_value}
            self._save_history()
        self.reset_daily_intake()
    def _initialize_database(self):
        self.food_database = {
            'teh_manis': {'gula_per_100': 10.0, 'satuan_umum': 'gelas', 'berat_satuan_umum': 200}, 'kopi_manis': {'gula_per_100': 8.0, 'satuan_umum': 'cangkir', 'berat_satuan_umum': 150},
            'es_teh_manis': {'gula_per_100': 12.0, 'satuan_umum': 'gelas', 'berat_satuan_umum': 250}, 'es_coklat': {'gula_per_100': 15.0, 'satuan_umum': 'gelas', 'berat_satuan_umum': 300},
            'sirup': {'gula_per_100': 65.0, 'satuan_umum': 'sendok makan', 'berat_satuan_umum': 15}, 'soda_cola': {'gula_per_100': 10.6, 'satuan_umum': 'kaleng', 'berat_satuan_umum': 330},
            'sprite': {'gula_per_100': 9.5, 'satuan_umum': 'kaleng', 'berat_satuan_umum': 330}, 'coca_cola_zero': {'gula_per_100': 0.0, 'satuan_umum': 'kaleng', 'berat_satuan_umum': 330},
            'jus_jeruk_kemasan': {'gula_per_100': 9.0, 'satuan_umum': 'kotak', 'berat_satuan_umum': 200}, 'minuman_energi': {'gula_per_100': 11.0, 'satuan_umum': 'kaleng', 'berat_satuan_umum': 250},
            'teh_kotak': {'gula_per_100': 8.5, 'satuan_umum': 'kotak', 'berat_satuan_umum': 200}, 'kopi_instan_sachet': {'gula_per_100': 50.0, 'satuan_umum': 'sachet', 'berat_satuan_umum': 20},
            'minuman_isotonik': {'gula_per_100': 6.0, 'satuan_umum': 'botol', 'berat_satuan_umum': 500}, 'susu_uht_full_cream': {'gula_per_100': 4.5, 'satuan_umum': 'kotak', 'berat_satuan_umum': 250},
            'susu_coklat': {'gula_per_100': 9.0, 'satuan_umum': 'kotak', 'berat_satuan_umum': 200}, 'yogurt_drink': {'gula_per_100': 11.0, 'satuan_umum': 'botol', 'berat_satuan_umum': 200},
            'susu_kedelai_kemasan': {'gula_per_100': 7.0, 'satuan_umum': 'kotak', 'berat_satuan_umum': 200}, 'air_kelapa_kemasan': {'gula_per_100': 6.0, 'satuan_umum': 'kotak', 'berat_satuan_umum': 250},
            'boba_milk_tea': {'gula_per_100': 18.0, 'satuan_umum': 'cup', 'berat_satuan_umum': 400}, 'es_kopi_susu_gula_aren': {'gula_per_100': 15.0, 'satuan_umum': 'cup', 'berat_satuan_umum': 250},
            'thai_tea': {'gula_per_100': 16.0, 'satuan_umum': 'cup', 'berat_satuan_umum': 300}, 'cheese_tea': {'gula_per_100': 14.0, 'satuan_umum': 'cup', 'berat_satuan_umum': 350},
            'matcha_latte': {'gula_per_100': 17.0, 'satuan_umum': 'cup', 'berat_satuan_umum': 350}, 'dalgano_coffee': {'gula_per_100': 18.0, 'satuan_umum': 'cup', 'berat_satuan_umum': 300},
            'coklat_batang': {'gula_per_100': 47.0, 'satuan_umum': 'batang', 'berat_satuan_umum': 50}, 'brownies_coklat': {'gula_per_100': 40.0, 'satuan_umum': 'potong', 'berat_satuan_umum': 60},
            'permen': {'gula_per_100': 85.0, 'satuan_umum': 'buah', 'berat_satuan_umum': 5}, 'kue_donat': {'gula_per_100': 25.0, 'satuan_umum': 'buah', 'berat_satuan_umum': 50},
            'es_krim': {'gula_per_100': 21.0, 'satuan_umum': 'scoop', 'berat_satuan_umum': 60}, 'biskuit_manis': {'gula_per_100': 25.0, 'satuan_umum': 'keping', 'berat_satuan_umum': 10},
            'cake_coklat': {'gula_per_100': 35.0, 'satuan_umum': 'potong', 'berat_satuan_umum': 60}, 'cookies': {'gula_per_100': 30.0, 'satuan_umum': 'keping', 'berat_satuan_umum': 15},
            'pudding': {'gula_per_100': 18.0, 'satuan_umum': 'cup', 'berat_satuan_umum': 120}, 'jelly': {'gula_per_100': 17.0, 'satuan_umum': 'cup', 'berat_satuan_umum': 100},
            'marshmallow': {'gula_per_100': 81.0, 'satuan_umum': 'buah', 'berat_satuan_umum': 7}, 'muffin': {'gula_per_100': 25.0, 'satuan_umum': 'buah', 'berat_satuan_umum': 90},
            'croissant_coklat': {'gula_per_100': 20.0, 'satuan_umum': 'buah', 'berat_satuan_umum': 70}, 'keripik_kentang_rasa': {'gula_per_100': 4.0, 'satuan_umum': 'bungkus kecil', 'berat_satuan_umum': 25},
            'wafer_coklat': {'gula_per_100': 35.0, 'satuan_umum': 'batang', 'berat_satuan_umum': 20}, 'biskuit_krim': {'gula_per_100': 28.0, 'satuan_umum': 'keping', 'berat_satuan_umum': 15},
            'apel': {'gula_per_100': 10.4, 'satuan_umum': 'buah', 'berat_satuan_umum': 180}, 'pisang': {'gula_per_100': 12.2, 'satuan_umum': 'buah', 'berat_satuan_umum': 120},
            'jeruk': {'gula_per_100': 9.4, 'satuan_umum': 'buah', 'berat_satuan_umum': 130}, 'mangga': {'gula_per_100': 13.7, 'satuan_umum': 'buah', 'berat_satuan_umum': 200},
            'anggur': {'gula_per_100': 16.3, 'satuan_umum': 'mangkuk', 'berat_satuan_umum': 150}, 'strawberry': {'gula_per_100': 4.9, 'satuan_umum': 'mangkuk', 'berat_satuan_umum': 150},
            'semangka': {'gula_per_100': 6.2, 'satuan_umum': 'potong', 'berat_satuan_umum': 280}, 'pepaya': {'gula_per_100': 5.9, 'satuan_umum': 'potong', 'berat_satuan_umum': 150},
            'nanas': {'gula_per_100': 9.9, 'satuan_umum': 'potong', 'berat_satuan_umum': 100}, 'melon': {'gula_per_100': 8.1, 'satuan_umum': 'potong', 'berat_satuan_umum': 150},
            'kurma': {'gula_per_100': 63.0, 'satuan_umum': 'buah', 'berat_satuan_umum': 7}, 'roti_tawar': {'gula_per_100': 5.0, 'satuan_umum': 'lembar', 'berat_satuan_umum': 25},
            'roti_manis': {'gula_per_100': 12.0, 'satuan_umum': 'buah', 'berat_satuan_umum': 60}, 'sereal_manis': {'gula_per_100': 30.0, 'satuan_umum': 'mangkuk', 'berat_satuan_umum': 40},
            'granola': {'gula_per_100': 20.0, 'satuan_umum': 'mangkuk', 'berat_satuan_umum': 50}, 'yogurt_buah': {'gula_per_100': 12.0, 'satuan_umum': 'cup', 'berat_satuan_umum': 125},
            'selai_strawberry': {'gula_per_100': 48.0, 'satuan_umum': 'sendok makan', 'berat_satuan_umum': 20}, 'selai_kacang': {'gula_per_100': 9.0, 'satuan_umum': 'sendok makan', 'berat_satuan_umum': 16},
            'madu': {'gula_per_100': 82.0, 'satuan_umum': 'sendok makan', 'berat_satuan_umum': 21}, 'gula_pasir': {'gula_per_100': 100.0, 'satuan_umum': 'sendok teh', 'berat_satuan_umum': 4},
            'gula_merah': {'gula_per_100': 85.0, 'satuan_umum': 'sendok makan', 'berat_satuan_umum': 15}, 'susu_kental_manis': {'gula_per_100': 54.0, 'satuan_umum': 'sendok makan', 'berat_satuan_umum': 20},
            'klepon': {'gula_per_100': 30.0, 'satuan_umum': 'buah', 'berat_satuan_umum': 20}, 'onde_onde': {'gula_per_100': 25.0, 'satuan_umum': 'buah', 'berat_satuan_umum': 40},
            'es_cendol': {'gula_per_100': 20.0, 'satuan_umum': 'gelas', 'berat_satuan_umum': 300}, 'es_doger': {'gula_per_100': 22.0, 'satuan_umum': 'mangkuk', 'berat_satuan_umum': 250},
            'kolak': {'gula_per_100': 18.0, 'satuan_umum': 'mangkuk', 'berat_satuan_umum': 250}, 'bubur_sumsum': {'gula_per_100': 14.0, 'satuan_umum': 'mangkuk', 'berat_satuan_umum': 200},
            'martabak_manis': {'gula_per_100': 22.0, 'satuan_umum': 'potong', 'berat_satuan_umum': 75}, 'kue_lapis': {'gula_per_100': 28.0, 'satuan_umum': 'potong', 'berat_satuan_umum': 40},
            'dodol': {'gula_per_100': 60.0, 'satuan_umum': 'potong', 'berat_satuan_umum': 20}, 'wingko': {'gula_per_100': 30.0, 'satuan_umum': 'buah', 'berat_satuan_umum': 50},
            'serabi': {'gula_per_100': 18.0, 'satuan_umum': 'buah', 'berat_satuan_umum': 60}, 'getuk': {'gula_per_100': 30.0, 'satuan_umum': 'potong', 'berat_satuan_umum': 50},
            'kue_putu': {'gula_per_100': 25.0, 'satuan_umum': 'buah', 'berat_satuan_umum': 25}, 'nasi_putih': {'gula_per_100': 0.1, 'satuan_umum': 'porsi', 'berat_satuan_umum': 200},
            'nasi_goreng': {'gula_per_100': 4.0, 'satuan_umum': 'porsi', 'berat_satuan_umum': 350}, 'mie_goreng_instan': {'gula_per_100': 8.0, 'satuan_umum': 'porsi', 'berat_satuan_umum': 120},
            'bubur_ayam': {'gula_per_100': 2.0, 'satuan_umum': 'porsi', 'berat_satuan_umum': 350}, 'lontong_sayur': {'gula_per_100': 5.0, 'satuan_umum': 'porsi', 'berat_satuan_umum': 450},
            'nasi_uduk': {'gula_per_100': 1.5, 'satuan_umum': 'porsi', 'berat_satuan_umum': 300}, 'ayam_goreng': {'gula_per_100': 1.0, 'satuan_umum': 'potong', 'berat_satuan_umum': 150},
            'rendang_daging': {'gula_per_100': 3.0, 'satuan_umum': 'potong', 'berat_satuan_umum': 50}, 'sate_ayam': {'gula_per_100': 10.0, 'satuan_umum': 'porsi', 'berat_satuan_umum': 150},
            'bakso': {'gula_per_100': 3.0, 'satuan_umum': 'porsi', 'berat_satuan_umum': 400}, 'soto_ayam': {'gula_per_100': 2.0, 'satuan_umum': 'porsi', 'berat_satuan_umum': 400},
            'gado_gado': {'gula_per_100': 12.0, 'satuan_umum': 'porsi', 'berat_satuan_umum': 400}, 'ikan_bakar': {'gula_per_100': 7.0, 'satuan_umum': 'porsi', 'berat_satuan_umum': 200},
            'ayam_bakar': {'gula_per_100': 9.0, 'satuan_umum': 'potong', 'berat_satuan_umum': 150}, 'burger': {'gula_per_100': 5.0, 'satuan_umum': 'buah', 'berat_satuan_umum': 250},
            'kentang_goreng': {'gula_per_100': 0.5, 'satuan_umum': 'porsi', 'berat_satuan_umum': 110}, 'pizza': {'gula_per_100': 3.6, 'satuan_umum': 'slice', 'berat_satuan_umum': 100},
            'fried_chicken': {'gula_per_100': 0.2, 'satuan_umum': 'potong', 'berat_satuan_umum': 120}, 'kecap_manis': {'gula_per_100': 60.0, 'satuan_umum': 'sendok makan', 'berat_satuan_umum': 15},
            'saus_tomat_botolan': {'gula_per_100': 22.0, 'satuan_umum': 'sendok makan', 'berat_satuan_umum': 15}, 'saus_sambal_botolan': {'gula_per_100': 15.0, 'satuan_umum': 'sendok makan', 'berat_satuan_umum': 15},
            'mayonnaise': {'gula_per_100': 4.0, 'satuan_umum': 'sendok makan', 'berat_satuan_umum': 15},
        }
    def set_user_profile(self, nama: str, umur: int, jenis_kelamin: str, berat_badan: float):
        self.user_profile = {'nama': nama, 'umur': umur, 'jenis_kelamin': jenis_kelamin.lower(), 'berat_badan': berat_badan, 'kategori': self._determine_category(umur, jenis_kelamin)}
    def _determine_category(self, umur: int, jenis_kelamin: str) -> str:
        if umur < 18: return 'anak'
        return 'pria_dewasa' if jenis_kelamin.lower() == 'pria' else 'wanita_dewasa'
    def get_recommended_limit(self) -> Dict[str, Any]:
        if not self.user_profile: return {'kemenkes': self.kemenkes_limit, 'aha': 'Profil belum diatur'}
        kategori = self.user_profile['kategori']
        return {'kemenkes': self.kemenkes_limit, 'aha': self.aha_limits.get(kategori)}
    def add_food_item(self, nama_makanan: str, jumlah: float, satuan: str):
        normalized_food_name = nama_makanan.lower().strip().replace(" ", "_")
        if normalized_food_name not in self.food_database: return False, f"❌ Makanan '{nama_makanan}' tidak ditemukan."
        food_info = self.food_database[normalized_food_name]
        jumlah_gram = 0
        if satuan in ['gram', 'ml']: jumlah_gram = jumlah
        elif satuan == food_info.get('satuan_umum'): jumlah_gram = jumlah * food_info.get('berat_satuan_umum', 0)
        else:
            factors = {'sendok teh': 5, 'sendok makan': 15, 'cup': 240, 'scoop': 60, 'keping': 10, 'buah': 120, 'potong': 50, 'lembar': 25, 'porsi': 200, 'gelas': 250, 'cangkir': 150, 'kaleng': 330, 'kotak': 200, 'botol': 500, 'sachet': 20, 'mangkuk': 250, 'slice': 100}
            if satuan in factors: jumlah_gram = jumlah * factors[satuan]
            else: return False, f"❌ Satuan '{satuan}' tidak umum. Coba 'gram' atau 'ml'."
        if jumlah_gram <= 0: return False, f"❌ Tidak dapat menghitung berat."
        total_gula = (food_info['gula_per_100'] * jumlah_gram) / 100
        item = {'nama': nama_makanan.title(), 'jumlah': jumlah, 'satuan': satuan, 'gula_gram': round(total_gula, 2), 'waktu': datetime.now().strftime('%H:%M:%S')}
        self.daily_intake.append(item)
        return True, f"✅ Berhasil ditambahkan: **{item['nama']}** ({total_gula:.2f}g gula)."
    def calculate_daily_sugar(self) -> float:
        return sum(item['gula_gram'] for item in self.daily_intake)
    def reset_daily_intake(self): self.daily_intake = []

# Sisa kode UI (CSS, Inisialisasi, Halaman-halaman) tidak perlu diubah.
# Tempelkan kode kelas SugarTracker di atas untuk menggantikan yang lama.
# --- UI CODE ---
if 'tracker' not in st.session_state:
    st.session_state.tracker = SugarTracker()
st.set_page_config(page_title="GluPal", page_icon="🍬", layout="wide")
st.markdown("""<style> ... </style>""", unsafe_allow_html=True) # CSS Anda di sini
# ... dan seterusnya untuk semua logika UI Anda ...
# (Sisa kode UI sama persis seperti jawaban sebelumnya yang menggunakan 2 progress bar)
