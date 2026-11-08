# Human Mobility di D.I. Yogyakarta (Des 2021 – Apr 2022)

Analisis pola mobilitas manusia di Daerah Istimewa Yogyakarta memakai data kehadiran perangkat seluler yang sudah dianonimkan (k = 5).

**Anggota kelompok:** _(isi nama dan NIM)_

## Sumber Data

| # | Sumber | Isi |
|---|---|---|
| 1 | [JogjaPulse, Zenodo](https://zenodo.org/records/23157460) (CC BY 4.0) | Kehadiran per sel 500 m per hari, per kapanewon per jam, arus asal–tujuan (OD), populasi BPS |
| 2 | [Open-Meteo Archive API](https://open-meteo.com/) + hari libur nasional | Curah hujan, suhu harian, dan hari libur/cuti bersama |

## Hasil Analisis

| Pertanyaan | Temuan |
|---|---|
| Bagaimana ritme harian? | Aktivitas terendah sekitar **03.00 WIB** dan puncaknya sekitar **18.00 WIB**. |
| Apakah akhir pekan/libur berbeda? | Selisih hanya sekitar **2%** dan **tidak signifikan** (p = 0,44). |
| Apakah hujan memengaruhi mobilitas? | **Tidak** ada hubungan berarti (rho ≈ 0,04; p = 0,65). |
| Kawasan mana yang teramai? | Sel di sekitar pusat Kota Yogyakarta (area Malioboro) paling padat, disusul sebuah sel di Gunungkidul. |
| Bagaimana karakter tiap kapanewon? | **Gondomanan** menonjol dengan aktivitas malam tinggi (rasio siang/malam 0,66), kemungkinan karena wisatawan dan hotel. Mayoritas kapanewon lain aktif di siang hari. |
| Ke mana warga bepergian? | **Gondokusuman, Danurejan, Gedongtengen, Ngampilan** adalah penarik pengunjung, dengan jumlah pengunjung masuk 2–5 kali lipat yang keluar. |
| Seberapa representatif datanya? | Jumlah perangkat berkorelasi dengan penduduk (r log-log = 0,69), dengan penetrasi median sekitar **9%**. |

**Kesimpulan:** mobilitas di DIY sangat mengikuti ritme harian dan terpusat di inti kota. Hari dalam seminggu dan hujan tidak banyak mengubahnya.

## Keterbatasan

- Jumlah perangkat terpantau turun sekitar **9 kali** dari Desember ke April, sehingga angka mentah tidak bisa dibandingkan. Analisis memakai proporsi dan *indeks aktivitas* (nilai harian dibagi median bergulir 15 hari).
- `n_maids` adalah jumlah perangkat unik dan tidak bisa dijumlahkan, jadi hasil penjumlahan disebut *device-hours*, bukan jumlah orang.
- Baris yang hilang berarti kurang dari 5 perangkat, bukan nol. Delapan kapanewon di Gunungkidul dan sekitarnya terlalu sedikit data untuk diklasifikasi.
- Data OD Maret–April berkualitas rendah dan tidak dipakai.
- Hujan memakai satu titik cuaca untuk seluruh DIY.

## Struktur Folder

```
code/
  01_etl.py          ambil, bersihkan, dan gabung 2 sumber data
  02_analysis.py     statistik dan grafik
  03_build_pbip.py   membuat proyek Power BI
data/raw/            data asli
data/processed/      CSV hasil olahan
outputs/figures/     9 grafik PNG
outputs/findings.txt ringkasan angka
powerbi/             JogjaPulse.pbip (5 halaman dashboard)
PANDUAN.md           langkah menjalankan dan mengumpulkan
```

## Cara Menjalankan

```bash
pip install -r requirements.txt
python code/01_etl.py
python code/02_analysis.py
```

Untuk dashboard, buka `powerbi/JogjaPulse.pbip` di Power BI Desktop lalu atur parameter `DataFolder` ke folder `data/processed`. Langkah lengkap ada di [PANDUAN.md](PANDUAN.md).
