import streamlit as st
import json
from datetime import datetime, date
from typing import Dict, List, Any
import pandas as pd

# ==============================================================================
# KELAS LOGIKA BISNIS (TIDAK ADA PERUBAHAN)
# ==============================================================================

class SugarTracker:
    """
    Sebuah kelas untuk melacak asupan gula harian berdasarkan rekomendasi
    dari Kemenkes RI dan American Heart Association (AHA).
    Kini dengan fitur penyimpanan riwayat.
    """
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
        
        # --- Fitur Riwayat Baru ---
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

    def _initialize_database(self):
        """
        Menginisialisasi database makanan dengan struktur yang lebih detail.
        (Tidak ada perubahan di fungsi ini)
        """
        self.food_database = {
            # Minuman
            'teh_manis': {'gula_per_100': 10.0, 'satuan_umum': 'gelas', 'berat_satuan_umum': 200, 'kategori': 'Minuman'},
            'kopi_manis': {'gula_per_100': 8.0, 'satuan_umum': 'cangkir', 'berat_satuan_umum': 150, 'kategori': 'Minuman'},
            'soda_cola': {'gula_per_100': 10.6, 'satuan_umum': 'kaleng', 'berat_satuan_umum': 250, 'kategori': 'Minuman'},
            'sprite': {'gula_per_100': 10.3, 'satuan_umum': 'kaleng', 'berat_satuan_umum': 250, 'kategori': 'Minuman'},
            'coca_cola_zero': {'gula_per_100': 0.0, 'satuan_umum': 'kaleng', 'berat_satuan_umum': 250, 'kategori': 'Minuman'},
            'jus_jeruk_kemasan': {'gula_per_100': 9.0, 'satuan_umum': 'kotak', 'berat_satuan_umum': 200, 'kategori': 'Minuman'},
            'es_teh_manis': {'gula_per_100': 12.0, 'satuan_umum': 'gelas', 'berat_satuan_umum': 250, 'kategori': 'Minuman'},
            'minuman_energi': {'gula_per_100': 11.0, 'satuan_umum': 'kaleng', 'berat_satuan_umum': 250, 'kategori': 'Minuman'},
            'sirup': {'gula_per_100': 65.0, 'satuan_umum': 'sendok makan', 'berat_satuan_umum': 15, 'kategori': 'Minuman'},
            'susu_coklat': {'gula_per_100': 9.0, 'satuan_umum': 'kotak', 'berat_satuan_umum': 200, 'kategori': 'Minuman'},
            'yogurt_drink': {'gula_per_100': 11.0, 'satuan_umum': 'botol', 'berat_satuan_umum': 200, 'kategori': 'Minuman'},
            'air_kelapa_kemasan': {'gula_per_100': 6.0, 'satuan_umum': 'kotak', 'berat_satuan_umum': 250, 'kategori': 'Minuman'},
            
            # Minuman Kemasan
            'teh_kotak': {'gula_per_100': 8.5, 'satuan_umum': 'kotak', 'berat_satuan_umum': 200, 'kategori': 'Minuman Kemasan'},
            'kopi_instan_sachet': {'gula_per_100': 50.0, 'satuan_umum': 'sachet', 'berat_satuan_umum': 20, 'kategori': 'Minuman Kemasan'},
            'minuman_isotonik': {'gula_per_100': 6.0, 'satuan_umum': 'botol', 'berat_satuan_umum': 500, 'kategori': 'Minuman Kemasan'},
            'susu_uht_full_cream': {'gula_per_100': 4.5, 'satuan_umum': 'kotak', 'berat_satuan_umum': 250, 'kategori': 'Minuman Kemasan'},

            # Minuman Kekinian
            'boba_milk_tea': {'gula_per_100': 18.0, 'satuan_umum': 'cup', 'berat_satuan_umum': 350, 'kategori': 'Minuman Kekinian'},
            'es_kopi_susu_gula_aren': {'gula_per_100': 15.0, 'satuan_umum': 'cup', 'berat_satuan_umum': 250, 'kategori': 'Minuman Kekinian'},
            'thai_tea': {'gula_per_100': 16.0, 'satuan_umum': 'cup', 'berat_satuan_umum': 300, 'kategori': 'Minuman Kekinian'},
            'cheese_tea': {'gula_per_100': 14.0, 'satuan_umum': 'cup', 'berat_satuan_umum': 350, 'kategori': 'Minuman Kekinian'},
            'matcha_latte': {'gula_per_100': 17.0, 'satuan_umum': 'cup', 'berat_satuan_umum': 350, 'kategori': 'Minuman Kekinian'},
            'greentea_latte': {'gula_per_100': 17.0, 'satuan_umum': 'cup', 'berat_satuan_umum': 350, 'kategori': 'Minuman Kekinian'},
            'red_velvet_latte': {'gula_per_100': 19.0, 'satuan_umum': 'cup', 'berat_satuan_umum': 350, 'kategori': 'Minuman Kekinian'},
            'es_coklat': {'gula_per_100': 15.0, 'satuan_umum': 'gelas', 'berat_satuan_umum': 300, 'kategori': 'Minuman Kekinian'},

            # Makanan Manis
            'coklat_batang': {'gula_per_100': 47.0, 'satuan_umum': 'batang', 'berat_satuan_umum': 50, 'kategori': 'Makanan Manis'},
            'brownies_coklat': {'gula_per_100': 40.0, 'satuan_umum': 'potong', 'berat_satuan_umum': 60, 'kategori': 'Makanan Manis'},
            'permen': {'gula_per_100': 85.0, 'satuan_umum': 'buah', 'berat_satuan_umum': 5, 'kategori': 'Makanan Manis'},
            'kue_donat': {'gula_per_100': 15.0, 'satuan_umum': 'buah', 'berat_satuan_umum': 50, 'kategori': 'Makanan Manis'},
            'es_krim': {'gula_per_100': 14.0, 'satuan_umum': 'scoop', 'berat_satuan_umum': 60, 'kategori': 'Makanan Manis'},
            'biskuit_manis': {'gula_per_100': 25.0, 'satuan_umum': 'keping', 'berat_satuan_umum': 10, 'kategori': 'Makanan Manis'},
            'cake_coklat': {'gula_per_100': 35.0, 'satuan_umum': 'potong', 'berat_satuan_umum': 60, 'kategori': 'Makanan Manis'},
            'cookies': {'gula_per_100': 20.0, 'satuan_umum': 'keping', 'berat_satuan_umum': 15, 'kategori': 'Makanan Manis'},
            'pudding': {'gula_per_100': 18.0, 'satuan_umum': 'cup', 'berat_satuan_umum': 120, 'kategori': 'Makanan Manis'},
            'jelly': {'gula_per_100': 17.0, 'satuan_umum': 'cup', 'berat_satuan_umum': 100, 'kategori': 'Makanan Manis'},
            'marshmallow': {'gula_per_100': 81.0, 'satuan_umum': 'buah', 'berat_satuan_umum': 7, 'kategori': 'Makanan Manis'},
            'kue_cubit': {'gula_per_100': 25.0, 'satuan_umum': 'buah', 'berat_satuan_umum': 20, 'kategori': 'Makanan Manis'},
            'lapis_legit': {'gula_per_100': 40.0, 'satuan_umum': 'potong', 'berat_satuan_umum': 30, 'kategori': 'Makanan Manis'},

            # Buah-buahan
            'apel': {'gula_per_100': 10.4, 'satuan_umum': 'buah', 'berat_satuan_umum': 180, 'kategori': 'Buah-buahan'},
            'pisang': {'gula_per_100': 12.2, 'satuan_umum': 'buah', 'berat_satuan_umum': 120, 'kategori': 'Buah-buahan'},
            'jeruk': {'gula_per_100': 9.4, 'satuan_umum': 'buah', 'berat_satuan_umum': 130, 'kategori': 'Buah-buahan'},
            'mangga': {'gula_per_100': 13.7, 'satuan_umum': 'buah', 'berat_satuan_umum': 200, 'kategori': 'Buah-buahan'},
            'anggur': {'gula_per_100': 16.3, 'satuan_umum': 'mangkuk', 'berat_satuan_umum': 150, 'kategori': 'Buah-buahan'},
            'strawberry': {'gula_per_100': 4.9, 'satuan_umum': 'mangkuk', 'berat_satuan_umum': 150, 'kategori': 'Buah-buahan'},
            'semangka': {'gula_per_100': 6.2, 'satuan_umum': 'potong', 'berat_satuan_umum': 280, 'kategori': 'Buah-buahan'},
            'pepaya': {'gula_per_100': 5.9, 'satuan_umum': 'potong', 'berat_satuan_umum': 150, 'kategori': 'Buah-buahan'},
            'nanas': {'gula_per_100': 9.9, 'satuan_umum': 'potong', 'berat_satuan_umum': 100, 'kategori': 'Buah-buahan'},
            'melon': {'gula_per_100': 8.1, 'satuan_umum': 'potong', 'berat_satuan_umum': 150, 'kategori': 'Buah-buahan'},
            'kurma': {'gula_per_100': 63.0, 'satuan_umum': 'buah', 'berat_satuan_umum': 7, 'kategori': 'Buah-buahan'},
            
            # Makanan Olahan
            'roti_manis': {'gula_per_100': 12.0, 'satuan_umum': 'buah', 'berat_satuan_umum': 60, 'kategori': 'Makanan Olahan'},
            'sereal_manis': {'gula_per_100': 30.0, 'satuan_umum': 'mangkuk', 'berat_satuan_umum': 40, 'kategori': 'Makanan Olahan'},
            'granola': {'gula_per_100': 6.0, 'satuan_umum': 'mangkuk', 'berat_satuan_umum': 50, 'kategori': 'Makanan Olahan'},
            'yogurt_buah': {'gula_per_100': 12.0, 'satuan_umum': 'cup', 'berat_satuan_umum': 125, 'kategori': 'Makanan Olahan'},
            'selai_strawberry': {'gula_per_100': 48.0, 'satuan_umum': 'sendok makan', 'berat_satuan_umum': 20, 'kategori': 'Makanan Olahan'},
            'madu': {'gula_per_100': 82.0, 'satuan_umum': 'sendok makan', 'berat_satuan_umum': 21, 'kategori': 'Makanan Olahan'},
            'gula_pasir': {'gula_per_100': 100.0, 'satuan_umum': 'sendok teh', 'berat_satuan_umum': 4, 'kategori': 'Makanan Olahan'},
            'gula_merah': {'gula_per_100': 85.0, 'satuan_umum': 'sendok makan', 'berat_satuan_umum': 15, 'kategori': 'Makanan Olahan'},
            'kondensed_milk': {'gula_per_100': 54.0, 'satuan_umum': 'sendok makan', 'berat_satuan_umum': 20, 'kategori': 'Makanan Olahan'},
            'roti_tawar': {'gula_per_100': 5.0, 'satuan_umum': 'lembar', 'berat_satuan_umum': 25, 'kategori': 'Makanan Olahan'},
            'selai_kacang': {'gula_per_100': 9.0, 'satuan_umum': 'sendok makan', 'berat_satuan_umum': 16, 'kategori': 'Makanan Olahan'},

            # Makanan Tradisional
            'klepon': {'gula_per_100': 20.0, 'satuan_umum': 'buah', 'berat_satuan_umum': 20, 'kategori': 'Makanan Tradisional'},
            'onde_onde': {'gula_per_100': 25.0, 'satuan_umum': 'buah', 'berat_satuan_umum': 40, 'kategori': 'Makanan Tradisional'},
            'es_cendol': {'gula_per_100': 15.0, 'satuan_umum': 'gelas', 'berat_satuan_umum': 300, 'kategori': 'Makanan Tradisional'},
            'es_doger': {'gula_per_100': 18.0, 'satuan_umum': 'mangkuk', 'berat_satuan_umum': 250, 'kategori': 'Makanan Tradisional'},
            'kolak': {'gula_per_100': 12.0, 'satuan_umum': 'mangkuk', 'berat_satuan_umum': 250, 'kategori': 'Makanan Tradisional'},
            'bubur_sumsum': {'gula_per_100': 14.0, 'satuan_umum': 'mangkuk', 'berat_satuan_umum': 200, 'kategori': 'Makanan Tradisional'},
            'martabak_manis': {'gula_per_100': 22.0, 'satuan_umum': 'potong', 'berat_satuan_umum': 75, 'kategori': 'Makanan Tradisional'},
            'kue_lapis': {'gula_per_100': 28.0, 'satuan_umum': 'potong', 'berat_satuan_umum': 40, 'kategori': 'Makanan Tradisional'},
            'dodol': {'gula_per_100': 60.0, 'satuan_umum': 'potong', 'berat_satuan_umum': 20, 'kategori': 'Makanan Tradisional'},
            'wingko': {'gula_per_100': 30.0, 'satuan_umum': 'buah', 'berat_satuan_umum': 50, 'kategori': 'Makanan Tradisional'},
            'serabi': {'gula_per_100': 18.0, 'satuan_umum': 'buah', 'berat_satuan_umum': 60, 'kategori': 'Makanan Tradisional'},
            'getuk': {'gula_per_100': 30.0, 'satuan_umum': 'potong', 'berat_satuan_umum': 50, 'kategori': 'Makanan Tradisional'},
            'cenil': {'gula_per_100': 22.0, 'satuan_umum': 'porsi', 'berat_satuan_umum': 100, 'kategori': 'Makanan Tradisional'},

            # Makanan Berat & Sarapan
            'nasi_goreng': {'gula_per_100': 4.0, 'satuan_umum': 'porsi', 'berat_satuan_umum': 350, 'kategori': 'Makanan Berat & Sarapan'},
            'mie_goreng_instan': {'gula_per_100': 8.0, 'satuan_umum': 'porsi', 'berat_satuan_umum': 120, 'kategori': 'Makanan Berat & Sarapan'},
            'bubur_ayam': {'gula_per_100': 2.0, 'satuan_umum': 'porsi', 'berat_satuan_umum': 350, 'kategori': 'Makanan Berat & Sarapan'},
            'lontong_sayur': {'gula_per_100': 5.0, 'satuan_umum': 'porsi', 'berat_satuan_umum': 450, 'kategori': 'Makanan Berat & Sarapan'},
            'nasi_uduk': {'gula_per_100': 1.5, 'satuan_umum': 'porsi', 'berat_satuan_umum': 300, 'kategori': 'Makanan Berat & Sarapan'},
            'ayam_goreng': {'gula_per_100': 1.0, 'satuan_umum': 'potong', 'berat_satuan_umum': 150, 'kategori': 'Makanan Berat & Sarapan'},
            'rendang_daging': {'gula_per_100': 3.0, 'satuan_umum': 'potong', 'berat_satuan_umum': 50, 'kategori': 'Makanan Berat & Sarapan'},
            'sate_ayam': {'gula_per_100': 10.0, 'satuan_umum': 'porsi', 'berat_satuan_umum': 150, 'kategori': 'Makanan Berat & Sarapan'},
            'bakso': {'gula_per_100': 3.0, 'satuan_umum': 'porsi', 'berat_satuan_umum': 400, 'kategori': 'Makanan Berat & Sarapan'},
            'soto_ayam': {'gula_per_100': 2.0, 'satuan_umum': 'porsi', 'berat_satuan_umum': 400, 'kategori': 'Makanan Berat & Sarapan'},
            'gado_gado': {'gula_per_100': 12.0, 'satuan_umum': 'porsi', 'berat_satuan_umum': 400, 'kategori': 'Makanan Berat & Sarapan'},
            'sop_ayam': {'gula_per_100': 1.5, 'satuan_umum': 'porsi', 'berat_satuan_umum': 400, 'kategori': 'Makanan Berat & Sarapan'},
            'ikan_goreng': {'gula_per_100': 0.5, 'satuan_umum': 'potong', 'berat_satuan_umum': 150, 'kategori': 'Makanan Berat & Sarapan'},
            'sushi': {'gula_per_100': 5.0, 'satuan_umum': 'potong', 'berat_satuan_umum': 30, 'kategori': 'Makanan Berat & Sarapan'},
            'nasi_putih': {'gula_per_100': 0.1, 'satuan_umum': 'porsi', 'berat_satuan_umum': 200, 'kategori': 'Makanan Berat & Sarapan'},
            'gulai_ayam': {'gula_per_100': 4.0, 'satuan_umum': 'porsi', 'berat_satuan_umum': 400, 'kategori': 'Makanan Berat & Sarapan'},
            
            # Saus & Bumbu
            'kecap_manis': {'gula_per_100': 60.0, 'satuan_umum': 'sendok makan', 'berat_satuan_umum': 15, 'kategori': 'Saus & Bumbu'},
            'saus_tomat_botolan': {'gula_per_100': 22.0, 'satuan_umum': 'sendok makan', 'berat_satuan_umum': 15, 'kategori': 'Saus & Bumbu'},
            'saus_sambal_botolan': {'gula_per_100': 15.0, 'satuan_umum': 'sendok makan', 'berat_satuan_umum': 15, 'kategori': 'Saus & Bumbu'}
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
            return False, f"Makanan '{nama_makanan}' tidak ditemukan."

        food_info = self.food_database[normalized_food_name]
        
        jumlah_gram = 0
        if satuan in ['gram', 'ml']:
            jumlah_gram = jumlah
        elif satuan in ['sendok teh', 'sendok makan']:
            conversion_factors = {'sendok teh': 5, 'sendok makan': 15} # Updated for consistency
            jumlah_gram = jumlah * conversion_factors.get(satuan, 0)
        elif satuan == food_info.get('satuan_umum'):
            jumlah_gram = jumlah * food_info.get('berat_satuan_umum', 0)
        else:
            return False, f"Satuan '{satuan}' tidak valid untuk {nama_makanan}."

        if jumlah_gram == 0:
            return False, f"Tidak dapat menghitung berat untuk satuan '{satuan}'."

        kandungan_gula_per_100g = food_info['gula_per_100']
        total_gula = (kandungan_gula_per_100g * jumlah_gram) / 100
        
        item = {
            'Waktu': datetime.now().strftime('%H:%M:%S'),
            'Nama': nama_makanan.replace('_', ' ').title(), 
            'Jumlah': jumlah, 
            'Satuan': satuan,
            'Gula (g)': round(total_gula, 2),
        }
        
        self.daily_intake.append(item)
        return True, f"Berhasil menambahkan: **{nama_makanan}** ({jumlah} {satuan}) mengandung **{total_gula:.2f}g** gula."

    def calculate_daily_sugar(self) -> float:
        return sum(item['Gula (g)'] for item in self.daily_intake)

    def reset_daily_intake(self):
        self.daily_intake = []

# ==============================================================================
# BAGIAN ANTARMUKA STREAMLIT (REFACTORED & IMPROVED UI)
# ==============================================================================

def get_greeting():
    """Mendapatkan sapaan berdasarkan waktu."""
    hour = datetime.now().hour
    if 5 <= hour < 12: return "Selamat Pagi ☀️"
    if 12 <= hour < 15: return "Selamat Siang 🌤️"
    if 15 <= hour < 19: return "Selamat Sore 🌥️"
    return "Selamat Malam 🌙"

def show_daily_report():
    """Menampilkan halaman Laporan Harian."""
    st.title(get_greeting())
    user_name = st.session_state.tracker.user_profile.get('nama', 'Pengguna')
    st.subheader(f"Ini laporan gula harian Anda, {user_name}.")
    
    if not st.session_state.tracker.user_profile:
        st.warning("ℹ️ Silakan atur profil Anda terlebih dahulu melalui menu 'Profil Pengguna' di sidebar.")
        return

    total_gula = st.session_state.tracker.calculate_daily_sugar()
    limits = st.session_state.tracker.get_recommended_limit()
    limit_kemenkes = limits['kemenkes']
    limit_aha = limits.get('aha', 0) if isinstance(limits.get('aha'), (int, float)) else 0

    st.divider()

    # --- Kartu Metrik Utama ---
    with st.container(border=True):
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Gula Hari Ini", f"{total_gula:.2f} g")
        col2.metric("Batas Kemenkes", f"{limit_kemenkes} g")
        if limit_aha > 0:
            col3.metric("Batas AHA", f"{limit_aha} g")

    st.divider()
    
    # --- Kartu Progres & Status ---
    st.subheader("📊 Progres Menuju Batas Harian")
    
    with st.container(border=True):
        # Progres untuk Kemenkes
        st.write(f"**Rekomendasi Kemenkes RI ({limit_kemenkes} g)**")
        progress_kemenkes = min(total_gula / limit_kemenkes, 1.0) if limit_kemenkes > 0 else 0
        st.progress(progress_kemenkes)
        sisa_kemenkes = limit_kemenkes - total_gula
        if sisa_kemenkes >= 0:
            st.success(f"✅ Masih ada **{sisa_kemenkes:.2f}g** tersisa dari batas Kemenkes.")
        else:
            st.error(f"🚨 Melebihi **{-sisa_kemenkes:.2f}g** dari batas Kemenkes!")
        
        st.write("") # Spacer

        # Progres untuk AHA
        if limit_aha > 0:
            st.write(f"**Rekomendasi AHA ({limit_aha} g)**")
            progress_aha = min(total_gula / limit_aha, 1.0)
            st.progress(progress_aha)
            sisa_aha = limit_aha - total_gula
            if sisa_aha >= 0:
                st.success(f"✅ Masih ada **{sisa_aha:.2f}g** tersisa dari batas AHA.")
            else:
                st.warning(f"⚠️ Melebihi **{-sisa_aha:.2f}g** dari batas AHA!")

    st.divider()
    
    # --- Rincian Asupan ---
    st.subheader("🍽️ Rincian Asupan Hari Ini")
    if not st.session_state.tracker.daily_intake:
        st.info("Belum ada asupan yang dicatat hari ini. Tambahkan di menu 'Tambah Asupan'.")
    else:
        df_intake = pd.DataFrame(st.session_state.tracker.daily_intake)
        # Reorder columns for better readability
        df_intake = df_intake[['Waktu', 'Nama', 'Jumlah', 'Satuan', 'Gula (g)']]
        st.dataframe(df_intake, use_container_width=True, hide_index=True)

    # --- Tombol Reset ---
    if st.button("Simpan & Reset Hari Ini", type="primary", use_container_width=True):
        st.session_state.tracker.archive_and_reset_day()
        st.success("Asupan hari ini berhasil diarsipkan dan direset!")
        st.balloons()
        st.rerun()

def show_add_intake():
    """Menampilkan halaman Tambah Asupan."""
    st.header("➕ Tambah Asupan")
    if not st.session_state.tracker.user_profile:
        st.warning("ℹ️ Silakan atur profil Anda terlebih dahulu melalui menu 'Profil Pengguna' di sidebar.")
        return

    with st.container(border=True):
        food_options = sorted([name.replace('_', ' ').title() for name in st.session_state.tracker.food_database.keys()])
        nama_makanan_display = st.selectbox("Langkah 1: Pilih Makanan/Minuman", options=food_options, key="food_selector")
        
        nama_makanan_key = nama_makanan_display.lower().replace(' ', '_')
        food_info = st.session_state.tracker.food_database[nama_makanan_key]
        
        # Determine available units
        satuan_options = ["gram", "ml"]
        if 'satuan_umum' in food_info and food_info['satuan_umum']:
            satuan_options.append(food_info['satuan_umum'])
        # Add common sugar units
        satuan_options.extend(['sendok teh', 'sendok makan'])
        satuan_options = sorted(list(set(satuan_options))) # Remove duplicates and sort
        
        with st.form("add_food_form"):
            st.markdown(f"Anda memilih: **{nama_makanan_display}**")
            col1, col2 = st.columns(2)
            jumlah = col1.number_input("Langkah 2: Masukkan Jumlah", min_value=0.1, value=1.0, step=0.1)
            satuan = col2.selectbox("Langkah 3: Pilih Satuan", options=satuan_options)
            
            submitted = st.form_submit_button("Tambah ke Catatan Harian", type="primary", use_container_width=True)
            if submitted:
                success, message = st.session_state.tracker.add_food_item(nama_makanan_display, jumlah, satuan)
                if success:
                    st.success(message)
                else:
                    st.error(message)

def show_history():
    """Menampilkan halaman Riwayat & Grafik."""
    st.header("📈 Riwayat & Grafik Konsumsi Gula")
    history_data = st.session_state.tracker.history

    if not history_data:
        st.info("Belum ada riwayat yang tersimpan. Gunakan aplikasi dan tekan 'Simpan & Reset Hari Ini' untuk mulai membangun riwayat Anda.")
        return

    # --- Data Preparation ---
    dates = sorted(history_data.keys())
    recent_dates = dates[-30:] # Limit to last 30 days for the chart
    
    chart_data = {
        "Tanggal": [datetime.strptime(d, '%Y-%m-%d').date() for d in recent_dates],
        "Total Gula (g)": [history_data[d]['total_gula'] for d in recent_dates],
        "Batas Kemenkes (g)": [history_data[d]['limit_kemenkes'] for d in recent_dates],
        "Batas AHA (g)": [history_data[d]['limit_aha'] for d in recent_dates]
    }
    
    df_chart = pd.DataFrame(chart_data)
    df_chart.set_index("Tanggal", inplace=True)
    
    # --- Chart ---
    with st.container(border=True):
        st.subheader("Grafik Konsumsi 30 Hari Terakhir")
        st.line_chart(df_chart, color=["#FF4B4B", "#1E90FF", "#FFA500"]) # Red, Blue, Orange

    st.divider()

    # --- Detailed History Table ---
    with st.container(border=True):
        st.subheader("Tabel Rincian Riwayat")
        # Use full history for the table, sorted descending
        full_history_df = df_chart.reset_index().sort_values(by="Tanggal", ascending=False)
        st.dataframe(full_history_df, use_container_width=True, hide_index=True)

def show_user_profile():
    """Menampilkan halaman Profil Pengguna."""
    st.header("👤 Profil Pengguna")
    st.write("Atur profil Anda untuk mendapatkan rekomendasi batas gula yang sesuai.")
    
    with st.form("profile_form"):
        with st.container(border=True):
            nama = st.text_input("Nama Lengkap", value=st.session_state.tracker.user_profile.get('nama', ''))
            
            col1, col2 = st.columns(2)
            umur = col1.number_input("Umur (tahun)", min_value=1, max_value=120, value=st.session_state.tracker.user_profile.get('umur', 25))
            berat_badan = col2.number_input("Berat Badan (kg)", min_value=1.0, max_value=300.0, value=st.session_state.tracker.user_profile.get('berat_badan', 60.0), format="%.1f")
            
            gender_options = ["Pria", "Wanita"]
            current_gender = st.session_state.tracker.user_profile.get('jenis_kelamin', 'pria')
            gender_index = 1 if current_gender == 'wanita' else 0
            jenis_kelamin = st.selectbox("Jenis Kelamin", gender_options, index=gender_index)
        
        submitted = st.form_submit_button("Simpan Profil", type="primary", use_container_width=True)
        if submitted:
            st.session_state.tracker.set_user_profile(nama, umur, jenis_kelamin, berat_badan)
            st.success(f"Profil untuk **{nama}** berhasil disimpan!")
            limits = st.session_state.tracker.get_recommended_limit()
            st.info(f"Batas konsumsi gula Anda: **Kemenkes: {limits['kemenkes']}g**, **AHA: {limits['aha']}g** per hari.")

def show_food_database():
    """Menampilkan halaman Database Makanan."""
    st.header("📚 Database Makanan")
    st.info("Cari makanan dan minuman untuk melihat estimasi kandungan gulanya.")

    # Convert database to DataFrame for easier searching and display
    db_list = []
    for key, value in st.session_state.tracker.food_database.items():
        db_list.append({
            "Nama Makanan": key.replace('_', ' ').title(),
            "Kategori": value.get('kategori', 'N/A'),
            "Gula (g/100g)": value['gula_per_100'],
            "Satuan Umum": f"1 {value.get('satuan_umum', '-')}",
            "Berat Satuan (g)": value.get('berat_satuan_umum', '-')
        })
    df_db = pd.DataFrame(db_list)

    # Search functionality
    search_term = st.text_input("Cari makanan...", placeholder="Contoh: Nasi Goreng, Teh, Donat")
    if search_term:
        df_db = df_db[df_db["Nama Makanan"].str.contains(search_term, case=False)]

    st.dataframe(
        df_db,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Gula (g/100g)": st.column_config.NumberColumn(format="%.1f g")
        }
    )

# ==============================================================================
# --- MAIN APP LOGIC ---
# ==============================================================================

# Initialize session state
if 'tracker' not in st.session_state:
    st.session_state.tracker = SugarTracker()

st.set_page_config(page_title="GulaCheck", page_icon="🍭", layout="wide")

# --- Sidebar ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2723/2723331.png", width=100)
    st.title("GulaCheck")
    
    user_name = st.session_state.tracker.user_profile.get('nama')
    if user_name:
        st.write(f"Halo, **{user_name}**!")
    
    # Menu selection
    menu_options = {
        "🏠 Laporan Harian": show_daily_report,
        "➕ Tambah Asupan": show_add_intake,
        "📈 Riwayat & Grafik": show_history,
        "👤 Profil Pengguna": show_user_profile,
        "📚 Database Makanan": show_food_database
    }
    selection = st.radio(
        "Pilih Menu:",
        options=menu_options.keys(),
        label_visibility="collapsed"
    )
    
    st.divider()
    st.info("Pantau asupan gula harian Anda dengan mudah. Jaga kesehatan, batasi gula!")
    st.markdown("<div style='text-align: center;'>Dibuat dengan ❤️</div>", unsafe_allow_html=True)

# --- Display selected page ---
# Call the function corresponding to the selected menu option
menu_options[selection]()
