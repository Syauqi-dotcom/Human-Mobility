# Panduan Lengkap: Project Human Mobility (JogjaPulse)

Panduan ini berisi langkah dari menjalankan kode sampai pengumpulan tugas.

---

## 0. Isi folder

```
Pak Widyawan/
├── code/
│   ├── 01_etl.py          # ambil data, bersihkan, gabung 2 sumber
│   ├── 02_analysis.py     # statistik + grafik
│   └── 03_build_pbip.py   # membuat proyek Power BI
├── data/
│   ├── raw/               # CSV asli dari Zenodo + cuaca Open-Meteo
│   └── processed/         # CSV siap pakai (dipakai Power BI)
├── outputs/
│   ├── figures/           # 9 grafik PNG
│   └── findings.txt       # ringkasan angka hasil analisis
├── powerbi/JogjaPulse.pbip
├── README.md
└── requirements.txt
```

---

## 1. Menjalankan kode Python

Data sudah terunduh dan hasil olahan sudah ada. Langkah ini hanya perlu dilakukan kalau ingin mengulang dari awal atau di komputer lain.

### 1.1 Siapkan lingkungan

```bash
cd "Pak Widyawan"
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 1.2 Jalankan berurutan

```bash
python code/01_etl.py        # hasil: data/processed/*.csv
python code/02_analysis.py   # hasil: outputs/figures/*.png dan outputs/findings.txt
```

Catatan:
- `01_etl.py` mengunduh cuaca dari Open-Meteo (butuh internet) dan menyimpannya di `data/raw/weather_open_meteo.csv`.
- File CSV dari Zenodo harus ada di `data/raw/`. Kalau hilang, unduh dari https://zenodo.org/records/23157460 .

---

## 2. Membuka dashboard di Power BI

Power BI Desktop hanya ada untuk Windows. Kalau komputer Anda Linux, salin seluruh folder ke komputer Windows.

### 2.1 Salin folder ke Windows

Misalnya ke `C:\JogjaPulse\`, sehingga ada `C:\JogjaPulse\data\processed\` dan `C:\JogjaPulse\powerbi\`.

### 2.2 Buka proyek

1. Buka Power BI Desktop.
2. Kalau diminta, aktifkan fitur ini: **File → Options and settings → Options → Preview features → Power BI Project (.pbip) save option**. Lalu restart Power BI.
3. **File → Open report → Browse this device** lalu pilih `powerbi\JogjaPulse.pbip`.

### 2.3 Arahkan ke folder data

1. **Home → Transform data → Edit parameters**.
2. Isi `DataFolder` dengan path folder `data\processed`, misalnya `C:\JogjaPulse\data\processed`. Jangan pakai garis miring di akhir.
3. Klik **OK**, lalu **Close & Apply** dan tunggu data termuat.

Alternatif: buat ulang proyek langsung dengan path yang benar.
```bash
python code/03_build_pbip.py "C:\JogjaPulse\data\processed"
```

### 2.4 Simpan sebagai .pbix (untuk dikumpulkan)

**File → Save as** lalu pilih format `.pbix`.

### 2.5 Isi 5 halaman dashboard

| Halaman | Isi | Cara membaca |
|---|---|---|
| 1. Overview | Kartu KPI, indeks aktivitas harian, ritme per jam, per hari | Indeks 1,0 berarti normal |
| 2. Spatial Hotspots | Sebaran sel 500 m, tabel sel teramai dan sel pelonjakan akhir pekan | Ukuran titik menunjukkan tingkat kehadiran |
| 3. Sub-district Profiles | Rasio siang/malam per kapanewon, populasi vs perangkat | Rasio >1 berarti ramai di siang hari |
| 4. Origin-Destination | Matriks asal–tujuan, kapanewon penarik | Rasio tarik >1 berarti penarik pengunjung |
| 5. Weather & Holidays | Hujan vs aktivitas, hari libur | Sumber data kedua |

### 2.6 Kalau ada masalah

| Masalah | Solusi |
|---|---|
| Proyek tidak bisa dibuka | Aktifkan fitur preview PBIP (langkah 2.2), restart |
| Error "file not found" saat refresh | Periksa parameter `DataFolder` |
| Visual kosong | Klik **Refresh**, pastikan data termuat di panel Data |
| Proyek PBIP tetap gagal dibuka | Buat manual: **Get Data → Text/CSV** untuk 7 file CSV di `data/processed` (`dim_date`, `dim_kapanewon`, `dim_cell`, `fact_hourly`, `fact_daily`, `fact_cell_daily`, `fact_od`), lalu buat relasi di Model view dan ukuran DAX dari `03_build_pbip.py` |

Relasi tabel:
- `fact_hourly[kapanewon_code]` → `dim_kapanewon[kapanewon_code]`
- `fact_hourly[date]`, `fact_daily[date]`, `fact_cell_daily[date]` → `dim_date[date]`
- `fact_cell_daily[cell_id]` → `dim_cell[cell_id]`
- `fact_od[origin_code]` → `dim_kapanewon[kapanewon_code]` (aktif)
- `fact_od[dest_code]` → `dim_kapanewon[kapanewon_code]` (tidak aktif, dipakai ukuran `OD Inbound`)

---

## 3. Mengunggah kode ke GitHub

```bash
cd "Pak Widyawan"
git init
cat > .gitignore <<'EOF'
.venv/
__pycache__/
data/raw/*.csv
EOF
git add code README.md PANDUAN.md requirements.txt outputs powerbi data/processed
git commit -m "Human mobility project: JogjaPulse analysis and Power BI"
git branch -M main
git remote add origin https://github.com/<username>/<nama-repo>.git
git push -u origin main
```

Langkah awal: buat repo kosong di https://github.com/new, lalu ganti `<username>` dan `<nama-repo>`.

Catatan: `data/processed` berukuran sekitar 31 MB. File terbesar (`fact_hourly.csv`, 20 MB) masih di bawah batas 100 MB per file di GitHub. Data mentah tidak perlu diunggah karena bisa diunduh dari Zenodo.

Tambahkan nama dan NIM anggota kelompok (5–8 orang) di `README.md`.

---

## 4. Video presentasi (5 menit)

Kumpulkan ke https://elok.ugm.ac.id **sebelum minggu ke-13**.

### Kerangka waktu

| Menit | Isi |
|---|---|
| 0:00–0:30 | Judul, anggota kelompok, tujuan |
| 0:30–1:15 | Dua sumber data: JogjaPulse (Zenodo) dan Open-Meteo plus hari libur |
| 1:15–1:45 | Catatan data: sampel menyusut sekitar 9×, jadi memakai indeks ternormalisasi |
| 1:45–3:45 | Demo dashboard Power BI, halaman 1 sampai 5, sebutkan satu temuan per halaman |
| 3:45–4:30 | Kesimpulan dan keterbatasan |
| 4:30–5:00 | Penutup dan tautan GitHub |

### Poin temuan untuk disebut
- Aktivitas terendah sekitar jam 03.00 dan puncaknya sekitar jam 18.00.
- Hari kerja vs akhir pekan hanya berbeda sekitar 2% dan tidak signifikan.
- Hujan tidak berpengaruh signifikan terhadap aktivitas.
- Gondomanan unik: aktivitas malam tinggi karena banyak pengunjung dan wisatawan.
- Gondokusuman, Danurejan, Gedongtengen, dan Ngampilan adalah penarik pengunjung.

Alat rekam: OBS Studio atau Zoom (rekam layar).

---

## 5. Presentasi proyek (minggu 13–14)

Gunakan struktur yang sama dengan video, tapi lebih detail:
1. Latar belakang dan pertanyaan penelitian.
2. Data: sumber, ukuran, privasi (k-anonymity, k=5).
3. Metode: normalisasi, indeks aktivitas, k-means, OD.
4. Hasil: lima halaman dashboard dan grafik di `outputs/figures/`.
5. Keterbatasan: sampel berubah, data Mar–Apr kualitas rendah, perangkat ≠ orang.
6. Kesimpulan dan saran.

Siapkan jawaban untuk pertanyaan yang mungkin muncul:
- **Kenapa pakai indeks aktivitas?** Jumlah perangkat turun sekitar 9×, jadi angka mentah tidak bisa dibandingkan antar bulan.
- **Kenapa tidak ada pengaruh hujan?** Mungkin memang kecil, atau sampel terlalu kasar. Datanya harian dan hanya satu titik cuaca untuk seluruh DIY.
- **Apakah `n_maids` jumlah orang?** Bukan. Itu jumlah perangkat unik per periode dan tidak bisa dijumlahkan antar wilayah atau jam, jadi saya menyebutnya *device-hours*.

---

## 6. Daftar periksa pengumpulan

- [ ] Kode diunggah ke GitHub dan tautannya dibagikan
- [ ] File `.pbix` disimpan
- [ ] Nama anggota kelompok ada di `README.md`
- [ ] Video 5 menit diunggah ke elok.ugm.ac.id sebelum minggu 13
- [ ] Slide presentasi siap untuk minggu 13–14
