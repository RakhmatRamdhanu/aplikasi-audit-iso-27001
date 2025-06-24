import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF
import datetime
import firebase_admin
from firebase_admin import credentials, firestore
import json

# ======================================================================================
# INISIALISASI FIREBASE
# Menggunakan @st.cache_resource agar koneksi hanya dibuat sekali.
# ======================================================================================
@st.cache_resource
def init_firestore():
    try:
        # Mengambil kredensial dari st.secrets
        # Menggunakan json.loads untuk mengubah string menjadi dictionary
        key_dict = json.loads(st.secrets["FIREBASE_SERVICE_ACCOUNT"])
        cred = credentials.Certificate(key_dict)
        # Cek apakah aplikasi sudah diinisialisasi
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
        return firestore.client()
    except Exception as e:
        st.error(f"Gagal menginisialisasi Firebase: {e}")
        return None

db = init_firestore()

# ======================================================================================
# KONFIGURASI HALAMAN DAN JUDUL
# ======================================================================================
st.set_page_config(
    page_title="Audit ISO 27001:2022",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ Aplikasi Audit Internal ISO 27001:2022")
st.markdown("Aplikasi ini membantu dalam proses audit kepatuhan terhadap standar ISO/IEC 27001:2022 Annex A.")

# ======================================================================================
# DATA KONTROL ISO 27001:2022 (Sama seperti sebelumnya)
# (Disingkat di sini untuk keringkasan, gunakan daftar lengkap Anda)
# ======================================================================================
CONTROLS_DATA = [
    # A.5 Organizational Controls
    ("A.5.1", "Kebijakan Keamanan Informasi", "Apakah organisasi telah menetapkan, mendokumentasikan, dan mengkomunikasikan kebijakan keamanan informasi yang disetujui manajemen puncak?"),
    ("A.5.2", "Peran & Tanggung Jawab Keamanan", "Apakah peran dan tanggung jawab terkait keamanan informasi telah didefinisikan dan dialokasikan dengan jelas?"),
    # ... (LANJUTKAN DENGAN SEMUA 93 KONTROL ANDA)
]

# ======================================================================================
# FUNGSI DATABASE (Simpan & Muat)
# ======================================================================================
def save_audit_to_db(audit_data):
    if db:
        try:
            # Membuat dokumen baru dengan ID berupa timestamp
            doc_id = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
            doc_ref = db.collection('audits').document(doc_id)
            # Firestore lebih suka dictionary, jadi kita kirim langsung
            doc_ref.set({'audit_results': audit_data})
            st.success(f"Audit berhasil disimpan ke database dengan ID: {doc_id}")
        except Exception as e:
            st.error(f"Gagal menyimpan ke database: {e}")

def load_latest_audit_from_db():
    if db:
        try:
            # Mengambil audit terakhir berdasarkan nama dokumen (timestamp)
            audits_ref = db.collection('audits').order_by(firestore.Client.field_path.document_id(), direction=firestore.Query.DESCENDING).limit(1)
            results = audits_ref.get()
            if results:
                latest_audit = results[0].to_dict()
                st.session_state.audit_results = latest_audit.get('audit_results', {})
                st.success(f"Audit terakhir berhasil dimuat dari database (ID: {results[0].id}).")
                # Trigger rerun untuk me-refresh widget dengan data yang dimuat
                st.rerun()
            else:
                st.info("Tidak ada data audit sebelumnya yang ditemukan di database.")
        except Exception as e:
            st.error(f"Gagal memuat dari database: {e}")

# ======================================================================================
# TOMBOL AKSI DATABASE
# ======================================================================================
st.sidebar.header("Aksi Database")
if st.sidebar.button("💾 Simpan Audit Saat Ini"):
    if 'audit_results' in st.session_state and st.session_state.audit_results:
        save_audit_to_db(st.session_state.audit_results)
    else:
        st.sidebar.warning("Tidak ada data untuk disimpan.")

if st.sidebar.button("🔄 Muat Audit Terakhir"):
    load_latest_audit_from_db()


# ======================================================================================
# INISIALISASI SESSION STATE
# ======================================================================================
if 'audit_results' not in st.session_state:
    st.session_state.audit_results = {}

if 'ai_summary' not in st.session_state:
    st.session_state.ai_summary = ""


# ======================================================================================
# FORMULIR PENGISIAN AUDIT (Sama seperti sebelumnya)
# ... (Kode untuk menampilkan form tidak perlu diubah, karena sudah pakai session_state)
# ======================================================================================
col1, col2 = st.columns(2)
mid_point = len(CONTROLS_DATA) // 2
first_half = CONTROLS_DATA[:mid_point]
second_half = CONTROLS_DATA[mid_point:]

def display_control_form(control_list, column):
    for id, title, question in control_list:
        with column.expander(f"{id} - {title}"):
            st.markdown(f"**Pertanyaan:** *{question}*")
            
            jawaban_key = f"jawaban_{id}"
            likelihood_key = f"likelihood_{id}"
            impact_key = f"impact_{id}"
            catatan_key = f"catatan_{id}"

            # Mengambil nilai default dari session state
            default_jawaban_index = ["Ya", "Sebagian", "Tidak", "N/A"].index(st.session_state.audit_results.get(id, {}).get('Jawaban', 'N/A'))
            default_likelihood = st.session_state.audit_results.get(id, {}).get('Likelihood', 3)
            default_impact = st.session_state.audit_results.get(id, {}).get('Impact', 3)
            default_catatan = st.session_state.audit_results.get(id, {}).get('Catatan', "")

            st.write("---")
            jawaban = st.radio("Status Implementasi:", ["Ya", "Sebagian", "Tidak", "N/A"], index=default_jawaban_index, key=jawaban_key, horizontal=True)
            likelihood = st.slider("Likelihood (Peluang Risiko)", 1, 5, value=default_likelihood, key=likelihood_key)
            impact = st.slider("Impact (Dampak Risiko)", 1, 5, value=default_impact, key=impact_key)
            catatan = st.text_area("Catatan/Observasi Auditor:", value=default_catatan, key=catatan_key)

            st.session_state.audit_results[id] = {
                'Kontrol': id, 'Judul': title, 'Jawaban': jawaban,
                'Likelihood': likelihood, 'Impact': impact, 'Catatan': catatan
            }

display_control_form(first_half, col1)
display_control_form(second_half, col2)


# ======================================================================================
# PENGOLAHAN DATA DAN VISUALISASI HASIL (Sama seperti sebelumnya)
# ... (Semua kode untuk rekapitulasi, AI, dan PDF tidak perlu diubah)
# ======================================================================================
# (Letakkan kode rekap, analisis AI, dan ekspor PDF Anda di sini)
