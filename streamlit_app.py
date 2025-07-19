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
        (Database lengkap seperti yang Anda sediakan)
        """
        self.food_database = {
            'teh_manis': {'gula_per_100': 10.0, 'satuan_umum': 'gelas', 'berat_satuan_umum': 200},
            'kopi_manis': {'gula_per_100': 8.0, 'satuan_umum': 'cangkir', 'berat_satuan_umum': 150},
            'soda_cola': {'gula_per_100': 10.6, 'satuan_umum': 'kaleng', 'berat_satuan_umum': 250},
            'jus_jeruk_kemasan': {'gula_per_100': 9.0, 'satuan_umum': 'kotak', 'berat_satuan_umum': 200},
            'boba_milk_tea': {'gula_per_100': 18.0, 'satuan_umum': 'cup', 'berat_satuan_umum': 350},
            'es_kopi_susu_gula_aren': {'gula_per_100': 15.0, 'satuan_umum': 'cup', 'berat_satuan_umum': 250},
            'coklat_batang': {'gula_per_100': 47.0, 'satuan_umum': 'batang', 'berat_satuan_umum': 50},
            'brownies_coklat': {'gula_per_100': 40.0, 'satuan_umum': 'potong', 'berat_satuan_umum': 60},
            'permen': {'gula_per_100': 85.0, 'satuan_umum': 'buah', 'berat_satuan_umum': 5},
            'kue_donat': {'gula_per_100': 15.0, 'satuan_umum': 'buah', 'berat_satuan_umum': 50},
            'es_krim': {'gula_per_100': 14.0, 'satuan_umum': 'scoop', 'berat_satuan_umum': 60},
            'apel': {'gula_per_100': 10.4, 'satuan_umum': 'buah', 'berat_satuan_umum': 180},
            'pisang': {'gula_per_100': 12.2, 'satuan_umum': 'buah', 'berat_satuan_umum': 120},
            'nasi_goreng': {'gula_per_100': 4.0, 'satuan_umum': 'porsi', 'berat_satuan_umum': 350},
            'mie_goreng_instan': {'gula_per_100': 8.0, 'satuan_umum': 'porsi', 'berat_satuan_umum': 120},
            'kecap_manis': {'gula_per_100': 60.0, 'satuan_umum': 'sendok makan', 'berat_satuan_umum': 15},
            # ... (Tambahkan sisa database lengkap Anda di sini) ...
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
        # Logika konversi tetap sama
        if satuan == 'gram':
            jumlah_gram = jumlah
        elif satuan == food_info.get('satuan_umum'):
            jumlah_gram = jumlah * food_info.get('berat_satuan_umum', 0)
        else:
            return False, f"Satuan '{satuan}' tidak valid untuk {nama_makanan}."
        
        if jumlah_gram == 0:
            return False, f"Tidak dapat menghitung berat untuk satuan '{satuan}'."

        kandungan_gula_per_100g = food_info['gula_per_100']
        total_gula = (kandungan_gula_per_100g * jumlah_gram) / 100
        
        item = {
            'Nama': nama_makanan.replace('_', ' ').title(), 'Jumlah': jumlah, 'Satuan': satuan,
            'Gula (g)': round(total_gula, 2), 'Waktu': datetime.now().strftime('%H:%M:%S')
        }
        
        self.daily_intake.append(item)
        return True, f"Berhasil menambahkan: {nama_makanan} ({jumlah} {satuan}) mengandung {total_gula:.2f}g gula."

    def calculate_daily_sugar(self) -> float:
        return sum(item['Gula (g)'] for item in self.daily_intake)

    def reset_daily_intake(self):
        self.daily_intake = []

# ==============================================================================
# BAGIAN ANTARMUKA STREAMLIT (VERSI REVISI)
# ==============================================================================

def get_greeting():
    """Mendapatkan sapaan dan ikon berdasarkan waktu."""
    hour = datetime.now().hour
    if 5 <= hour < 12: return "Selamat Pagi", "☀️"
    if 12 <= hour < 15: return "Selamat Siang", "နေ့"
    if 15 <= hour < 19: return "Selamat Sore", "🌇"
    return "Selamat Malam", "🌙"

# --- Inisialisasi Aplikasi ---
if 'tracker' not in st.session_state:
    st.session_state.tracker = SugarTracker()

st.set_page_config(page_title="GulaCheck", page_icon="🍭", layout="wide")

# --- Sidebar ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2723/2723331.png", width=100)
    st.title("GulaCheck")
    
    user_name = st.session_state.tracker.user_profile.get('nama', '').split(" ")[0]
    if user_name:
        st.write(f"Halo, **{user_name}**!")
    
    menu = st.radio(
        "Pilih Menu:",
        ("Dasbor Harian", "Tambah Asupan", "Riwayat & Analisis", "Profil Pengguna", "Database Makanan"),
        key="menu_selection"
    )
    st.markdown("---")
    st.info("Pantau asupan gula harian Anda dengan mudah. Jaga kesehatan, batasi gula!")
    st.markdown(f"<p style='text-align: center; font-size: 0.8em;'>Versi 2.0</p>", unsafe_allow_html=True)


# ==============================================================================
# --- Tampilan Halaman (REVISI TOTAL) ---
# ==============================================================================

if menu == "Dasbor Harian":
    greeting, icon = get_greeting()
    user_name = st.session_state.tracker.user_profile.get('nama', 'Pengguna')
    st.title(f"{greeting}, {user_name}! {icon}")
    st.markdown("Berikut adalah ringkasan dasbor konsumsi gula Anda untuk hari ini.")
    
    if not st.session_state.tracker.user_profile:
        st.warning("⚠️ Silakan atur profil Anda terlebih dahulu melalui menu **'Profil Pengguna'** di sidebar.")
    else:
        total_gula = st.session_state.tracker.calculate_daily_sugar()
        limits = st.session_state.tracker.get_recommended_limit()

        # --- Kartu Metrik Utama ---
        with st.container(border=True):
            col1, col2, col3 = st.columns(3)
            col1.metric("🍬 Total Gula Hari Ini", f"{total_gula:.2f} g")
            col2.metric("🇮🇩 Batas Kemenkes", f"{limits['kemenkes']} g")
            col3.metric("❤️ Batas AHA", f"{limits.get('aha', 'N/A')} g")
        
        st.markdown("---")
        
        # --- Visualisasi Progres ---
        st.subheader("📊 Progres Menuju Batas Harian")
        with st.container(border=True):
            aha_limit = limits.get('aha')
            if isinstance(aha_limit, (int, float)) and aha_limit > 0:
                st.write(f"**Progres Batas AHA ({aha_limit}g)**")
                progress_aha = min(total_gula / aha_limit, 1.0)
                st.progress(progress_aha, text=f"{progress_aha*100:.0f}%")
                if total_gula > aha_limit:
                    st.error("🚨 Asupan gula Anda telah MELEBIHI batas yang direkomendasikan oleh AHA!", icon="🚨")
                elif progress_aha >= 0.75:
                    st.warning("⚠️ Asupan gula Anda mendekati batas AHA. Hati-hati!", icon="⚠️")
                else:
                    st.success("✅ Asupan gula Anda masih dalam batas aman AHA.", icon="✅")
                st.write("") # Spacer

            kemenkes_limit = limits['kemenkes']
            if kemenkes_limit > 0:
                st.write(f"**Progres Batas Kemenkes ({kemenkes_limit}g)**")
                progress_kemenkes = min(total_gula / kemenkes_limit, 1.0)
                st.progress(progress_kemenkes, text=f"{progress_kemenkes*100:.0f}%")
                if total_gula > kemenkes_limit:
                    st.error("🚨 Asupan gula Anda telah MELEBIHI batas yang direkomendasikan oleh Kemenkes!", icon="🚨")
                elif progress_kemenkes >= 0.75:
                    st.warning("⚠️ Asupan gula Anda mendekati batas Kemenkes. Hati-hati!", icon="⚠️")
                else:
                    st.success("✅ Asupan gula Anda masih dalam batas aman Kemenkes.", icon="✅")

        st.markdown("---")
        
        # --- Rincian Asupan ---
        st.subheader("📜 Log Makanan Hari Ini")
        if not st.session_state.tracker.daily_intake:
            st.info("Belum ada asupan yang dicatat hari ini. Tambahkan di menu 'Tambah Asupan'.")
        else:
            df_daily = pd.DataFrame(st.session_state.tracker.daily_intake)
            st.dataframe(df_daily, use_container_width=True, hide_index=True)
        
        # --- Tombol Aksi ---
        if st.button("💾 Simpan & Reset Hari Ini", use_container_width=True):
            st.session_state.tracker.archive_and_reset_day()
            st.success("Asupan hari ini berhasil diarsipkan dan direset! Halaman akan dimuat ulang.")
            st.balloons()
            st.rerun()

elif menu == "Tambah Asupan":
    st.header("➕ Tambah Asupan Makanan/Minuman")
    if not st.session_state.tracker.user_profile:
        st.warning("⚠️ Silakan atur profil Anda terlebih dahulu melalui menu 'Profil Pengguna' di sidebar.")
    else:
        food_options = sorted([name.replace('_', ' ').title() for name in st.session_state.tracker.food_database.keys()])
        
        col1, col2 = st.columns([2, 1])

        with col1:
            nama_makanan_display = st.selectbox("Langkah 1: Pilih Makanan/Minuman", options=food_options, key="food_selector")
            nama_makanan_key = nama_makanan_display.lower().replace(' ', '_')
            food_info = st.session_state.tracker.food_database[nama_makanan_key]
            
            with st.form("add_food_form"):
                st.markdown("**Langkah 2: Tentukan Jumlah**")
                form_col1, form_col2 = st.columns(2)
                
                jumlah = form_col1.number_input("Jumlah", min_value=0.1, value=1.0, step=0.1, label_visibility="collapsed")
                
                satuan_options = ["gram"]
                if 'satuan_umum' in food_info and food_info['satuan_umum']:
                    satuan_options.append(food_info['satuan_umum'])
                
                satuan = form_col2.selectbox("Satuan", options=satuan_options, label_visibility="collapsed")
                
                submitted = st.form_submit_button("➕ Tambahkan ke Catatan", use_container_width=True)
                if submitted:
                    success, message = st.session_state.tracker.add_food_item(nama_makanan_display, jumlah, satuan)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
        with col2:
            st.markdown("**Info Cepat**")
            with st.container(border=True):
                 gula = food_info['gula_per_100']
                 satuan_umum = food_info.get('satuan_umum', 'N/A')
                 berat_satuan = food_info.get('berat_satuan_umum', 'N/A')
                 st.markdown(f"""
                 **{nama_makanan_display}**
                 - **Gula:** `{gula}g` / 100g
                 - **Sajian Umum:** `{berat_satuan}g` per {satuan_umum}
                 """)


elif menu == "Riwayat & Analisis":
    st.header("📈 Riwayat & Analisis Konsumsi Gula")
    history_data = st.session_state.tracker.history

    if not history_data:
        st.info("Belum ada riwayat yang tersimpan. Gunakan aplikasi dan tekan 'Simpan & Reset Hari Ini' di Dasbor Harian untuk mulai membangun riwayat Anda.")
    else:
        # --- Ringkasan Statistik ---
        st.subheader("💡 Ringkasan Statistik")
        df_history = pd.DataFrame.from_dict(history_data, orient='index')
        df_history.index = pd.to_datetime(df_history.index)
        
        avg_sugar = df_history['total_gula'].mean()
        max_sugar_day = df_history['total_gula'].idxmax()
        max_sugar_val = df_history['total_gula'].max()
        days_over_limit = (df_history['total_gula'] > df_history['limit_kemenkes']).sum()

        with st.container(border=True):
            col1, col2, col3 = st.columns(3)
            col1.metric("Rata-rata Gula Harian", f"{avg_sugar:.1f} g")
            col2.metric("Konsumsi Tertinggi", f"{max_sugar_val:.1f} g", help=f"Pada {max_sugar_day.strftime('%d %b %Y')}")
            col3.metric("Hari Melebihi Batas", f"{days_over_limit} hari")

        st.markdown("---")

        # --- Grafik ---
        st.subheader("Tren Konsumsi Gula vs Batas Harian")
        chart_data = df_history[['total_gula', 'limit_kemenkes', 'limit_aha']].rename(columns={
            'total_gula': 'Total Gula (g)',
            'limit_kemenkes': 'Batas Kemenkes (g)',
            'limit_aha': 'Batas AHA (g)'
        })
        st.line_chart(chart_data.tail(30)) # Tampilkan 30 hari terakhir
        
        st.markdown("---")

        # --- Tabel Riwayat ---
        st.subheader("📖 Detail Riwayat Konsumsi")
        display_df = chart_data.reset_index().rename(columns={'index': 'Tanggal'}).sort_values(by="Tanggal", ascending=False)
        st.dataframe(display_df, use_container_width=True, hide_index=True)


elif menu == "Profil Pengguna":
    st.header("👤 Pengaturan Profil Pengguna")
    st.markdown("Atur profil Anda agar GulaCheck dapat memberikan rekomendasi batas gula yang sesuai.")
    
    with st.container(border=True):
        with st.form("profile_form"):
            nama = st.text_input("Nama Lengkap", value=st.session_state.tracker.user_profile.get('nama', ''))
            
            col1, col2 = st.columns(2)
            umur = col1.number_input("Umur (tahun)", min_value=1, max_value=120, value=st.session_state.tracker.user_profile.get('umur', 25))
            berat_badan = col2.number_input("Berat Badan (kg)", min_value=1.0, max_value=300.0, value=st.session_state.tracker.user_profile.get('berat_badan', 60.0), format="%.1f")
            
            gender_options = ["Pria", "Wanita"]
            gender_index = gender_options.index(st.session_state.tracker.user_profile.get('jenis_kelamin', 'pria').title())
            jenis_kelamin = st.selectbox("Jenis Kelamin", gender_options, index=gender_index)
            
            submitted = st.form_submit_button("💾 Simpan Profil", use_container_width=True)
            if submitted:
                st.session_state.tracker.set_user_profile(nama, umur, jenis_kelamin, berat_badan)
                st.success(f"Profil untuk **{nama}** berhasil disimpan!")
                limits = st.session_state.tracker.get_recommended_limit()
                st.info(f"Batas konsumsi gula Anda telah diperbarui: Kemenkes: {limits['kemenkes']}g, AHA: {limits['aha']}g per hari.")


elif menu == "Database Makanan":
    st.header("📚 Database Makanan & Minuman")
    st.info("Cari makanan dan minuman untuk melihat estimasi kandungan gulanya.")
    
    search_term = st.text_input("🔍 Cari makanan...", placeholder="Contoh: Nasi Goreng")
    
    # Kategori bisa dibuat lebih dinamis jika diinginkan
    categories = {
        'Minuman': ['teh_manis', 'kopi_manis', 'soda_cola', 'jus_jeruk_kemasan'],
        'Minuman Kekinian': ['boba_milk_tea', 'es_kopi_susu_gula_aren'],
        'Makanan Manis': ['coklat_batang', 'brownies_coklat', 'permen', 'kue_donat', 'es_krim'],
        'Buah-buahan': ['apel', 'pisang'],
        'Makanan Berat': ['nasi_goreng', 'mie_goreng_instan'],
        'Bumbu & Saus': ['kecap_manis']
        # (Lengkapi dengan kategori dan item dari database Anda)
    }

    # Untuk menyederhanakan, kita akan iterasi langsung dari database yang ada
    all_items = sorted(st.session_state.tracker.food_database.keys())
    
    filtered_items = [
        item_key for item_key in all_items 
        if search_term.lower() in item_key.replace('_', ' ').lower()
    ]

    for item_key in filtered_items:
        with st.container(border=True):
            food_info = st.session_state.tracker.food_database[item_key]
            item_name = item_key.replace('_', ' ').title()
            gula = food_info['gula_per_100']
            satuan_umum = food_info.get('satuan_umum', 'N/A')
            berat_satuan = food_info.get('berat_satuan_umum', 'N/A')
            
            st.markdown(f"""
            **{item_name}**
            - **Kandungan Gula:** `{gula}g` / 100g
            - **Ukuran Saji Umum:** `{berat_satuan}g` per 1 {satuan_umum}
            """)
