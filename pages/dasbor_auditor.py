import streamlit as st
import pandas as pd
import json
import firebase_admin
from firebase_admin import credentials, firestore
import datetime

# --- Fungsi Inisialisasi Firebase (Diletakkan di sini agar mandiri) ---
@st.cache_resource
def init_firestore():
    try:
        # Cek apakah secret sudah ada
        if "FIREBASE_SERVICE_ACCOUNT" not in st.secrets:
            return None # Akan menampilkan error di bagian login jika None
            
        service_account_str = st.secrets["FIREBASE_SERVICE_ACCOUNT"]
        if not service_account_str.strip():
            return None

        key_dict = json.loads(service_account_str)
        cred = credentials.Certificate(key_dict)

        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
        return firestore.client()
    except Exception:
        # Jika ada error, kembalikan None agar bisa ditangani di bagian login
        return None

db = init_firestore()

# --- DATA KONTROL (Harus ada di sini juga untuk referensi judul) ---
ALL_CONTROLS = {
    "A.5.1": ("Kebijakan Keamanan Informasi", "Apakah organisasi telah menetapkan..."),
    "A.5.4": ("Tanggung Jawab Manajemen", "Apakah manajemen mewajibkan..."),
    "A.5.8": ("Keamanan Informasi dalam Manajemen Proyek", "Apakah keamanan informasi diintegrasikan..."),
    "A.5.10": ("Penggunaan Aset yang Dapat Diterima", "Apakah aturan untuk penggunaan aset..."),
    "A.5.12": ("Klasifikasi Informasi", "Apakah organisasi memiliki prosedur..."),
    "A.6.2": ("Syarat dan Ketentuan Kerja", "Apakah perjanjian kontrak kerja..."),
    "A.6.8": ("Pelaporan Peristiwa Keamanan", "Apakah mekanisme pelaporan peristiwa..."),
    "A.7.7": ("Meja dan Layar Bersih", "Apakah kebijakan 'meja bersih' dan 'layar bersih'..."),
    "A.8.1": ("Perangkat Titik Akhir Pengguna", "Apakah informasi yang disimpan atau diproses..."),
    "A.8.5": ("Otentikasi Aman", "Apakah sistem mewajibkan metode otentikasi..."),
    "A.8.7": ("Perlindungan terhadap Malware", "Apakah perlindungan terhadap malware..."),
    "A.8.13": ("Backup Informasi", "Apakah salinan cadangan (backup)..."),
    "A.8.15": ("Pencatatan (Logging)", "Apakah log aktivitas penting..."),
    "A.5.35": ("Peninjauan Independen Keamanan Informasi", "Apakah pendekatan organisasi..."),
    # (Lengkapi dengan semua 93 kontrol jika diperlukan untuk referensi judul)
}


st.set_page_config(layout="wide")

def display_auditor_dashboard():
    st.title("🔍 Dasbor Auditor")
    st.markdown("Area ini khusus untuk auditor melakukan analisis risiko dan melihat rekapitulasi.")
    
    @st.cache_data(ttl=300) # Cache data selama 5 menit
    def load_submissions(_db): # Menggunakan _db sebagai argumen
        if not _db:
            return []
        submissions_ref = _db.collection('auditee_submissions').stream()
        submissions = [doc for doc in submissions_ref]
        return submissions

    submissions = load_submissions(db)
    
    if not submissions:
        st.warning("Belum ada data checklist yang dikirim oleh auditee.")
        return

    submission_options = {doc.id: f"{doc.to_dict().get('role', 'N/A')} - {doc.id}" for doc in submissions}
    selected_submission_id = st.selectbox("Pilih Checklist untuk Dianalisis:", options=submission_options.keys(), format_func=lambda x: submission_options[x], index=None, placeholder="Pilih submission...")

    if selected_submission_id:
        submission_data = db.collection('auditee_submissions').document(selected_submission_id).get().to_dict()
        st.header(f"Analisis untuk: {submission_data.get('role', 'N/A')}")
        st.caption(f"ID Submission: {selected_submission_id}")

        analysis_results = []
        auditee_answers = submission_data.get('answers', {})

        for control_id, data in auditee_answers.items():
            st.markdown("---")
            title, _ = ALL_CONTROLS.get(control_id, ("Kontrol Tidak Ditemukan", ""))
            st.subheader(f"{control_id} - {title}")

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Jawaban Auditee:**")
                st.info(f"Status: **{data.get('jawaban')}**")
                st.markdown("**Catatan Auditee:**")
                st.caption(f"{data.get('catatan') if data.get('catatan') else 'Tidak ada catatan.'}")
            
            with col2:
                st.markdown("**Penilaian Auditor:**")
                likelihood = st.slider("Likelihood (1-5)", 1, 5, 3, key=f"like_{control_id}_{selected_submission_id}")
                impact = st.slider("Impact (1-5)", 1, 5, 3, key=f"impact_{control_id}_{selected_submission_id}")
                
                skor_risiko = likelihood * impact
                if skor_risiko >= 15: level = "Kritis"
                elif skor_risiko >= 9: level = "Tinggi"
                elif skor_risiko >= 4: level = "Sedang"
                else: level = "Rendah"
                
                st.metric("Skor Risiko", skor_risiko, delta=level, delta_color="inverse")

            analysis_results.append({'Kontrol': control_id, 'Judul': title, 'Jawaban Auditee': data.get('jawaban'), 'Likelihood': likelihood, 'Impact': impact, 'Skor Risiko': skor_risiko, 'Level Risiko': level})
        
        st.markdown("---")
        st.header("Rekapitulasi Analisis")
        
        if analysis_results:
            df = pd.DataFrame(analysis_results).sort_values(by="Skor Risiko", ascending=False)
            st.dataframe(df, use_container_width=True)

            st.subheader("Grafik Peringkat Risiko")
            df_chart = df[df['Skor Risiko'] > 0].set_index('Kontrol')
            if not df_chart.empty: st.bar_chart(df_chart["Skor Risiko"])

# --- Gerbang Login untuk Auditor ---
st.header("Login Auditor")

if db is None:
    st.error("Koneksi ke database gagal. Tidak dapat melanjutkan. Periksa konfigurasi secrets Anda.")
else:
    password = st.text_input("Masukkan Password:", type="password")
    
    if "AUDITOR_PASSWORD" not in st.secrets:
        st.error("Konfigurasi password auditor belum diatur di st.secrets.")
    elif password == st.secrets["AUDITOR_PASSWORD"]:
        st.success("Login Berhasil!")
        display_auditor_dashboard()
    elif password: # Jika input tidak kosong tapi salah
        st.error("Password yang Anda masukkan salah.")
