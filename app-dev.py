import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF

st.set_page_config(page_title="Audit ISO 27001:2022", layout="wide")
st.title("🛡️ Aplikasi Audit ISO 27001:2022")

# 96 kontrol ISO 27001:2022 (bahasa sederhana)
data_kontrol = [
    {"id": "A.5.1", "judul": "Kebijakan Keamanan Informasi (menetapkan aturan umum keamanan)"},
    {"id": "A.5.2", "judul": "Peran & Tanggung Jawab Keamanan (menetapkan siapa yang bertanggung jawab atas keamanan)"},
    {"id": "A.5.3", "judul": "Manajemen Sumber Daya Keamanan (mengatur sumber daya keamanan seperti software dan personel)"},
    {"id": "A.5.4", "judul": "Kontak dengan Pihak Eksternal (mengatur hubungan keamanan dengan vendor, mitra)"},
    {"id": "A.5.5", "judul": "Kepatuhan terhadap Persyaratan Hukum (memastikan patuh terhadap hukum dan peraturan)"},
    {"id": "A.5.6", "judul": "Pengendalian Akses Informasi (mengatur siapa yang bisa akses data)"},
    {"id": "A.5.7", "judul": "Kebijakan Penggunaan Perangkat Mobile (mengatur penggunaan HP, laptop di luar kantor)"},
    {"id": "A.5.8", "judul": "Kerja Jarak Jauh (mengamankan kerja remote dan WFH)"},

    {"id": "A.6.1", "judul": "Proses Pengelolaan Aset (mengatur cara mencatat dan melindungi aset TI)"},
    {"id": "A.6.2", "judul": "Klasifikasi Informasi (mengelompokkan data sesuai sensitivitasnya)"},
    {"id": "A.6.3", "judul": "Penanganan Media Penyimpanan (mengamankan USB, harddisk, dokumen)"},

    {"id": "A.7.1", "judul": "Keamanan SDM Sebelum Bekerja (misalnya kontrak, pemeriksaan latar belakang)"},
    {"id": "A.7.2", "judul": "Selama Bekerja (pelatihan keamanan, pengawasan)"},
    {"id": "A.7.3", "judul": "Setelah Bekerja (penghapusan akses, serah terima data)"},

    {"id": "A.8.1", "judul": "Pengelolaan Akses Pengguna (buat akun, izin akses)"},
    {"id": "A.8.2", "judul": "Kontrol Akses (atur izin berdasarkan jabatan)"},
    {"id": "A.8.3", "judul": "Kredensial & Otentikasi (atur password, MFA)"},
    {"id": "A.8.4", "judul": "Akses Informasi Aplikasi (kontrol akses ke software)"},
    {"id": "A.8.5", "judul": "Akses ke Kode Sumber (mengamankan source code)"},

    {"id": "A.9.1", "judul": "Keamanan Fisik dan Lingkungan (akses ruang server, CCTV, bencana)"},
    {"id": "A.9.2", "judul": "Perangkat dan Media (mengamankan hardware)"},

    {"id": "A.10.1", "judul": "Pengelolaan Operasi TI (jadwal backup, pemeliharaan)"},
    {"id": "A.10.2", "judul": "Perlindungan Malware (antivirus, filter email)"},
    {"id": "A.10.3", "judul": "Pencatatan Aktivitas (log user, monitoring aktivitas)"},
    {"id": "A.10.4", "judul": "Pemisahan Lingkungan Pengembangan (dev/test/prod environment)"},

    {"id": "A.11.1", "judul": "Keamanan Komunikasi (VPN, enkripsi, firewall)"},
    {"id": "A.11.2", "judul": "Transfer Informasi (prosedur kirim data ke luar)"},

    {"id": "A.12.1", "judul": "Pengamanan Sistem Aplikasi (secure coding, review aplikasi)"},
    {"id": "A.12.2", "judul": "Manajemen Kerentanan Teknis (patching, update sistem)"},

    {"id": "A.13.1", "judul": "Manajemen Insiden Keamanan (lapor dan tangani kejadian keamanan)"},
    {"id": "A.13.2", "judul": "Pembelajaran dari Insiden (analisis akar masalah)"},

    {"id": "A.14.1", "judul": "Keamanan Informasi untuk Kesiapsiagaan (continuity plan, DRP)"},
    {"id": "A.14.2", "judul": "Pengujian Kesiapan (simulasi insiden dan recovery)"},

    {"id": "A.15.1", "judul": "Kepatuhan pada Persyaratan (audit, dokumentasi hukum)"},
    {"id": "A.15.2", "judul": "Penghapusan Informasi (penghapusan data lama, sesuai regulasi)"},

    {"id": "A.16.1", "judul": "Keamanan Proyek & Pengembangan (security by design)"},
    {"id": "A.16.2", "judul": "Manajemen Perubahan (evaluasi risiko perubahan sistem)"}
]

rekap_data = []

for kontrol in data_kontrol:
    st.markdown(f"## {kontrol['id']} - {kontrol['judul']}")

    with st.expander("👤 Diisi oleh Narasumber"):
        jawaban = st.radio(f"Apakah kontrol {kontrol['id']} diterapkan?", ["Ya", "Sebagian", "Tidak"], key=f"jawaban_{kontrol['id']}")

    with st.expander("🧑‍💼 Diisi oleh Auditor"):
        likelihood = st.slider("Likelihood (1-5)", 1, 5, 3, key=f"like_{kontrol['id']}")
        impact = st.slider("Impact (1-5)", 1, 5, 3, key=f"impact_{kontrol['id']}")
        catatan = st.text_area("Catatan Auditor", key=f"catatan_{kontrol['id']}")

    skor_map = {"Ya": 5, "Sebagian": 3, "Tidak": 1}
    implementasi_skor = skor_map[jawaban]
    skor_risiko = likelihood * impact

    if skor_risiko <= 5:
        level = "Rendah"
        warna = "🟢"
    elif skor_risiko <= 10:
        level = "Sedang"
        warna = "🟡"
    else:
        level = "Tinggi"
        warna = "🔴"

    st.metric("Skor Risiko", skor_risiko, delta=level + " " + warna)

    rekap_data.append({
        "Kontrol": kontrol['id'],
        "Judul": kontrol['judul'],
        "Jawaban": jawaban,
        "Likelihood": likelihood,
        "Impact": impact,
        "Risiko": skor_risiko,
        "Level": level,
        "Catatan": catatan
    })

# Rekap akhir
st.subheader("📊 Rekapitulasi Risiko")
df = pd.DataFrame(rekap_data)
st.dataframe(df)
st.bar_chart(df.set_index("Kontrol")["Risiko"])

# Analisis dengan AI21 Studio (Jurassic-2)
if st.button("🔎 Analisis Otomatis (AI21)"):
    isi_prompt = ""
    for item in rekap_data:
        isi_prompt += f"- {item['Kontrol']} {item['Judul']}: {item['Jawaban']}, Risiko: {item['Risiko']} ({item['Level']})\n"
    isi_prompt += "\nBuatkan ringkasan hasil audit dan rekomendasi mitigasi untuk kontrol dengan risiko sedang dan tinggi."

    with st.spinner("Menghubungi AI21..."):
        headers = {
            "Authorization": f"Bearer {st.secrets['AI21_API_KEY']}",
            "Content-Type": "application/json"
        }
        payload = {
            "prompt": isi_prompt,
            "numResults": 1,
            "maxTokens": 500,
            "temperature": 0.7,
            "topKReturn": 0,
            "topP": 1.0,
            "stopSequences": ["###"]
        }
        response = requests.post(
            "https://api.ai21.com/studio/v1/j2-light/completions",
            headers=headers,
            json=payload
        )
        st.write(response.json())
        result_json = response.json()
	if "completions" in result_json:
	    hasil = result_json["completions"][0]["data"]["text"]
	    st.text_area("📝 Ringkasan Audit Otomatis:", hasil, height=300)
	elif "error" in result_json:
	    st.error(f"❌ Gagal: {result_json['error'].get('message', 'Terjadi kesalahan.')}")
	else:
	    st.error("❌ Respons dari AI21 tidak dikenali.")

       # hasil = response.json()["completions"][0]["data"]["text"]
       # st.text_area("📝 Ringkasan Audit Otomatis:", hasil, height=300)
        


# Export PDF
if st.button("⬇️ Export PDF"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, "Rekapitulasi Audit ISO 27001:2022\n")
    for item in rekap_data:
        teks = f"{item['Kontrol']} - {item['Judul']}\nJawaban: {item['Jawaban']}\nRisiko: {item['Risiko']} ({item['Level']})\nCatatan: {item['Catatan']}\n"
        pdf.multi_cell(0, 10, teks + "\n")
    if 'hasil' in locals():
        pdf.multi_cell(0, 10, "Ringkasan AI21:\n" + hasil)
    pdf.output("laporan_audit.pdf")
    st.success("PDF berhasil diekspor sebagai laporan_audit.pdf")


