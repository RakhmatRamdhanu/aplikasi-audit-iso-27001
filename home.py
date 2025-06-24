import streamlit as st
import json
import firebase_admin
from firebase_admin import credentials, firestore

# --- Fungsi Inisialisasi Firebase (ditaruh di sini agar bisa di-cache) ---
@st.cache_resource
def init_firestore():
    try:
        if "FIREBASE_SERVICE_ACCOUNT" not in st.secrets:
            st.error("Kunci 'FIREBASE_SERVICE_ACCOUNT' tidak ditemukan di st.secrets.")
            return None
        
        service_account_str = st.secrets["FIREBASE_SERVICE_ACCOUNT"]
        if not service_account_str.strip():
            st.error("Nilai 'FIREBASE_SERVICE_ACCOUNT' di st.secrets kosong.")
            return None

        key_dict = json.loads(service_account_str)
        cred = credentials.Certificate(key_dict)

        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
        
        return firestore.client()
    except Exception as e:
        st.error(f"Gagal menginisialisasi Firebase. Error: {e}")
        return None

# Panggil fungsi inisialisasi di awal
db = init_firestore()


# --- Konfigurasi Halaman ---
st.set_page_config(
    page_title="Audit ISO 27001:2022",
    page_icon="🛡️",
    layout="centered"
)

# --- Konten Halaman Utama ---
st.title("🛡️ Sistem Audit Internal ISO 27001:2022")
st.image("https://placehold.co/600x200/003366/FFFFFF?text=Selamat+Datang+di+STMKG", use_column_width=True)

st.header("Pilih Peran Anda")

st.markdown("""
Selamat datang di sistem audit internal keamanan informasi STMKG. 
Aplikasi ini dirancang untuk memfasilitasi proses audit kepatuhan terhadap standar internasional ISO/IEC 27001:2022.

**Silakan pilih peran Anda di bawah ini untuk memulai.**
""")

# Daftar peran yang tersedia
roles = [
    "--- Pilih Peran Anda ---",
    "Ketua STMKG",
    "Kabag/Kadum",
    "Kaprodi",
    "IT STMKG",
    "Pengguna Akhir"
]

# Simpan pilihan peran ke session_state agar bisa diakses oleh halaman lain
selected_role = st.selectbox(
    "Saya adalah:",
    roles,
    index=0 # Default ke pilihan pertama
)

if selected_role != "--- Pilih Peran Anda ---":
    st.session_state['user_role'] = selected_role
    st.success(f"Anda telah memilih peran sebagai **{selected_role}**.")
    st.info("👈 Silakan pilih halaman **'1_Isi_Checklist'** di sidebar sebelah kiri untuk melanjutkan.")
else:
    # Hapus peran jika kembali ke pilihan default
    if 'user_role' in st.session_state:
        del st.session_state['user_role']

st.markdown("---")
st.caption("Dikembangkan untuk riset internal di STMKG.")
