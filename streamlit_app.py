import streamlit as st
import json
from datetime import datetime, date, timedelta
from typing import Dict, List, Any
import pandas as pd
import plotly.graph_objects as go

# ==============================================================================
# KELAS LOGIKA BISNIS (DENGAN DATABASE LENGKAP)
# ==============================================================================

class SugarTracker:
    """
    Sebuah kelas untuk melacak asupan gula harian berdasarkan rekomendasi
    dari Kemenkes RI dan American Heart Association (AHA).
    Kini dengan fitur penyimpanan riwayat.
    """
    # --- Perbaikan Bug: _init_ harus menggunakan dua garis bawah ---
    def __init__(self):
        """Inisialisasi tracker dengan nilai default, database, dan riwayat."""
        self.kemenkes_limit = 50
        self.aha_limits = {
            'pria_dewasa': 36,
            'wanita_dewasa': 25,
            'anak': 25
        }
        self._initialize_database()
        self.daily_intake: List[Dict] = []
        self.user_profile: Dict = {}
        self.history_file = "gula_check_history.json"
        self.history = self._load_history()

    def _load_history(self) -> Dict:
        """Memuat riwayat konsumsi dari file JSON."""
        try:
            with open(self.history_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _save_history(self):
        """Menyimpan data riwayat ke file JSON."""
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=4)

    def archive_and_reset_day(self):
        """Mengarsipkan total hari ini ke riwayat dan mereset asupan."""
        total_gula = self.calculate_daily_sugar()
        if total_gula > 0 and self.user_profile:
            today_str = date.today().strftime('%Y-%m-%d')
            limits = self.get_recommended_limit()
            aha_limit_value = limits.get('aha') if isinstance(limits.get('aha'), (int, float)) else 0
            self.history[today_str] = {
                'total_gula': round(total_gula, 2),
                'limit_kemenkes': limits.get('kemenkes'),
                'limit_aha': aha_limit_value
            }
            self._save_history()
        self.reset_daily_intake()

    # --- DATABASE DIPERBARUI DAN DIPERLUAS ---
    def _initialize_database(self):
        """
        Menginisialisasi database makanan dengan daftar yang lebih lengkap dan beragam.
        """
        self.food_database = {
            # Minuman
            'teh_manis': {'gula_per_100': 10.0, 'satuan_umum': 'gelas', 'berat_satuan_umum': 200},
            'kopi_manis': {'gula_per_100': 8.0, 'satuan_umum': 'cangkir', 'berat_satuan_umum': 150},
            'es_teh_manis': {'gula_per_100': 12.0, 'satuan_umum': 'gelas', 'berat_satuan_umum': 250},
            'es_coklat': {'gula_per_100': 15.0, 'satuan_umum': 'gelas', 'berat_satuan_umum': 300},
            'sirup': {'gula_per_100': 65.0, 'satuan_umum': 'sendok makan', 'berat_satuan_umum': 15},

            # Minuman Kemasan
            'soda_cola': {'gula_per_100': 10.6, 'satuan_umum': 'kaleng', 'berat_satuan_umum': 330},
            'sprite': {'gula_per_100': 9.5, 'satuan_umum': 'kaleng', 'berat_satuan_umum': 330},
            'coca_cola_zero': {'gula_per_100': 0.0, 'satuan_umum': 'kaleng', 'berat_satuan_umum': 330},
            'jus_jeruk_kemasan': {'gula_per_100': 9.0, 'satuan_umum': 'kotak', 'berat_satuan_umum': 200},
            'minuman_energi': {'gula_per_100': 11.0, 'satuan_umum': 'kaleng', 'berat_satuan_umum': 250},
            'teh_kotak': {'gula_per_100': 8.5, 'satuan_umum': 'kotak', 'berat_satuan_umum': 200},
            'kopi_instan_sachet': {'gula_per_100': 50.0, 'satuan_umum': 'sachet', 'berat_satuan_umum': 20},
            'minuman_isotonik': {'gula_per_100': 6.0, 'satuan_umum': 'botol', 'berat_satuan_umum': 500},
            'susu_uht_full_cream': {'gula_per_100': 4.5, 'satuan_umum': 'kotak', 'berat_satuan_umum': 250},
            'susu_coklat': {'gula_per_100': 9.0, 'satuan_umum': 'kotak', 'berat_satuan_umum': 200},
            'yogurt_drink': {'gula_per_100': 11.0, 'satuan_umum': 'botol', 'berat_satuan_umum': 200},
            'susu_kedelai_kemasan': {'gula_per_100': 7.0, 'satuan_umum': 'kotak', 'berat_satuan_umum': 200},
            'air_kelapa_kemasan': {'gula_per_100': 6.0, 'satuan_umum': 'kotak', 'berat_satuan_umum': 250},

            # Minuman Kekinian
            'boba_milk_tea': {'gula_per_100': 18.0, 'satuan_umum': 'cup', 'berat_satuan_umum': 400},
            'es_kopi_susu_gula_aren': {'gula_per_100': 15.0, 'satuan_umum': 'cup', 'berat_satuan_umum': 250},
            'thai_tea': {'gula_per_100': 16.0, 'satuan_umum': 'cup', 'berat_satuan_umum': 300},
            'cheese_tea': {'gula_per_100': 14.0, 'satuan_umum': 'cup', 'berat_satuan_umum': 350},
            'matcha_latte': {'gula_per_100': 17.0, 'satuan_umum': 'cup', 'berat_satuan_umum': 350},
            'dalgano_coffee': {'gula_per_100': 18.0, 'satuan_umum': 'cup', 'berat_satuan_umum': 300},

            # Makanan Manis & Kue
            'coklat_batang': {'gula_per_100': 47.0, 'satuan_umum': 'batang', 'berat_satuan_umum': 50},
            'brownies_coklat': {'gula_per_100': 40.0, 'satuan_umum': 'potong', 'berat_satuan_umum': 60},
            'permen': {'gula_per_100': 85.0, 'satuan_umum': 'buah', 'berat_satuan_umum': 5},
            'kue_donat': {'gula_per_100': 25.0, 'satuan_umum': 'buah', 'berat_satuan_umum': 50},
            'es_krim': {'gula_per_100': 21.0, 'satuan_umum': 'scoop', 'berat_satuan_umum': 60},
            'biskuit_manis': {'gula_per_100': 25.0, 'satuan_umum': 'keping', 'berat_satuan_umum': 10},
            'cake_coklat': {'gula_per_100': 35.0, 'satuan_umum': 'potong', 'berat_satuan_umum': 60},
            'cookies': {'gula_per_100': 30.0, 'satuan_umum': 'keping', 'berat_satuan_umum': 15},
            'pudding': {'gula_per_100': 18.0, 'satuan_umum': 'cup', 'berat_satuan_umum': 120},
            'jelly': {'gula_per_100': 17.0, 'satuan_umum': 'cup', 'berat_satuan_umum': 100},
            'marshmallow': {'gula_per_100': 81.0, 'satuan_umum': 'buah', 'berat_satuan_umum': 7},
            'muffin': {'gula_per_100': 25.0, 'satuan_umum': 'buah', 'berat_satuan_umum': 90},
            'croissant_coklat': {'gula_per_100': 20.0, 'satuan_umum': 'buah', 'berat_satuan_umum': 70},

            # Cemilan Kemasan
            'keripik_kentang_rasa': {'gula_per_100': 4.0, 'satuan_umum': 'bungkus kecil', 'berat_satuan_umum': 25},
            'wafer_coklat': {'gula_per_100': 35.0, 'satuan_umum': 'batang', 'berat_satuan_umum': 20},
            'biskuit_krim': {'gula_per_100': 28.0, 'satuan_umum': 'keping', 'berat_satuan_umum': 15},
            
            # Buah-buahan
            'apel': {'gula_per_100': 10.4, 'satuan_umum': 'buah', 'berat_satuan_umum': 180},
            'pisang': {'gula_per_100': 12.2, 'satuan_umum': 'buah', 'berat_satuan_umum': 120},
            'jeruk': {'gula_per_100': 9.4, 'satuan_umum': 'buah', 'berat_satuan_umum': 130},
            'mangga': {'gula_per_100': 13.7, 'satuan_umum': 'buah', 'berat_satuan_umum': 200},
            'anggur': {'gula_per_100': 16.3, 'satuan_umum': 'mangkuk', 'berat_satuan_umum': 150},
            'strawberry': {'gula_per_100': 4.9, 'satuan_umum': 'mangkuk', 'berat_satuan_umum': 150},
            'semangka': {'gula_per_100': 6.2, 'satuan_umum': 'potong', 'berat_satuan_umum': 280},
            'pepaya': {'gula_per_100': 5.9, 'satuan_umum': 'potong', 'berat_satuan_umum': 150},
            'nanas': {'gula_per_100': 9.9, 'satuan_umum': 'potong', 'berat_satuan_umum': 100},
            'melon': {'gula_per_100': 8.1, 'satuan_umum': 'potong', 'berat_satuan_umum': 150},
            'kurma': {'gula_per_100': 63.0, 'satuan_umum': 'buah', 'berat_satuan_umum': 7},
            
            # Makanan Olahan & Sarapan
            'roti_tawar': {'gula_per_100': 5.0, 'satuan_umum': 'lembar', 'berat_satuan_umum': 25},
            'roti_manis': {'gula_per_100': 12.0, 'satuan_umum': 'buah', 'berat_satuan_umum': 60},
            'sereal_manis': {'gula_per_100': 30.0, 'satuan_umum': 'mangkuk', 'berat_satuan_umum': 40},
            'granola': {'gula_per_100': 20.0, 'satuan_umum': 'mangkuk', 'berat_satuan_umum': 50},
            'yogurt_buah': {'gula_per_100': 12.0, 'satuan_umum': 'cup', 'berat_satuan_umum': 125},
            'selai_strawberry': {'gula_per_100': 48.0, 'satuan_umum': 'sendok makan', 'berat_satuan_umum': 20},
            'selai_kacang': {'gula_per_100': 9.0, 'satuan_umum': 'sendok makan', 'berat_satuan_umum': 16},
            'madu': {'gula_per_100': 82.0, 'satuan_umum': 'sendok makan', 'berat_satuan_umum': 21},
            'gula_pasir': {'gula_per_100': 100.0, 'satuan_umum': 'sendok teh', 'berat_satuan_umum': 4},
            'gula_merah': {'gula_per_100': 85.0, 'satuan_umum': 'sendok makan', 'berat_satuan_umum': 15},
            'susu_kental_manis': {'gula_per_100': 54.0, 'satuan_umum': 'sendok makan', 'berat_satuan_umum': 20},

            # Makanan Tradisional
            'klepon': {'gula_per_100': 30.0, 'satuan_umum': 'buah', 'berat_satuan_umum': 20},
            'onde_onde': {'gula_per_100': 25.0, 'satuan_umum': 'buah', 'berat_satuan_umum': 40},
            'es_cendol': {'gula_per_100': 20.0, 'satuan_umum': 'gelas', 'berat_satuan_umum': 300},
            'es_doger': {'gula_per_100': 22.0, 'satuan_umum': 'mangkuk', 'berat_satuan_umum': 250},
            'kolak': {'gula_per_100': 18.0, 'satuan_umum': 'mangkuk', 'berat_satuan_umum': 250},
            'bubur_sumsum': {'gula_per_100': 14.0, 'satuan_umum': 'mangkuk', 'berat_satuan_umum': 200},
            'martabak_manis': {'gula_per_100': 22.0, 'satuan_umum': 'potong', 'berat_satuan_umum': 75},
            'kue_lapis': {'gula_per_100': 28.0, 'satuan_umum': 'potong', 'berat_satuan_umum': 40},
            'dodol': {'gula_per_100': 60.0, 'satuan_umum': 'potong', 'berat_satuan_umum': 20},
            'wingko': {'gula_per_100': 30.0, 'satuan_umum': 'buah', 'berat_satuan_umum': 50},
            'serabi': {'gula_per_100': 18.0, 'satuan_umum': 'buah', 'berat_satuan_umum': 60},
            'getuk': {'gula_per_100': 30.0, 'satuan_umum': 'potong', 'berat_satuan_umum': 50},
            'kue_putu': {'gula_per_100': 25.0, 'satuan_umum': 'buah', 'berat_satuan_umum': 25},

            # Makanan Berat & Lauk
            'nasi_putih': {'gula_per_100': 0.1, 'satuan_umum': 'porsi', 'berat_satuan_umum': 200},
            'nasi_goreng': {'gula_per_100': 4.0, 'satuan_umum': 'porsi', 'berat_satuan_umum': 350},
            'mie_goreng_instan': {'gula_per_100': 8.0, 'satuan_umum': 'porsi', 'berat_satuan_umum': 120},
            'bubur_ayam': {'gula_per_100': 2.0, 'satuan_umum': 'porsi', 'berat_satuan_umum': 350},
            'lontong_sayur': {'gula_per_100': 5.0, 'satuan_umum': 'porsi', 'berat_satuan_umum': 450},
            'nasi_uduk': {'gula_per_100': 1.5, 'satuan_umum': 'porsi', 'berat_satuan_umum': 300},
            'ayam_goreng': {'gula_per_100': 1.0, 'satuan_umum': 'potong', 'berat_satuan_umum': 150},
            'rendang_daging': {'gula_per_100': 3.0, 'satuan_umum': 'potong', 'berat_satuan_umum': 50},
            'sate_ayam': {'gula_per_100': 10.0, 'satuan_umum': 'porsi', 'berat_satuan_umum': 150},
            'bakso': {'gula_per_100': 3.0, 'satuan_umum': 'porsi', 'berat_satuan_umum': 400},
            'soto_ayam': {'gula_per_100': 2.0, 'satuan_umum': 'porsi', 'berat_satuan_umum': 400},
            'gado_gado': {'gula_per_100': 12.0, 'satuan_umum': 'porsi', 'berat_satuan_umum': 400},
            'ikan_bakar': {'gula_per_100': 7.0, 'satuan_umum': 'porsi', 'berat_satuan_umum': 200},
            'ayam_bakar': {'gula_per_100': 9.0, 'satuan_umum': 'potong', 'berat_satuan_umum': 150},
            
            # Makanan Cepat Saji
            'burger': {'gula_per_100': 5.0, 'satuan_umum': 'buah', 'berat_satuan_umum': 250},
            'kentang_goreng': {'gula_per_100': 0.5, 'satuan_umum': 'porsi', 'berat_satuan_umum': 110},
            'pizza': {'gula_per_100': 3.6, 'satuan_umum': 'slice', 'berat_satuan_umum': 100},
            'fried_chicken': {'gula_per_100': 0.2, 'satuan_umum': 'potong', 'berat_satuan_umum': 120},
            
            # Saus & Bumbu
            'kecap_manis': {'gula_per_100': 60.0, 'satuan_umum': 'sendok makan', 'berat_satuan_umum': 15},
            'saus_tomat_botolan': {'gula_per_100': 22.0, 'satuan_umum': 'sendok makan', 'berat_satuan_umum': 15},
            'saus_sambal_botolan': {'gula_per_100': 15.0, 'satuan_umum': 'sendok makan', 'berat_satuan_umum': 15},
            'mayonnaise': {'gula_per_100': 4.0, 'satuan_umum': 'sendok makan', 'berat_satuan_umum': 15},
        }

    def set_user_profile(self, nama: str, umur: int, jenis_kelamin: str, berat_badan: float):
        self.user_profile = {
            'nama': nama, 'umur': umur, 'jenis_kelamin': jenis_kelamin.lower(),
            'berat_badan': berat_badan, 'kategori': self._determine_category(umur, jenis_kelamin)
        }

    def _determine_category(self, umur: int, jenis_kelamin: str) -> str:
        if umur < 18: return 'anak'
        return 'pria_dewasa' if jenis_kelamin.lower() == 'pria' else 'wanita_dewasa'

    def get_recommended_limit(self) -> Dict[str, Any]:
        if not self.user_profile:
            return {'kemenkes': self.kemenkes_limit, 'aha': 'Profil belum diatur'}
        kategori = self.user_profile['kategori']
        aha_limit = self.aha_limits.get(kategori)
        return {'kemenkes': self.kemenkes_limit, 'aha': aha_limit}

    def add_food_item(self, nama_makanan: str, jumlah: float, satuan: str):
        normalized_food_name = nama_makanan.lower().strip().replace(" ", "_")
        if normalized_food_name not in self.food_database:
            return False, f"❌ Makanan '{nama_makanan}' tidak ditemukan."

        food_info = self.food_database[normalized_food_name]
        
        jumlah_gram = 0
        if satuan in ['gram', 'ml']:
            jumlah_gram = jumlah
        elif satuan == food_info.get('satuan_umum'):
             jumlah_gram = jumlah * food_info.get('berat_satuan_umum', 0)
        else:
            conversion_factors = {
                'sendok teh': 5, 'sendok makan': 15, 'cup': 240, 'scoop': 60,
                'keping': 10, 'buah': 120, 'potong': 50, 'lembar': 25, 'porsi': 200,
                'gelas': 250, 'cangkir': 150, 'kaleng': 330, 'kotak': 200, 
                'botol': 500, 'sachet': 20, 'mangkuk': 250, 'slice': 100
            }
            if satuan in conversion_factors:
                 jumlah_gram = jumlah * conversion_factors[satuan]
            else:
                return False, f"❌ Satuan '{satuan}' tidak umum. Coba gunakan 'gram' atau 'ml'."

        if jumlah_gram <= 0:
            return False, f"❌ Tidak dapat menghitung berat untuk satuan '{satuan}' pada makanan ini."

        kandungan_gula_per_100g = food_info['gula_per_100']
        total_gula = (kandungan_gula_per_100g * jumlah_gram) / 100
        
        item = {
            'nama': nama_makanan.replace('_', ' ').title(), 'jumlah': jumlah, 'satuan': satuan,
            'gula_gram': round(total_gula, 2), 'waktu': datetime.now().strftime('%H:%M:%S')
        }
        
        self.daily_intake.append(item)
        return True, f"✅ Berhasil ditambahkan: *{item['nama']}* ({total_gula:.2f}g gula)."

    def calculate_daily_sugar(self) -> float:
        return sum(item['gula_gram'] for item in self.daily_intake)

    def reset_daily_intake(self):
        self.daily_intake = []


# ==============================================================================
# --- BAGIAN UI/UX STREAMLIT DENGAN TEMA ADAPTIF ---
# ==============================================================================

# --- Inisialisasi Aplikasi ---
if 'tracker' not in st.session_state:
    st.session_state.tracker = SugarTracker()

st.set_page_config(page_title="GluPal", page_icon="🍬", layout="wide")

# --- CSS Kustom dengan Variabel untuk Tema Terang & Gelap ---
st.markdown("""
<style>
    /* Definisikan variabel warna untuk tema terang (default) */
    :root {
        --bg-color: #FFFFFF;
        --card-bg-color: #F0F8FF; /* AliceBlue */
        --text-color: #0d1117;
        --secondary-text-color: #555;
        --primary-accent-color: #1E90FF; /* DodgerBlue */
        --sugar-color: #FF69B4; /* HotPink */
        --safe-color: #28a745;
        --warning-color: #ffc107;
        --danger-color: #dc3545;
        --progress-track-color: #e9ecef;
        --shadow-color: rgba(0, 0, 0, 0.08);
    }

    /* Ganti variabel warna saat browser dalam mode gelap */
    @media (prefers-color-scheme: dark) {
        :root {
            --bg-color: #0d1117;
            --card-bg-color: #161b22;
            --text-color: #c9d1d9;
            --secondary-text-color: #8b949e;
            --primary-accent-color: #58a6ff;
            --sugar-color: #f781c6;
            --safe-color: #3fb950;
            --warning-color: #e3b341;
            --danger-color: #f85149;
            --progress-track-color: #2d333b;
            --shadow-color: rgba(0, 0, 0, 0.3);
        }
    }

    /* Menggunakan variabel di seluruh elemen */
    body {
        color: var(--text-color);
        background-color: var(--bg-color);
    }
    .metric-card {
        background-color: var(--card-bg-color);
        border-radius: 12px;
        padding: 25px;
        box-shadow: 0 4px 12px var(--shadow-color);
        border-left: 8px solid var(--primary-accent-color);
        margin-bottom: 15px;
        color: var(--text-color);
    }
    .metric-card h3 {
        font-size: 18px;
        color: var(--secondary-text-color);
        margin-bottom: 8px;
    }
    .metric-card p {
        font-size: 26px;
        font-weight: bold;
        color: var(--primary-accent-color);
    }
    .metric-card .sugar-value { color: var(--sugar-color); }
    .stButton>button {
        border-radius: 20px;
        border: 2px solid var(--primary-accent-color);
        background-color: var(--primary-accent-color);
        color: white;
        font-weight: bold;
        transition: all 0.2s;
    }
    .stButton>button:hover { opacity: 0.8; border-color: var(--sugar-color); }
    [data-testid="stSidebar"] { background-color: var(--card-bg-color); }
</style>
""", unsafe_allow_html=True)

# --- Fungsi Bantuan UI ---
def get_greeting():
    hour = datetime.now().hour
    if 5 <= hour < 12: return "Selamat Pagi ☀"
    elif 12 <= hour < 15: return "Selamat Siang 🌤"
    elif 15 <= hour < 19: return "Selamat Sore 🌇"
    else: return "Selamat Malam 🌙"

def colored_progress_bar(progress):
    if progress < 0.75: color_var = "var(--safe-color)"
    elif progress < 1.0: color_var = "var(--warning-color)"
    else: color_var = "var(--danger-color)"
    
    st.markdown(f"""
    <div style="background-color: var(--progress-track-color); border-radius: 10px; padding: 3px;">
        <div style="background-color: {color_var}; width: {min(progress * 100, 100)}%; height: 22px; border-radius: 7px; text-align: center; color: white; font-weight: bold; line-height: 22px;">
            {int(progress * 100)}%
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/128/18371/18371806.png", width=100)
    st.title("GluPal")
    
    user_name = st.session_state.tracker.user_profile.get('nama', "Pengguna")
    st.write(f"Halo, *{user_name}*!")

    menu_options = { 
        "🏠 Laporan Harian": "Laporan Harian", 
        "➕ Tambah Asupan": "Tambah Asupan", 
        "📚 Database Makanan": "Database Makanan",
        "📊 Riwayat & Grafik": "Riwayat & Grafik", 
        "👤 Profil Pengguna": "Profil Pengguna" 
    }
    selection = st.radio("Menu Navigasi:", options=menu_options.keys(), label_visibility="collapsed")
    menu = menu_options[selection]
    
    st.markdown("---")
    st.info("Pantau gula, jaga kesehatan. Aplikasi ini siap membantumu setiap hari!")

# ==============================================================================
# --- Tampilan Halaman (Pages) ---
# ==============================================================================

if menu == "Laporan Harian":
    st.title(get_greeting())
    st.subheader(f"Ini ringkasan gula harianmu, {user_name}.")
    
    if not st.session_state.tracker.user_profile:
        st.warning("⚠ Silakan atur profilmu terlebih dahulu di menu 'Profil Pengguna'.")
    else:
        total_gula = st.session_state.tracker.calculate_daily_sugar()
        limits = st.session_state.tracker.get_recommended_limit()

        col1, col2, col3 = st.columns(3)
        aha_val = limits['aha'] if isinstance(limits['aha'], (int, float)) else "N/A"
        sisa_gula = max(0, limits.get('aha', 0) - total_gula) if isinstance(limits.get('aha'), (int, float)) else "N/A"

        with col1:
            st.markdown(f'<div class="metric-card"><h3>🍬 Total Gula</h3><p class="sugar-value">{total_gula:.2f} g</p></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="metric-card"><h3>❤ Batas AHA</h3><p>{aha_val} g</p></div>', unsafe_allow_html=True)
        with col3:
             sisa_val = f"{sisa_gula:.2f}" if isinstance(sisa_gula, (int, float)) else sisa_gula
             st.markdown(f'<div class="metric-card"><h3>🏁 Sisa Jatah</h3><p>{sisa_val} g</p></div>', unsafe_allow_html=True)
        
        st.markdown("---")
        st.subheader("Progres Menuju Batas Harian (AHA)")
        if isinstance(limits['aha'], (int, float)) and limits['aha'] > 0:
            progress = total_gula / limits['aha']
            colored_progress_bar(progress)
            if progress >= 1.0: st.error("MELEBIHI BATAS! Harap lebih berhati-hati.")
        
        st.markdown("---")
        st.subheader("Rincian Asupan Hari Ini")
        if not st.session_state.tracker.daily_intake:
            st.info("Belum ada asupan yang dicatat. Tambahkan di menu 'Tambah Asupan'.")
        else:
            st.dataframe(pd.DataFrame(st.session_state.tracker.daily_intake), use_container_width=True, hide_index=True)

        if st.button("Simpan & Reset Hari Ini 💾"):
            st.session_state.tracker.archive_and_reset_day()
            st.success("Asupan hari ini berhasil diarsipkan dan direset!")
            st.balloons()
            st.rerun()

elif menu == "Tambah Asupan":
    st.header("📋 Tambah Asupan Makanan/Minuman")
    if not st.session_state.tracker.user_profile:
        st.warning("⚠ Silakan atur profilmu terlebih dahulu.")
    else:
        food_options = sorted([name.replace('_', ' ').title() for name in st.session_state.tracker.food_database.keys()])
        nama_makanan = st.selectbox("Langkah 1: Pilih atau cari Makanan/Minuman", options=food_options, index=None, placeholder="Ketik untuk mencari...")
        
        if nama_makanan:
            with st.form("add_food_form"):
                st.markdown(f"#### *{nama_makanan}*")
                col1, col2 = st.columns(2)
                jumlah = col1.number_input("Langkah 2: Masukkan Jumlah", min_value=0.1, value=1.0, step=0.1)
                
                food_key = nama_makanan.lower().replace(' ', '_')
                default_unit = st.session_state.tracker.food_database.get(food_key, {}).get('satuan_umum', 'gram')
                all_units = sorted(['gram', 'ml', 'porsi', 'buah', 'potong', 'lembar', 'sendok makan', 'sendok teh', 'cup', 'gelas', 'kaleng', 'kotak', 'botol', 'sachet', 'mangkuk', 'scoop', 'keping', 'slice'])
                try:
                    default_index = all_units.index(default_unit)
                except ValueError:
                    default_index = 0

                satuan = col2.selectbox("Langkah 3: Pilih Satuan", options=all_units, index=default_index)
                
                if st.form_submit_button("Tambahkan ke Catatan Harian ➕"):
                    success, message = st.session_state.tracker.add_food_item(nama_makanan, jumlah, satuan)
                    if success: st.success(message)
                    else: st.error(message)

elif menu == "Database Makanan":
    st.header("📚 Database Makanan")
    st.info("Cari makanan dan minuman untuk melihat estimasi kandungan gulanya.")
    db_instance = st.session_state.tracker
    
    categories = {
        'Minuman Kekinian & Tradisional': ['boba_milk_tea', 'es_kopi_susu_gula_aren', 'thai_tea', 'cheese_tea', 'matcha_latte', 'dalgano_coffee', 'es_cendol', 'es_doger', 'kolak', 'bubur_sumsum'],
        'Minuman Kemasan & Lainnya': ['soda_cola', 'sprite', 'teh_kotak', 'minuman_isotonik', 'susu_coklat', 'yogurt_drink', 'teh_manis', 'kopi_manis'],
        'Makanan Manis, Kue, & Cemilan': ['coklat_batang', 'brownies_coklat', 'permen', 'kue_donat', 'es_krim', 'biskuit_manis', 'cookies', 'muffin', 'wafer_coklat', 'martabak_manis', 'kue_lapis', 'serabi'],
        'Makanan Berat & Cepat Saji': ['nasi_goreng', 'mie_goreng_instan', 'bubur_ayam', 'sate_ayam', 'gado_gado', 'ayam_bakar', 'burger', 'pizza', 'kentang_goreng'],
        'Bahan & Buah': ['roti_tawar', 'selai_strawberry', 'madu', 'gula_pasir', 'kecap_manis', 'apel', 'pisang', 'mangga', 'kurma']
    }
    
    search_term = st.text_input("Cari makanan...", placeholder="Contoh: Boba Milk Tea")
    
    for category, items in categories.items():
        # Gabungkan item dari database yang ada dalam kategori ini
        db_keys = st.session_state.tracker.food_database.keys()
        relevant_items = [item for item in db_keys if item in items]
        
        # Filter berdasarkan pencarian
        filtered_items = [k for k in relevant_items if search_term.lower() in k.replace('_', ' ').lower()]
        
        if not search_term or filtered_items:
            with st.expander(f"{category}", expanded=bool(search_term)):
                for item_key in sorted(filtered_items if search_term else relevant_items):
                    food_info = db_instance.food_database[item_key]
                    item_name = item_key.replace('_', ' ').title()
                    gula = food_info['gula_per_100']
                    
                    col1, col2 = st.columns([3,1])
                    col1.markdown(f"{item_name}")
                    col2.metric(label="Gula / 100g", value=f"{gula} g")

elif menu == "Riwayat & Grafik":
    st.header("📊 Riwayat & Grafik Konsumsi Gula")
    if not st.session_state.tracker.user_profile:
        st.warning("⚠ Atur profil untuk melihat grafik dengan batas rekomendasi.")
    elif not st.session_state.tracker.history:
        st.info("Belum ada riwayat. Gunakan aplikasi dan 'Simpan & Reset' untuk membangun riwayatmu.")
    else:
        all_dates = sorted([datetime.strptime(d, '%Y-%m-%d').date() for d in st.session_state.tracker.history.keys()])
        
        with st.expander("🗓 Filter Riwayat", expanded=True):
            col1, col2 = st.columns(2)
            start_date = col1.date_input("Mulai", value=max(all_dates[0], date.today() - timedelta(days=6)), min_value=all_dates[0], max_value=all_dates[-1])
            end_date = col2.date_input("Selesai", value=all_dates[-1], min_value=all_dates[0], max_value=all_dates[-1])

        if start_date > end_date:
            st.error("Error: Tanggal Mulai tidak boleh setelah Tanggal Selesai.")
        else:
            filtered_dates = [d.strftime('%Y-%m-%d') for d in all_dates if start_date <= d <= end_date]
            if not filtered_dates:
                st.warning("Tidak ada data untuk rentang tanggal yang dipilih.")
            else:
                limits = st.session_state.tracker.get_recommended_limit()
                aha = limits.get('aha')

                fig = go.Figure()
                fig.add_trace(go.Scatter(x=filtered_dates, y=[st.session_state.tracker.history[d]['total_gula'] for d in filtered_dates], mode='lines+markers', name='Konsumsi Gula', line=dict(color='var(--sugar-color)', width=4), hovertemplate='<b>%{x}</b><br>Gula: %{y:.1f} g<extra></extra>'))
                if isinstance(aha, (int, float)):
                    fig.add_trace(go.Scatter(x=filtered_dates, y=[aha] * len(filtered_dates), mode='lines', name=f'Batas AHA ({aha}g)', line=dict(color='var(--warning-color)', dash='dash'), hoverinfo='skip'))
                
                fig.update_layout(
                    title_text=f"Grafik Konsumsi Gula", xaxis_title="Tanggal", yaxis_title="Jumlah Gula (g)",
                    plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color="var(--text-color)"), yaxis=dict(gridcolor='rgba(128,128,128,0.2)'),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1), hovermode="x unified"
                )
                st.plotly_chart(fig, use_container_width=True)

elif menu == "Profil Pengguna":
    st.header("👤 Profil Pengguna")
    st.write("Informasi ini digunakan untuk menentukan batas rekomendasi asupan gula harianmu.")
    profile = st.session_state.tracker.user_profile
    
    col1, col2 = st.columns([1, 2])
    with col1:
        avatar = "https://cdn-icons-png.flaticon.com/512/3135/3135715.png" if profile.get('jenis_kelamin', 'pria') == 'pria' else "https://cdn-icons-png.flaticon.com/512/3135/3135789.png"
        st.image(avatar, width=150)
    with col2:
        with st.form("profile_form"):
            nama = st.text_input("Nama Lengkap", value=profile.get('nama', ''))
            c1, c2 = st.columns(2)
            umur = c1.number_input("Umur", min_value=1, max_value=120, value=profile.get('umur', 25))
            berat = c2.number_input("Berat (kg)", min_value=1.0, value=profile.get('berat_badan', 60.0), format="%.1f")
            
            jenis_kelamin = st.selectbox("Jenis Kelamin", ["Pria", "Wanita"], index=1 if profile.get('jenis_kelamin') == 'wanita' else 0)
            
            if st.form_submit_button("Simpan Profil 💾"):
                st.session_state.tracker.set_user_profile(nama, umur, jenis_kelamin, berat)
                st.success(f"Profil untuk *{nama}* berhasil disimpan!")
                st.rerun()

    if profile:
        limits = st.session_state.tracker.get_recommended_limit()
        st.success(f"Batas konsumsi gulamu: *Kemenkes: {limits['kemenkes']}g, **AHA: {limits['aha']}g* per hari.")
