import streamlit as st
import pandas as pd
from Home import init_firestore # Mengimpor fungsi dari file utama

st.set_page_config(layout="wide")
db = init_firestore()

def display_auditor_dashboard():
    st.title("🔍 Dasbor Auditor")
    st.markdown("Area ini khusus untuk auditor melakukan analisis risiko dan melihat rekapitulasi.")
    
    # Fungsi untuk memuat semua submission dari auditee
    @st.cache_data(ttl=300) # Cache data selama 5 menit
    def load_submissions():
        if not db:
            return []
        submissions_ref = db.collection('auditee_submissions').stream()
        submissions = [doc for doc in submissions_ref]
        return submissions

    submissions = load_submissions()
    
    if not submissions:
        st.warning("Belum ada data checklist yang dikirim oleh auditee.")
        return

    # Tampilkan pilihan submission
    submission_options = {doc.id: f"{doc.to_dict().get('role', 'N/A')} - {doc.id}" for doc in submissions}
    selected_submission_id = st.selectbox("Pilih Checklist untuk Dianalisis:", options=submission_options.keys(), format_func=lambda x: submission_options[x])

    if selected_submission_id:
        # Ambil data lengkap dari submission yang dipilih
        submission_data = db.collection('auditee_submissions').document(selected_submission_id).get().to_dict()
        st.header(f"Analisis untuk: {submission_data.get('role', 'N/A')}")
        st.caption(f"ID Submission: {selected_submission_id}")

        analysis_results = []
        auditee_answers = submission_data.get('answers', {})

        for control_id, data in auditee_answers.items():
            st.markdown("---")
            title, _ = ALL_CONTROLS[control_id]
            st.subheader(f"{control_id} - {title}")

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Jawaban Auditee:**")
                st.info(f"Status: **{data.get('jawaban')}**")
                st.markdown("**Catatan Auditee:**")
                st.caption(f"{data.get('catatan') if data.get('catatan') else 'Tidak ada catatan.'}")
            
            with col2:
                st.markdown("**Penilaian Auditor:**")
                likelihood = st.slider("Likelihood (1-5)", 1, 5, 3, key=f"like_{control_id}")
                impact = st.slider("Impact (1-5)", 1, 5, 3, key=f"impact_{control_id}")
                
                skor_risiko = likelihood * impact
                if skor_risiko >= 15:
                    level = "Kritis"
                elif skor_risiko >= 9:
                    level = "Tinggi"
                elif skor_risiko >= 4:
                    level = "Sedang"
                else:
                    level = "Rendah"
                
                st.metric("Skor Risiko", skor_risiko, delta=level, delta_color="inverse")

            analysis_results.append({
                'Kontrol': control_id, 'Judul': title, 'Jawaban Auditee': data.get('jawaban'), 
                'Likelihood': likelihood, 'Impact': impact, 'Skor Risiko': skor_risiko, 'Level Risiko': level
            })
        
        st.markdown("---")
        st.header("Rekapitulasi Analisis")
        
        if analysis_results:
            df = pd.DataFrame(analysis_results).sort_values(by="Skor Risiko", ascending=False)
            st.dataframe(df, use_container_width=True)

            st.subheader("Grafik Peringkat Risiko")
            df_chart = df[df['Skor Risiko'] > 0].set_index('Kontrol')
            if not df_chart.empty:
                st.bar_chart(df_chart["Skor Risiko"])

# --- Gerbang Login untuk Auditor ---
st.header("Login Auditor")
password = st.text_input("Masukkan Password:", type="password")

# Cek password dari st.secrets
# Anda harus menambahkan AUDITOR_PASSWORD di secrets Anda!
# Contoh: AUDITOR_PASSWORD = "passwordrahasia123"
if "AUDITOR_PASSWORD" not in st.secrets:
    st.error("Konfigurasi password auditor belum diatur di st.secrets.")
elif password == st.secrets["AUDITOR_PASSWORD"]:
    st.success("Login Berhasil!")
    display_auditor_dashboard()
elif password: # Jika input tidak kosong tapi salah
    st.error("Password yang Anda masukkan salah.")
