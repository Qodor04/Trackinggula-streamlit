import streamlit as st
import json
from datetime import datetime
from typing import Dict, List, Any

# ==============================================================================
# KELAS LOGIKA BISNIS (TIDAK BERUBAH)
# ==============================================================================

class SugarTracker:
    """
    Sebuah kelas untuk melacak asupan gula harian berdasarkan rekomendasi
    dari Kemenkes RI dan American Heart Association (AHA).
    """
    def __init__(self):
        """Inisialisasi tracker dengan nilai default dan database makanan."""
        self.kemenkes_limit = 50
        self.aha_limits = {
            'pria_dewasa': 36,
            'wanita_dewasa': 25,
            'anak': 25
        }
        self._initialize_database()
        self.daily_intake: List[Dict] = []
        self.user_profile: Dict = {}

    def _initialize_database(self):
        """
        Menginisialisasi database makanan dengan struktur yang lebih detail.
        """
        self.food_database = {
            # Minuman
            'teh_manis': {'gula_per_100': 10.0, 'satuan_umum': 'gelas', 'berat_satuan_umum': 200},
            'kopi_manis': {'gula_per_100': 8.0, 'satuan_umum': 'cangkir', 'berat_satuan_umum': 150},
            'soda_cola': {'gula_per_100': 10.6, 'satuan_umum': 'kaleng', 'berat_satuan_umum': 250},
            'sprite': {'gula_per_100': 10.3, 'satuan_umum': 'kaleng', 'berat_satuan_umum': 250},
            'coca_cola_zero': {'gula_per_100': 0.0, 'satuan_umum': 'kaleng', 'berat_satuan_umum': 250},
            'jus_jeruk_kemasan': {'gula_per_100': 9.0, 'satuan_umum': 'kotak', 'berat_satuan_umum': 200},
            'es_teh_manis': {'gula_per_100': 12.0, 'satuan_umum': 'gelas', 'berat_satuan_umum': 250},
            'minuman_energi': {'gula_per_100': 11.0, 'satuan_umum': 'kaleng', 'berat_satuan_umum': 250},
            'sirup': {'gula_per_100': 65.0, 'satuan_umum': 'sendok makan', 'berat_satuan_umum': 15},
            'susu_coklat': {'gula_per_100': 9.0, 'satuan_umum': 'kotak', 'berat_satuan_umum': 200},
            'yogurt_drink': {'gula_per_100': 11.0, 'satuan_umum': 'botol', 'berat_satuan_umum': 200},
            'air_kelapa_kemasan': {'gula_per_100': 6.0, 'satuan_umum': 'kotak', 'berat_satuan_umum': 250},
            
            # Minuman Kemasan
            'teh_kotak': {'gula_per_100': 8.5, 'satuan_umum': 'kotak', 'berat_satuan_umum': 200},
            'kopi_instan_sachet': {'gula_per_100': 50.0, 'satuan_umum': 'sachet', 'berat_satuan_umum': 20},
            'minuman_isotonik': {'gula_per_100': 6.0, 'satuan_umum': 'botol', 'berat_satuan_umum': 500},
            'susu_uht_full_cream': {'gula_per_100': 4.5, 'satuan_umum': 'kotak', 'berat_satuan_umum': 250},

            # Minuman Kekinian
            'boba_milk_tea': {'gula_per_100': 18.0, 'satuan_umum': 'cup', 'berat_satuan_umum': 350},
            'es_kopi_susu_gula_aren': {'gula_per_100': 15.0, 'satuan_umum': 'cup', 'berat_satuan_umum': 250},
            'thai_tea': {'gula_per_100': 16.0, 'satuan_umum': 'cup', 'berat_satuan_umum': 300},
            'cheese_tea': {'gula_per_100': 14.0, 'satuan_umum': 'cup', 'berat_satuan_umum': 350},
            'matcha_latte': {'gula_per_100': 17.0, 'satuan_umum': 'cup', 'berat_satuan_umum': 350},
            'greentea_latte': {'gula_per_100': 17.0, 'satuan_umum': 'cup', 'berat_satuan_umum': 350},
            'red_velvet_latte': {'gula_per_100': 19.0, 'satuan_umum': 'cup', 'berat_satuan_umum': 350},
            'es_coklat': {'gula_per_100': 15.0, 'satuan_umum': 'gelas', 'berat_satuan_umum': 300},

            # Makanan Manis
            'coklat_batang': {'gula_per_100': 47.0, 'satuan_umum': 'batang', 'berat_satuan_umum': 50},
            'brownies_coklat': {'gula_per_100': 40.0, 'satuan_umum': 'potong', 'berat_satuan_umum': 60},
            'permen': {'gula_per_100': 85.0, 'satuan_umum': 'buah', 'berat_satuan_umum': 5},
            'kue_donat': {'gula_per_100': 15.0, 'satuan_umum': 'buah', 'berat_satuan_umum': 50},
            'es_krim': {'gula_per_100': 14.0, 'satuan_umum': 'scoop', 'berat_satuan_umum': 60},
            'biskuit_manis': {'gula_per_100': 25.0, 'satuan_umum': 'keping', 'berat_satuan_umum': 10},
            'cake_coklat': {'gula_per_100': 35.0, 'satuan_umum': 'potong', 'berat_satuan_umum': 60},
            'cookies': {'gula_per_100': 20.0, 'satuan_umum': 'keping', 'berat_satuan_umum': 15},
            'pudding': {'gula_per_100': 18.0, 'satuan_umum': 'cup', 'berat_satuan_umum': 120},
            'jelly': {'gula_per_100': 17.0, 'satuan_umum': 'cup', 'berat_satuan_umum': 100},
            'marshmallow': {'gula_per_100': 81.0, 'satuan_umum': 'buah', 'berat_satuan_umum': 7},
            'kue_cubit': {'gula_per_100': 25.0, 'satuan_umum': 'buah', 'berat_satuan_umum': 20},
            'lapis_legit': {'gula_per_100': 40.0, 'satuan_umum': 'potong', 'berat_satuan_umum': 30},

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
            
            # Makanan Olahan
            'roti_manis': {'gula_per_100': 12.0, 'satuan_umum': 'buah', 'berat_satuan_umum': 60},
            'sereal_manis': {'gula_per_100': 30.0, 'satuan_umum': 'mangkuk', 'berat_satuan_umum': 40},
            'granola': {'gula_per_100': 6.0, 'satuan_umum': 'mangkuk', 'berat_satuan_umum': 50},
            'yogurt_buah': {'gula_per_100': 12.0, 'satuan_umum': 'cup', 'berat_satuan_umum': 125},
            'selai_strawberry': {'gula_per_100': 48.0, 'satuan_umum': 'sendok makan', 'berat_satuan_umum': 20},
            'madu': {'gula_per_100': 82.0, 'satuan_umum': 'sendok makan', 'berat_satuan_umum': 21},
            'gula_pasir': {'gula_per_100': 100.0, 'satuan_umum': 'sendok teh', 'berat_satuan_umum': 4},
            'gula_merah': {'gula_per_100': 85.0, 'satuan_umum': 'sendok makan', 'berat_satuan_umum': 15},
            'kondensed_milk': {'gula_per_100': 54.0, 'satuan_umum': 'sendok makan', 'berat_satuan_umum': 20},
            'roti_tawar': {'gula_per_100': 5.0, 'satuan_umum': 'lembar', 'berat_satuan_umum': 25},
            'selai_kacang': {'gula_per_100': 9.0, 'satuan_umum': 'sendok makan', 'berat_satuan_umum': 16},

            # Makanan Tradisional
            'klepon': {'gula_per_100': 20.0, 'satuan_umum': 'buah', 'berat_satuan_umum': 20},
            'onde_onde': {'gula_per_100': 25.0, 'satuan_umum': 'buah', 'berat_satuan_umum': 40},
            'es_cendol': {'gula_per_100': 15.0, 'satuan_umum': 'gelas', 'berat_satuan_umum': 300},
            'es_doger': {'gula_per_100': 18.0, 'satuan_umum': 'mangkuk', 'berat_satuan_umum': 250},
            'kolak': {'gula_per_100': 12.0, 'satuan_umum': 'mangkuk', 'berat_satuan_umum': 250},
            'bubur_sumsum': {'gula_per_100': 14.0, 'satuan_umum': 'mangkuk', 'berat_satuan_umum': 200},
            'martabak_manis': {'gula_per_100': 22.0, 'satuan_umum': 'potong', 'berat_satuan_umum': 75},
            'kue_lapis': {'gula_per_100': 28.0, 'satuan_umum': 'potong', 'berat_satuan_umum': 40},
            'dodol': {'gula_per_100': 60.0, 'satuan_umum': 'potong', 'berat_satuan_umum': 20},
            'wingko': {'gula_per_100': 30.0, 'satuan_umum': 'buah', 'berat_satuan_umum': 50},
            'serabi': {'gula_per_100': 18.0, 'satuan_umum': 'buah', 'berat_satuan_umum': 60},
            'getuk': {'gula_per_100': 30.0, 'satuan_umum': 'potong', 'berat_satuan_umum': 50},
            'cenil': {'gula_per_100': 22.0, 'satuan_umum': 'porsi', 'berat_satuan_umum': 100},

            # Makanan Berat & Sarapan
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
            'sop_ayam': {'gula_per_100': 1.5, 'satuan_umum': 'porsi', 'berat_satuan_umum': 400},
            'ikan_goreng': {'gula_per_100': 0.5, 'satuan_umum': 'potong', 'berat_satuan_umum': 150},
            'sushi': {'gula_per_100': 5.0, 'satuan_umum': 'potong', 'berat_satuan_umum': 30},
            'nasi_putih': {'gula_per_100': 0.1, 'satuan_umum': 'porsi', 'berat_satuan_umum': 200},
            'gulai_ayam': {'gula_per_100': 4.0, 'satuan_umum': 'porsi', 'berat_satuan_umum': 400},
            
            # Saus & Bumbu
            'kecap_manis': {'gula_per_100': 60.0, 'satuan_umum': 'sendok makan', 'berat_satuan_umum': 15},
            'saus_tomat_botolan': {'gula_per_100': 22.0, 'satuan_umum': 'sendok makan', 'berat_satuan_umum': 15},
            'saus_sambal_botolan': {'gula_per_100': 15.0, 'satuan_umum': 'sendok makan', 'berat_satuan_umum': 15}
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
            return {'kemenkes': self.kemenkes_limit, 'aha': 'Profil pengguna belum diatur'}
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
            conversion_factors = {'sendok teh': 4, 'sendok makan': 12}
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
            'nama': nama_makanan.replace('_', ' ').title(), 'jumlah': jumlah, 'satuan': satuan,
            'gula_gram': round(total_gula, 2), 'waktu': datetime.now().strftime('%H:%M:%S')
        }
        
        self.daily_intake.append(item)
        return True, f"Berhasil menambahkan: {nama_makanan} ({jumlah} {satuan}) mengandung {total_gula:.2f}g gula."

    def calculate_daily_sugar(self) -> float:
        return sum(item['gula_gram'] for item in self.daily_intake)

    def reset_daily_intake(self):
        self.daily_intake = []

# ==============================================================================
# BAGIAN ANTARMUKA STREAMLIT (UI KEMBALI KE VERSI AWAL)
# ==============================================================================

def get_greeting():
    """Mendapatkan sapaan berdasarkan waktu."""
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return "Selamat Pagi"
    elif 12 <= hour < 15:
        return "Selamat Siang"
    elif 15 <= hour < 19:
        return "Selamat Sore"
    else:
        return "Selamat Malam"

# --- Inisialisasi Aplikasi ---
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
    
    menu = st.radio(
        "Pilih Menu:",
        ("Laporan Harian", "Profil Pengguna", "Tambah Asupan", "Database Makanan"),
        label_visibility="collapsed"
    )
    st.markdown("---")
    st.info("Pantau asupan gula harian Anda dengan mudah. Jaga kesehatan, batasi gula!")

# ==============================================================================
# --- Tampilan Halaman ---
# ==============================================================================

if menu == "Laporan Harian":
    st.title(get_greeting())
    user_name = st.session_state.tracker.user_profile.get('nama', 'Pengguna')
    st.subheader(f"Ini laporan gula harian Anda, {user_name}.")
    
    if not st.session_state.tracker.user_profile:
        st.warning("Silakan atur profil Anda terlebih dahulu melalui menu 'Profil Pengguna' di sidebar.")
    else:
        total_gula = st.session_state.tracker.calculate_daily_sugar()
        limits = st.session_state.tracker.get_recommended_limit()

        # Tampilkan metrik utama
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Gula Hari Ini", f"{total_gula:.2f} g")
        col2.metric("Batas Kemenkes", f"{limits['kemenkes']} g")
        col3.metric("Batas AHA", f"{limits['aha']} g")

        # Tampilkan progress bar
        st.markdown("---")
        st.subheader("Progres Menuju Batas Harian")
        
        # Progress untuk AHA
        if isinstance(limits['aha'], (int, float)) and limits['aha'] > 0:
            progress_aha = min(total_gula / limits['aha'], 1.0)
            st.write(f"Batas AHA ({limits['aha']}g)")
            st.progress(progress_aha)
            if total_gula > limits['aha']:
                st.error("Asupan gula Anda telah MELEBIHI batas yang direkomendasikan oleh AHA!")
        
        # Progress untuk Kemenkes
        if limits['kemenkes'] > 0:
            progress_kemenkes = min(total_gula / limits['kemenkes'], 1.0)
            st.write(f"Batas Kemenkes ({limits['kemenkes']}g)")
            st.progress(progress_kemenkes)
            if total_gula > limits['kemenkes']:
                st.error("Asupan gula Anda telah MELEBIHI batas yang direkomendasikan oleh Kemenkes!")
        
        st.markdown("---")
        st.subheader("Rincian Asupan Hari Ini")
        if not st.session_state.tracker.daily_intake:
            st.info("Belum ada asupan yang dicatat hari ini.")
        else:
            st.dataframe(st.session_state.tracker.daily_intake, use_container_width=True)

        if st.button("Reset Asupan Hari Ini"):
            st.session_state.tracker.reset_daily_intake()
            st.success("Asupan harian berhasil direset!")
            st.rerun()

elif menu == "Profil Pengguna":
    st.header("Profil Pengguna")
    with st.form("profile_form"):
        nama = st.text_input("Nama Lengkap", value=st.session_state.tracker.user_profile.get('nama', ''))
        col1, col2 = st.columns(2)
        with col1:
            umur = st.number_input("Umur (tahun)", min_value=1, max_value=120, value=st.session_state.tracker.user_profile.get('umur', 25))
        with col2:
            berat_badan = st.number_input("Berat Badan (kg)", min_value=1.0, max_value=300.0, value=st.session_state.tracker.user_profile.get('berat_badan', 60.0), format="%.1f")
        jenis_kelamin = st.selectbox("Jenis Kelamin", ["Pria", "Wanita"], index=0 if st.session_state.tracker.user_profile.get('jenis_kelamin') == 'pria' else 1)
        
        submitted = st.form_submit_button("Simpan Profil")
        if submitted:
            st.session_state.tracker.set_user_profile(nama, umur, jenis_kelamin, berat_badan)
            st.success(f"Profil untuk {nama} berhasil disimpan!")
            limits = st.session_state.tracker.get_recommended_limit()
            st.info(f"Batas konsumsi gula Anda: Kemenkes: {limits['kemenkes']}g, AHA: {limits['aha']}g per hari.")

elif menu == "Tambah Asupan":
    st.header("Tambah Asupan")
    if not st.session_state.tracker.user_profile:
        st.warning("Silakan atur profil Anda terlebih dahulu melalui menu 'Profil Pengguna' di sidebar.")
    else:
        food_options = sorted([name.replace('_', ' ').title() for name in st.session_state.tracker.food_database.keys()])
        nama_makanan_display = st.selectbox("Langkah 1: Pilih Makanan/Minuman", options=food_options, key="food_selector")
        
        nama_makanan_key = nama_makanan_display.lower().replace(' ', '_')
        food_info = st.session_state.tracker.food_database[nama_makanan_key]
        satuan_options = ["gram", "ml"]
        if 'satuan_umum' in food_info and food_info['satuan_umum']:
            satuan_options.append(food_info['satuan_umum'])
        satuan_options = sorted(list(set(satuan_options)))
        
        with st.form("add_food_form"):
            st.markdown(f"**Makanan yang dipilih:** {nama_makanan_display}")
            col1, col2 = st.columns(2)
            with col1:
                jumlah = st.number_input("Langkah 2: Masukkan Jumlah", min_value=0.1, value=1.0, step=0.1)
            with col2:
                satuan = st.selectbox("Langkah 3: Pilih Satuan", options=satuan_options)
            
            submitted = st.form_submit_button("Tambah ke Catatan Harian")
            if submitted:
                success, message = st.session_state.tracker.add_food_item(nama_makanan_display, jumlah, satuan)
                if success:
                    st.success(message)
                else:
                    st.error(message)

elif menu == "Database Makanan":
    st.header("Database Makanan")
    st.info("Cari makanan dan minuman untuk melihat estimasi kandungan gulanya.")
    
    categories = {
        'Makanan Berat & Sarapan': ['nasi_goreng', 'mie_goreng_instan', 'bubur_ayam', 'lontong_sayur', 'nasi_uduk', 'ayam_goreng', 'rendang_daging', 'sate_ayam', 'bakso', 'soto_ayam', 'gado_gado', 'sop_ayam', 'ikan_goreng', 'sushi', 'nasi_putih', 'gulai_ayam'],
        'Minuman Kemasan': ['teh_kotak', 'kopi_instan_sachet', 'minuman_isotonik', 'susu_uht_full_cream'],
        'Minuman': ['teh_manis', 'kopi_manis', 'soda_cola', 'sprite', 'coca_cola_zero', 'jus_jeruk_kemasan', 'es_teh_manis', 'minuman_energi', 'sirup', 'susu_coklat', 'yogurt_drink', 'air_kelapa_kemasan'],
        'Minuman Kekinian': ['boba_milk_tea', 'es_kopi_susu_gula_aren', 'thai_tea', 'cheese_tea', 'matcha_latte', 'greentea_latte', 'red_velvet_latte', 'es_coklat'],
        'Makanan Manis': ['coklat_batang', 'brownies_coklat', 'permen', 'kue_donat', 'es_krim', 'biskuit_manis', 'cake_coklat', 'cookies', 'pudding', 'jelly', 'marshmallow', 'kue_cubit', 'lapis_legit'],
        'Buah-buahan': ['apel', 'pisang', 'jeruk', 'mangga', 'anggur', 'strawberry', 'semangka', 'pepaya', 'nanas', 'melon', 'kurma'],
        'Makanan Olahan': ['roti_manis', 'sereal_manis', 'granola', 'yogurt_buah', 'selai_strawberry', 'madu', 'gula_pasir', 'gula_merah', 'kondensed_milk', 'roti_tawar', 'selai_kacang'],
        'Makanan Tradisional': ['klepon', 'onde_onde', 'es_cendol', 'es_doger', 'kolak', 'bubur_sumsum', 'martabak_manis', 'kue_lapis', 'dodol', 'wingko', 'serabi', 'getuk', 'cenil'],
        'Saus & Bumbu': ['kecap_manis', 'saus_tomat_botolan', 'saus_sambal_botolan']
    }

    search_term = st.text_input("Cari makanan...", placeholder="Contoh: Nasi Goreng")
    for category, items in categories.items():
        filtered_items = [item_key for item_key in items if search_term.lower() in item_key.replace('_', ' ').lower()]
        if not search_term or filtered_items:
            with st.expander(f"{category}", expanded=bool(search_term)):
                for item_key in sorted(filtered_items if search_term else items):
                    food_info = st.session_state.tracker.food_database[item_key]
                    item_name = item_key.replace('_', ' ').title()
                    gula = food_info['gula_per_100']
                    satuan_umum = food_info.get('satuan_umum', 'N/A')
                    berat_satuan = food_info.get('berat_satuan_umum', 'N/A')
                    st.markdown(f"**{item_name}** \n*Gula: `{gula}g`/100g | 1 {satuan_umum} ≈ `{berat_satuan}g`*")
