import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF
import datetime

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
# DATA KONTROL ISO 27001:2022
# Disusun dalam format (ID, Nama, Pertanyaan Deskriptif) untuk kejelasan.
# ======================================================================================
CONTROLS_DATA = [
    # A.5 Organizational Controls
    ("A.5.1", "Kebijakan Keamanan Informasi", "Apakah organisasi telah menetapkan, mendokumentasikan, dan mengkomunikasikan kebijakan keamanan informasi yang disetujui manajemen puncak?"),
    ("A.5.2", "Peran & Tanggung Jawab Keamanan", "Apakah peran dan tanggung jawab terkait keamanan informasi telah didefinisikan dan dialokasikan dengan jelas?"),
    ("A.5.3", "Pemisahan Tugas", "Apakah tugas dan area tanggung jawab yang saling bertentangan dipisahkan untuk mengurangi risiko penyalahgunaan?"),
    ("A.5.4", "Tanggung Jawab Manajemen", "Apakah manajemen mewajibkan semua personel untuk menerapkan keamanan informasi sesuai dengan kebijakan yang ditetapkan?"),
    ("A.5.5", "Kontak dengan Otoritas", "Apakah organisasi telah menjalin dan memelihara kontak dengan otoritas yang relevan (misalnya, penegak hukum, tim siber nasional)?"),
    ("A.5.6", "Kontak dengan Kelompok Kepentingan Khusus", "Apakah organisasi menjalin kontak dengan kelompok kepentingan khusus di bidang keamanan atau asosiasi profesional?"),
    ("A.5.7", "Intelijen Ancaman (Threat Intelligence)", "Apakah organisasi secara proaktif mengumpulkan dan menganalisis informasi tentang ancaman siber untuk meningkatkan pertahanan?"),
    ("A.5.8", "Keamanan Informasi dalam Manajemen Proyek", "Apakah keamanan informasi diintegrasikan ke dalam metodologi manajemen proyek organisasi?"),
    ("A.5.9", "Inventaris Informasi dan Aset Terkait", "Apakah inventaris aset informasi dan aset lain yang terkait (seperti hardware, software) telah dibuat dan dipelihara?"),
    ("A.5.10", "Penggunaan Aset yang Dapat Diterima", "Apakah aturan untuk penggunaan aset informasi dan TIK yang dapat diterima telah ditetapkan dan diimplementasikan?"),
    ("A.5.11", "Pengembalian Aset", "Apakah personel dan pihak eksternal wajib mengembalikan semua aset organisasi yang mereka miliki setelah berhenti bekerja?"),
    ("A.5.12", "Klasifikasi Informasi", "Apakah organisasi memiliki prosedur untuk mengklasifikasikan informasi berdasarkan tingkat kerahasiaan dan kepentingannya?"),
    ("A.5.13", "Pelabelan Informasi", "Apakah prosedur untuk pelabelan informasi (baik fisik maupun digital) sesuai dengan skema klasifikasi telah dikembangkan dan diterapkan?"),
    ("A.5.14", "Transfer Informasi", "Apakah aturan, prosedur, atau perjanjian untuk transfer informasi telah ada untuk semua jenis fasilitas transfer (misalnya, email, FTP, USB)?"),
    ("A.5.15", "Kontrol Akses", "Apakah kebijakan kontrol akses telah ditetapkan, didokumentasikan, dan ditinjau berdasarkan kebutuhan bisnis dan keamanan?"),
    ("A.5.16", "Manajemen Identitas", "Apakah siklus hidup penuh dari identitas pengguna (dari pendaftaran hingga penghapusan) dikelola secara terpusat dan aman?"),
    ("A.5.17", "Informasi Otentikasi", "Apakah alokasi dan pengelolaan informasi otentikasi (seperti password, token) dikendalikan melalui proses yang aman?"),
    ("A.5.18", "Hak Akses", "Apakah hak akses ke informasi dan aset lainnya diberikan, ditinjau, dimodifikasi, dan dicabut sesuai dengan kebijakan kontrol akses?"),
    ("A.5.19", "Keamanan Informasi dalam Hubungan Pemasok", "Apakah proses dan prosedur telah ditetapkan untuk mengelola risiko keamanan informasi yang terkait dengan penggunaan produk atau layanan dari pemasok?"),
    ("A.5.20", "Mengatasi Keamanan dalam Perjanjian Pemasok", "Apakah persyaratan keamanan informasi yang relevan telah ditetapkan dan disepakati dalam setiap perjanjian dengan pemasok?"),
    ("A.5.21", "Mengelola Keamanan Rantai Pasokan TIK", "Apakah proses telah diterapkan untuk mengelola risiko dalam rantai pasokan produk dan layanan TIK?"),
    ("A.5.22", "Pemantauan & Peninjauan Layanan Pemasok", "Apakah organisasi secara teratur memantau, meninjau, dan mengaudit layanan yang diberikan oleh pemasok terkait keamanan?"),
    ("A.5.23", "Keamanan Informasi untuk Layanan Cloud", "Apakah proses untuk akuisisi, penggunaan, pengelolaan, dan penghentian layanan cloud telah ditetapkan sesuai dengan kebutuhan keamanan?"),
    ("A.5.24", "Perencanaan Manajemen Insiden", "Apakah organisasi telah merencanakan dan mempersiapkan respons terhadap insiden keamanan informasi dengan mendefinisikan peran dan prosedur?"),
    ("A.5.25", "Penilaian Peristiwa Keamanan", "Apakah ada kriteria untuk menilai peristiwa keamanan informasi dan memutuskan apakah peristiwa tersebut merupakan insiden keamanan?"),
    ("A.5.26", "Respons terhadap Insiden Keamanan", "Apakah insiden keamanan informasi ditanggapi sesuai dengan prosedur yang telah didokumentasikan?"),
    ("A.5.27", "Belajar dari Insiden Keamanan", "Apakah pengetahuan yang diperoleh dari analisis insiden keamanan digunakan untuk memperkuat kontrol keamanan?"),
    ("A.5.28", "Pengumpulan Bukti", "Apakah prosedur telah ditetapkan untuk mengidentifikasi, mengumpulkan, memperoleh, dan menjaga bukti terkait insiden keamanan?"),
    ("A.5.29", "Keamanan Informasi selama Gangguan", "Apakah organisasi merencanakan bagaimana menjaga tingkat keamanan informasi selama terjadi gangguan atau bencana?"),
    ("A.5.30", "Kesiapan TIK untuk Kelangsungan Bisnis", "Apakah kesiapan TIK untuk kelangsungan bisnis direncanakan, diimplementasikan, dipelihara, dan diuji berdasarkan tujuan kelangsungan bisnis?"),
    ("A.5.31", "Identifikasi Persyaratan Hukum & Kontrak", "Apakah persyaratan hukum, peraturan, dan kontrak yang relevan dengan keamanan informasi telah diidentifikasi dan didokumentasikan?"),
    ("A.5.32", "Hak Kekayaan Intelektual", "Apakah organisasi menerapkan prosedur yang sesuai untuk melindungi hak kekayaan intelektual (HKI)?"),
    ("A.5.33", "Perlindungan Catatan", "Apakah catatan dan data dilindungi dari kehilangan, perusakan, pemalsuan, akses tidak sah, dan rilis tidak sah?"),
    ("A.5.34", "Privasi dan Perlindungan PII", "Apakah organisasi mengidentifikasi dan memenuhi persyaratan terkait privasi dan perlindungan Informasi Identitas Pribadi (PII)?"),
    ("A.5.35", "Peninjauan Independen Keamanan Informasi", "Apakah pendekatan organisasi terhadap pengelolaan keamanan informasi ditinjau secara independen secara berkala?"),
    ("A.5.36", "Kepatuhan terhadap Kebijakan & Standar", "Apakah kepatuhan terhadap kebijakan, aturan, dan standar keamanan informasi organisasi ditinjau secara berkala?"),
    ("A.5.37", "Prosedur Operasi yang Terdokumentasi", "Apakah prosedur operasi untuk fasilitas pemrosesan informasi didokumentasikan dan tersedia untuk personel yang membutuhkannya?"),

    # A.6 People Controls
    ("A.6.1", "Penyaringan (Screening)", "Apakah pemeriksaan latar belakang pada semua kandidat untuk menjadi personel dilakukan sesuai dengan hukum dan peraturan yang berlaku?"),
    ("A.6.2", "Syarat dan Ketentuan Kerja", "Apakah perjanjian kontrak kerja menyatakan tanggung jawab personel terhadap keamanan informasi?"),
    ("A.6.3", "Pelatihan Kesadaran Keamanan", "Apakah personel secara berkala menerima pelatihan dan pembaruan mengenai kesadaran keamanan informasi yang relevan dengan peran mereka?"),
    ("A.6.4", "Proses Disipliner", "Apakah ada proses disipliner formal yang ditetapkan dan dikomunikasikan untuk personel yang melakukan pelanggaran keamanan?"),
    ("A.6.5", "Tanggung Jawab setelah Pemutusan Kerja", "Apakah tanggung jawab dan tugas keamanan informasi yang tetap berlaku setelah pemutusan atau perubahan pekerjaan didefinisikan dan ditegakkan?"),
    ("A.6.6", "Perjanjian Kerahasiaan", "Apakah perjanjian kerahasiaan atau non-disclosure (NDA) yang mencerminkan kebutuhan organisasi untuk melindungi informasi digunakan?"),
    ("A.6.7", "Kerja Jarak Jauh (Remote Working)", "Apakah ada kebijakan dan kontrol keamanan yang diterapkan untuk personel yang bekerja dari jarak jauh untuk melindungi informasi?"),
    ("A.6.8", "Pelaporan Peristiwa Keamanan", "Apakah mekanisme pelaporan peristiwa keamanan informasi telah ditetapkan, memungkinkan personel untuk melaporkan insiden secepat mungkin?"),

    # A.7 Physical Controls
    ("A.7.1", "Perimeter Keamanan Fisik", "Apakah perimeter keamanan (misalnya, dinding, gerbang, pagar) digunakan untuk melindungi area yang berisi informasi dan fasilitas pemrosesan penting?"),
    ("A.7.2", "Pintu Masuk Fisik", "Apakah area aman dilindungi oleh kontrol pintu masuk yang sesuai untuk memastikan hanya personel yang berwenang yang diizinkan masuk?"),
    ("A.7.3", "Mengamankan Kantor, Ruangan, dan Fasilitas", "Apakah keamanan fisik untuk kantor, ruangan, dan fasilitas telah dirancang dan diterapkan?"),
    ("A.7.4", "Pemantauan Keamanan Fisik", "Apakah lokasi dipantau secara terus-menerus terhadap akses fisik yang tidak sah? (misalnya, CCTV)"),
    ("A.7.5", "Perlindungan terhadap Ancaman Fisik", "Apakah perlindungan terhadap ancaman fisik dan lingkungan, seperti bencana alam (banjir, kebakaran), telah dirancang dan diterapkan?"),
    ("A.7.6", "Bekerja di Area Aman", "Apakah prosedur dan kontrol keamanan untuk bekerja di area aman telah dirancang dan diterapkan?"),
    ("A.7.7", "Meja dan Layar Bersih", "Apakah kebijakan 'meja bersih' untuk kertas dan media penyimpanan yang dapat dilepas, dan kebijakan 'layar bersih' untuk fasilitas pemrosesan informasi diterapkan?"),
    ("A.7.8", "Penempatan dan Perlindungan Peralatan", "Apakah peralatan ditempatkan dan dilindungi untuk mengurangi risiko dari ancaman lingkungan dan akses yang tidak sah?"),
    ("A.7.9", "Keamanan Aset di Luar Lokasi", "Apakah aset yang digunakan di luar lokasi organisasi (misalnya, laptop untuk WFH) diamankan?"),
    ("A.7.10", "Media Penyimpanan", "Apakah media penyimpanan (misalnya, hard disk, USB drive) dikelola melalui siklus hidupnya (perolehan, penggunaan, transportasi, pembuangan) secara aman?"),
    ("A.7.11", "Pemeliharaan Peralatan", "Apakah peralatan dipelihara dengan benar untuk memastikan ketersediaan, integritas, dan kerahasiaannya yang berkelanjutan?"),
    ("A.7.12", "Pembuangan Media", "Apakah media penyimpanan dibuang dengan aman ketika tidak lagi diperlukan?"),
    ("A.7.13", "Pembuangan Peralatan", "Apakah item peralatan yang berisi media penyimpanan dibuang atau digunakan kembali dengan aman untuk mencegah kebocoran data?"),
    ("A.7.14", "Peralatan Pengguna yang Tidak Diawasi", "Apakah pengguna memastikan bahwa peralatan yang tidak diawasi memiliki perlindungan yang sesuai?"),

    # A.8 Technological Controls
    ("A.8.1", "Perangkat Titik Akhir Pengguna", "Apakah informasi yang disimpan, diproses, atau dapat diakses melalui perangkat pengguna (endpoint) dilindungi?"),
    ("A.8.2", "Hak Akses Istimewa", "Apakah alokasi dan penggunaan hak akses istimewa (admin/root) dibatasi dan dikelola dengan ketat?"),
    ("A.8.3", "Pembatasan Akses ke Informasi", "Apakah akses ke informasi dan aset lainnya dibatasi sesuai dengan kebijakan kontrol akses yang ditetapkan?"),
    ("A.8.4", "Akses ke Kode Sumber", "Apakah akses baca dan tulis ke kode sumber (source code), alat pengembangan, dan perpustakaan perangkat lunak dikelola dengan baik?"),
    ("A.8.5", "Otentikasi Aman", "Apakah teknologi dan prosedur otentikasi yang aman diterapkan untuk mengontrol akses ke sistem dan data? (misalnya, MFA)"),
    ("A.8.6", "Manajemen Kapasitas", "Apakah penggunaan sumber daya dipantau dan disesuaikan agar sesuai dengan kebutuhan kapasitas saat ini dan yang diharapkan?"),
    ("A.8.7", "Perlindungan terhadap Malware", "Apakah perlindungan terhadap malware diimplementasikan dan didukung oleh kesadaran pengguna yang sesuai?"),
    ("A.8.8", "Manajemen Kerentanan Teknis", "Apakah informasi tentang kerentanan teknis sistem diperoleh, dievaluasi, dan tindakan yang tepat diambil secara tepat waktu? (misalnya, patching)"),
    ("A.8.9", "Manajemen Konfigurasi", "Apakah konfigurasi hardware, software, layanan, dan jaringan dikelola dan didokumentasikan dengan aman?"),
    ("A.8.10", "Penghapusan Informasi", "Apakah alat digunakan untuk menghapus data yang disimpan di media penyimpanan secara aman sehingga tidak dapat dipulihkan lagi?"),
    ("A.8.11", "Penyamaran Data (Data Masking)", "Apakah penyamaran data (misalnya, anonimisasi, pseudonymisasi) digunakan sesuai dengan kebijakan kontrol akses dan persyaratan lainnya?"),
    ("A.8.12", "Pencegahan Kebocoran Data", "Apakah tindakan pencegahan kebocoran data (DLP) diterapkan pada sistem, jaringan, dan perangkat yang memproses, menyimpan, atau mengirimkan informasi sensitif?"),
    ("A.8.13", "Backup Informasi", "Apakah salinan cadangan (backup) informasi, perangkat lunak, dan sistem dibuat dan diuji secara teratur?"),
    ("A.8.14", "Redundansi Sumber Daya", "Apakah fasilitas pemrosesan informasi diimplementasikan dengan redundansi yang cukup untuk memenuhi persyaratan ketersediaan?"),
    ("A.8.15", "Pencatatan (Logging)", "Apakah log yang mencatat aktivitas, pengecualian, kesalahan, dan peristiwa keamanan lainnya dibuat, disimpan, dan ditinjau?"),
    ("A.8.16", "Aktivitas Pemantauan", "Apakah jaringan, sistem, dan aplikasi dipantau untuk perilaku anomali dan peristiwa keamanan informasi?"),
    ("A.8.17", "Sinkronisasi Jam", "Apakah jam dari semua sistem pemrosesan informasi yang relevan disinkronkan ke sumber waktu yang disetujui?"),
    ("A.8.18", "Penggunaan Utilitas Program Istimewa", "Apakah penggunaan program utilitas yang dapat mengesampingkan kontrol sistem dan aplikasi dibatasi dan dikontrol dengan ketat?"),
    ("A.8.19", "Instalasi Perangkat Lunak", "Apakah aturan untuk instalasi perangkat lunak pada sistem operasional telah ditetapkan dan diimplementasikan?"),
    ("A.8.20", "Keamanan Jaringan", "Apakah jaringan dan perangkat jaringan diamankan, dikelola, dan dikontrol untuk melindungi sistem dan informasi?"),
    ("A.8.21", "Keamanan Layanan Jaringan", "Apakah fitur keamanan, tingkat layanan, dan persyaratan layanan dari layanan jaringan diidentifikasi dan diimplementasikan?"),
    ("A.8.22", "Pemisahan Jaringan", "Apakah kelompok layanan informasi, pengguna, dan sistem informasi dipisahkan dalam jaringan (segmentasi)?"),
    ("A.8.23", "Penyaringan Web (Web Filtering)", "Apakah akses ke situs web eksternal dikelola untuk mengurangi paparan konten berbahaya?"),
    ("A.8.24", "Penggunaan Kriptografi", "Apakah aturan untuk penggunaan kriptografi yang efektif, termasuk manajemen kunci kriptografi, telah ditetapkan dan diterapkan?"),
    ("A.8.25", "Siklus Hidup Pengembangan yang Aman", "Apakah aturan untuk pengembangan perangkat lunak dan sistem yang aman telah ditetapkan dan diterapkan?"),
    ("A.8.26", "Persyaratan Keamanan Aplikasi", "Apakah persyaratan keamanan informasi ditentukan pada tahap awal pengembangan atau akuisisi aplikasi?"),
    ("A.8.27", "Prinsip Arsitektur Sistem yang Aman", "Apakah prinsip-prinsip untuk rekayasa arsitektur sistem yang aman telah ditetapkan dan diterapkan?"),
    ("A.8.28", "Pengkodean Aman (Secure Coding)", "Apakah prinsip pengkodean yang aman diterapkan untuk pengembangan perangkat lunak internal?"),
    ("A.8.29", "Pengujian Keamanan dalam Pengembangan", "Apakah proses pengujian keamanan didefinisikan dan dilakukan secara teratur selama siklus hidup pengembangan?"),
    ("A.8.30", "Pengembangan yang Dialihdayakan", "Apakah organisasi mengawasi dan memantau aktivitas pengembangan perangkat lunak yang dialihdayakan (outsourced)?"),
    ("A.8.31", "Pemisahan Lingkungan Pengembangan", "Apakah lingkungan pengembangan, pengujian, dan produksi dipisahkan dan diamankan?"),
    ("A.8.32", "Manajemen Perubahan", "Apakah perubahan pada fasilitas pemrosesan informasi dan sistem dikendalikan melalui proses manajemen perubahan formal?"),
    ("A.8.33", "Informasi Pengujian", "Apakah informasi pengujian dipilih, dilindungi, dan dikelola dengan hati-hati?"),
    ("A.8.34", "Perlindungan Informasi Sistem selama Pengujian", "Apakah data pengujian dan lingkungan pengujian dilindungi secara memadai?"),
]

# ======================================================================================
# INISIALISASI SESSION STATE
# Ini adalah 'memori' aplikasi untuk menyimpan semua input.
# ======================================================================================
if 'audit_results' not in st.session_state:
    st.session_state.audit_results = {}

if 'ai_summary' not in st.session_state:
    st.session_state.ai_summary = ""

# ======================================================================================
# FORMULIR PENGISIAN AUDIT
# Loop melalui setiap kontrol dan buat widget input.
# ======================================================================================
# Membuat dua kolom untuk tata letak yang lebih rapi
col1, col2 = st.columns(2)
# Membagi kontrol menjadi dua bagian untuk ditampilkan di dua kolom
mid_point = len(CONTROLS_DATA) // 2
first_half = CONTROLS_DATA[:mid_point]
second_half = CONTROLS_DATA[mid_point:]

# Fungsi untuk menampilkan form per kontrol
def display_control_form(control_list, column):
    for id, title, question in control_list:
        with column.expander(f"{id} - {title}"):
            st.markdown(f"**Pertanyaan:** *{question}*")
            
            # Menggunakan st.session_state untuk menyimpan nilai agar tidak hilang
            # Membuat kunci unik untuk setiap widget
            jawaban_key = f"jawaban_{id}"
            likelihood_key = f"likelihood_{id}"
            impact_key = f"impact_{id}"
            catatan_key = f"catatan_{id}"

            # Mengambil nilai default dari session state jika ada
            default_jawaban_index = ["Ya", "Sebagian", "Tidak", "N/A"].index(st.session_state.audit_results.get(id, {}).get('Jawaban', 'N/A'))
            default_likelihood = st.session_state.audit_results.get(id, {}).get('Likelihood', 3)
            default_impact = st.session_state.audit_results.get(id, {}).get('Impact', 3)
            default_catatan = st.session_state.audit_results.get(id, {}).get('Catatan', "")

            st.write("---")
            jawaban = st.radio(
                "Status Implementasi:",
                ["Ya", "Sebagian", "Tidak", "N/A"],
                index=default_jawaban_index,
                key=jawaban_key,
                horizontal=True
            )
            likelihood = st.slider("Likelihood (Peluang Risiko)", 1, 5, value=default_likelihood, key=likelihood_key)
            impact = st.slider("Impact (Dampak Risiko)", 1, 5, value=default_impact, key=impact_key)
            catatan = st.text_area("Catatan/Observasi Auditor:", value=default_catatan, key=catatan_key)

            # Simpan hasil ke session_state setiap kali ada perubahan
            st.session_state.audit_results[id] = {
                'Kontrol': id,
                'Judul': title,
                'Jawaban': jawaban,
                'Likelihood': likelihood,
                'Impact': impact,
                'Catatan': catatan
            }

# Menampilkan form di masing-masing kolom
display_control_form(first_half, col1)
display_control_form(second_half, col2)


# ======================================================================================
# PENGOLAHAN DATA DAN VISUALISASI HASIL
# ======================================================================================
st.write("---")
st.header("📊 Rekapitulasi & Analisis Risiko")

# Cek apakah ada data untuk diproses
if st.session_state.audit_results:
    processed_data = []
    for id, data in st.session_state.audit_results.items():
        # Hitung skor risiko hanya jika relevan (bukan 'N/A')
        if data['Jawaban'] != 'N/A':
            skor_risiko = data['Likelihood'] * data['Impact']
        else:
            skor_risiko = 0
            
        # Tentukan level risiko
        if skor_risiko >= 15:
            level = "Kritis"
            warna = "🔴"
        elif skor_risiko >= 9:
            level = "Tinggi"
            warna = "🟠"
        elif skor_risiko >= 4:
            level = "Sedang"
            warna = "🟡"
        else:
            level = "Rendah"
            warna = "🟢"

        # Tambahkan data yang sudah diproses ke list
        entry = data.copy()
        entry['Skor Risiko'] = skor_risiko
        entry['Level Risiko'] = f"{warna} {level}"
        processed_data.append(entry)

    # Konversi ke DataFrame untuk kemudahan analisis dan tampilan
    df = pd.DataFrame(processed_data)
    df = df.sort_values(by="Skor Risiko", ascending=False)
    
    st.subheader("Tabel Hasil Audit")
    # Mengatur kolom yang akan ditampilkan
    st.dataframe(df[[
        'Kontrol', 'Judul', 'Jawaban', 'Likelihood', 'Impact', 'Skor Risiko', 'Level Risiko', 'Catatan'
    ]], use_container_width=True)

    # Visualisasi data
    st.subheader("Grafik Peringkat Risiko per Kontrol")
    df_chart = df[df['Skor Risiko'] > 0].set_index('Kontrol')
    if not df_chart.empty:
        st.bar_chart(df_chart["Skor Risiko"])
    else:
        st.info("Tidak ada risiko yang teridentifikasi untuk divisualisasikan.")

else:
    st.info("Silakan isi kuesioner audit di atas untuk melihat rekapitulasi.")


# ======================================================================================
# FUNGSI ANALISIS DENGAN AI (LLM)
# ======================================================================================
st.header("🤖 Analisis & Rekomendasi Otomatis (AI)")

if st.button("Jalankan Analisis AI"):
    if 'df' in locals() and not df.empty:
        # Filter kontrol dengan risiko Sedang, Tinggi, atau Kritis
        df_risiko = df[df['Skor Risiko'] >= 4]

        if not df_risiko.empty:
            with st.spinner("Menghubungi AI untuk menganalisis data... Proses ini mungkin memakan waktu beberapa saat."):
                # Membuat prompt yang kaya konteks untuk AI
                prompt_parts = [
                    "Anda adalah seorang konsultan keamanan siber dan auditor ISO 27001 yang berpengalaman.",
                    "Berdasarkan data hasil audit berikut, di mana 'Skor Risiko' dihitung dari 'Likelihood' x 'Impact':\n"
                ]
                for _, row in df_risiko.iterrows():
                    prompt_parts.append(
                        f"- Kontrol {row['Kontrol']} ({row['Judul']}): Status Implementasi '{row['Jawaban']}', "
                        f"menghasilkan Skor Risiko {row['Skor Risiko']} ({row['Level Risiko']}). "
                        f"Catatan: {row['Catatan']}"
                    )
                
                prompt_parts.append(
                    "\nTugas Anda:\n"
                    "1. Buat **Ringkasan Eksekutif** dari temuan utama. Soroti area risiko paling signifikan.\n"
                    "2. Berikan **Rekomendasi Mitigasi** yang konkret dan dapat ditindaklanjuti untuk setiap kontrol dengan risiko TINGGI dan KRITIS. Kelompokkan rekomendasi berdasarkan kontrolnya.\n"
                    "3. Format output dengan jelas menggunakan Markdown."
                )
                
                full_prompt = "\n".join(prompt_parts)

                try:
                    # Menggunakan API Key dari st.secrets
                    api_key = st.secrets.get("AI21_API_KEY", "")
                    if not api_key:
                        st.error("AI21_API_KEY tidak ditemukan di st.secrets. Mohon konfigurasikan terlebih dahulu.")
                    else:
                        headers = {
                            "Authorization": f"Bearer {api_key}",
                            "Content-Type": "application/json"
                        }
                        payload = {
                            "prompt": full_prompt,
                            "numResults": 1,
                            "maxTokens": 1024, # Token lebih besar untuk output yang komprehensif
                            "temperature": 0.5,
                            "topKReturn": 0,
                            "topP": 1.0,
                            "stopSequences": []
                        }
                        response = requests.post(
                            "https://api.ai21.com/studio/v1/j2-ultra/completions",
                            headers=headers,
                            json=payload
                        )
                        response.raise_for_status() # Akan error jika status code 4xx atau 5xx
                        
                        result_json = response.json()
                        
                        if "completions" in result_json and result_json["completions"]:
                            ai_result = result_json["completions"][0]["data"]["text"]
                            st.session_state.ai_summary = ai_result.strip()
                        else:
                            st.session_state.ai_summary = "AI tidak memberikan hasil yang valid. Coba lagi."
                            st.warning(f"Respon dari AI: {result_json}")

                except requests.exceptions.RequestException as e:
                    st.session_state.ai_summary = f"Gagal menghubungi server AI. Error: {e}"
                    st.error(st.session_state.ai_summary)
                except Exception as e:
                    st.session_state.ai_summary = f"Terjadi kesalahan tak terduga: {e}"
                    st.error(st.session_state.ai_summary)
        else:
            st.success("Analisis selesai. Tidak ada risiko tingkat Sedang atau lebih tinggi yang ditemukan.")
            st.session_state.ai_summary = "Tidak ada risiko signifikan yang teridentifikasi yang memerlukan rekomendasi AI."
    else:
        st.warning("Tidak ada data audit untuk dianalisis. Silakan isi formulir terlebih dahulu.")

# Selalu tampilkan hasil AI jika ada di session state
if st.session_state.ai_summary:
    st.markdown("### Hasil Analisis AI:")
    st.markdown(st.session_state.ai_summary)

# ======================================================================================
# FUNGSI EKSPOR LAPORAN KE PDF
# ======================================================================================
st.header("⬇️ Ekspor Laporan")

if st.button("Siapkan Laporan untuk Diunduh"):
    if 'df' in locals() and not df.empty:
        class PDF(FPDF):
            def header(self):
                self.set_font('Arial', 'B', 12)
                self.cell(0, 10, 'Laporan Audit Internal ISO 27001:2022', 0, 1, 'C')
                self.set_font('Arial', '', 9)
                self.cell(0, 5, f'Tanggal Dibuat: {datetime.date.today().strftime("%d-%m-%Y")}', 0, 1, 'C')
                self.ln(10)

            def footer(self):
                self.set_y(-15)
                self.set_font('Arial', 'I', 8)
                self.cell(0, 10, f'Halaman {self.page_no()}/{{nb}}', 0, 0, 'C')

        pdf = PDF()
        pdf.alias_nb_pages()
        pdf.add_page()
        pdf.set_font("Arial", size=10)

        # Menambahkan data tabel ke PDF
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(0, 10, "1. Rekapitulasi Hasil Audit", ln=True)
        pdf.set_font("Arial", size=9)
        
        for _, row in df.iterrows():
            pdf.set_font('Arial', 'B', 9)
            pdf.multi_cell(0, 5, f"{row['Kontrol']} - {row['Judul']}")
            pdf.set_font("Arial", '', 9)
            pdf.multi_cell(0, 5, f"  Status: {row['Jawaban']} | Skor Risiko: {row['Skor Risiko']} | Level: {row['Level Risiko']}")
            pdf.multi_cell(0, 5, f"  Catatan: {row['Catatan'] if row['Catatan'] else 'Tidak ada'}")
            pdf.ln(3)

        # Menambahkan hasil analisis AI jika ada
        if st.session_state.ai_summary:
            pdf.add_page()
            pdf.set_font('Arial', 'B', 11)
            pdf.cell(0, 10, "2. Analisis & Rekomendasi AI", ln=True)
            pdf.set_font("Arial", size=9)
            # FPDF tidak bisa handle semua karakter unicode, jadi kita encode
            # Menggunakan 'latin-1' dengan 'replace' adalah cara aman untuk menghindari error
            encoded_summary = st.session_state.ai_summary.encode('latin-1', 'replace').decode('latin-1')
            pdf.multi_cell(0, 5, encoded_summary)
        
        # Menyiapkan data PDF untuk diunduh
        pdf_output = pdf.output(dest='S').encode('latin-1')
        
        st.download_button(
            label="📥 Unduh Laporan PDF Sekarang",
            data=pdf_output,
            file_name=f"laporan_audit_iso27001_{datetime.date.today().strftime('%Y%m%d')}.pdf",
            mime="application/pdf"
        )
        st.success("Laporan PDF berhasil dibuat! Klik tombol di atas untuk mengunduh.")
    else:
        st.warning("Tidak ada data untuk diekspor. Silakan isi formulir dan proses data terlebih dahulu.")

