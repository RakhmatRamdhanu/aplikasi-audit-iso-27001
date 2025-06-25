import streamlit as st
import datetime
import json
import firebase_admin
from firebase_admin import credentials, firestore

# --- Fungsi Inisialisasi Firebase (Diletakkan di sini agar mandiri) ---
@st.cache_resource
def init_firestore():
    try:
        if "FIREBASE_SERVICE_ACCOUNT" not in st.secrets:
            return None
        service_account_str = st.secrets["FIREBASE_SERVICE_ACCOUNT"]
        if not service_account_str.strip():
            return None
        key_dict = json.loads(service_account_str)
        cred = credentials.Certificate(key_dict)
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
        return firestore.client()
    except Exception as e:
        # Menampilkan error di halaman jika gagal, tapi tidak menghentikan aplikasi
        st.error(f"Koneksi ke Firebase gagal: {e}")
        return None

db = init_firestore()

st.set_page_config(layout="wide")
st.title("📝 Formulir Checklist Keamanan Informasi")

# --- DATA KONTROL (Sama seperti sebelumnya, letakkan di sini) ---
ALL_CONTROLS = {
    "A.5.1": ("Kebijakan Keamanan Informasi", "Apakah organisasi telah menetapkan, mendokumentasikan, dan mengkomunikasikan kebijakan keamanan informasi yang disetujui manajemen puncak?"),
    "A.5.4": ("Tanggung Jawab Manajemen", "Apakah manajemen mewajibkan semua personel untuk menerapkan keamanan informasi sesuai dengan kebijakan yang ditetapkan?"),
    "A.5.8": ("Keamanan Informasi dalam Manajemen Proyek", "Apakah keamanan informasi diintegrasikan ke dalam metodologi manajemen proyek organisasi?"),
    "A.5.10": ("Penggunaan Aset yang Dapat Diterima", "Apakah aturan untuk penggunaan aset informasi dan TIK yang dapat diterima telah ditetapkan dan diimplementasikan?"),
    "A.5.12": ("Klasifikasi Informasi", "Apakah organisasi memiliki prosedur untuk mengklasifikasikan informasi berdasarkan tingkat kerahasiaan dan kepentingannya?"),
    "A.6.2": ("Syarat dan Ketentuan Kerja", "Apakah perjanjian kontrak kerja menyatakan tanggung jawab personel terhadap keamanan informasi?"),
    "A.6.8": ("Pelaporan Peristiwa Keamanan", "Apakah mekanisme pelaporan peristiwa keamanan informasi telah ditetapkan, memungkinkan personel untuk melaporkan insiden secepat mungkin?"),
    "A.7.7": ("Meja dan Layar Bersih", "Apakah kebijakan 'meja bersih' dan 'layar bersih' diterapkan secara konsisten?"),
    "A.8.1": ("Perangkat Titik Akhir Pengguna", "Apakah informasi yang disimpan atau diproses melalui perangkat pengguna (laptop, PC) dilindungi?"),
    "A.8.5": ("Otentikasi Aman", "Apakah sistem mewajibkan metode otentikasi yang aman, seperti password yang kompleks dan/atau MFA?"),
    "A.8.7": ("Perlindungan terhadap Malware", "Apakah perlindungan terhadap malware (misalnya, antivirus) diimplementasikan dan diperbarui secara berkala?"),
    "A.8.13": ("Backup Informasi", "Apakah salinan cadangan (backup) informasi penting dibuat dan diuji secara teratur?"),
    "A.8.15": ("Pencatatan (Logging)", "Apakah log aktivitas penting pada sistem dibuat dan disimpan untuk keperluan audit?"),
    "A.5.35": ("Peninjauan Independen Keamanan Informasi", "Apakah pendekatan organisasi terhadap pengelolaan keamanan informasi ditinjau secara independen secara berkala?"),
}
CONTROLS_BY_ROLE = {
    "Ketua STMKG": ["A.5.1", "A.5.4", "A.5.35"],
    "Kabag/Kadum": ["A.5.10", "A.6.2", "A.7.7"],
    "Kaprodi": ["A.5.12", "A.6.2"],
    "IT STMKG": ["A.5.8", "A.8.1", "A.8.5", "A.8.7", "A.8.13", "A.8.15"],
    "Pengguna Akhir": ["A.5.10", "A.6.8", "A.7.7", "A.8.5"]
}

# --- FUNGSI SIMPAN KE DATABASE ---
def save_auditee_submission(role, submission_data):
    if db:
        try:
            doc_id = f"{role.replace(' ', '_')}_{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}"
            doc_ref = db.collection('auditee_submissions').document(doc_id)
            doc_ref.set(submission_data)
            st.success(f"Terima kasih! Jawaban Anda telah berhasil disimpan dengan ID: {doc_id}")
            st.balloons()
        except Exception as e:
            st.error(f"Gagal menyimpan ke database: {e}")
    else:
        st.error("Koneksi database tidak tersedia. Jawaban tidak dapat disimpan.")

# --- TAMPILAN UTAMA HALAMAN CHECKLIST ---
# (Sisa kode sama persis dengan sebelumnya, tidak perlu diubah)
if 'user_role' not in st.session_state:
    st.warning("⚠️ Silakan pilih peran Anda di halaman 'Home' terlebih dahulu.")
    st.page_link("Home.py", label="Kembali ke Halaman Utama", icon="🏠")
else:
    role = st.session_state['user_role']
    st.info(f"Anda mengisi checklist sebagai: **{role}**")
    relevant_control_ids = CONTROLS_BY_ROLE.get(role, [])
    if not relevant_control_ids:
        st.error(f"Tidak ada checklist yang didefinisikan untuk peran '{role}'.")
    else:
        with st.form(key='checklist_form'):
            auditee_answers = {}
            for control_id in relevant_control_ids:
                title, question = ALL_CONTROLS[control_id]
                with st.expander(f"{control_id} - {title}", expanded=True):
                    st.markdown(f"**Pertanyaan:** *{question}*")
                    jawaban = st.radio("Status Implementasi Saat Ini:", options=["Sesuai", "Sebagian", "Tidak Sesuai", "Tidak Tahu"], key=f"jawaban_{control_id}", horizontal=True)
                    catatan = st.text_area("Bukti atau Catatan Pendukung:", key=f"catatan_{control_id}", height=100)
                    auditee_answers[control_id] = {"jawaban": jawaban, "catatan": catatan}
            submitted = st.form_submit_button("Simpan Jawaban Checklist")
            if submitted:
                submission_data = {"role": role, "timestamp": datetime.datetime.now(), "answers": auditee_answers}
                save_auditee_submission(role, submission_data)
