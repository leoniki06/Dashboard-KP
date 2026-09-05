# Panduan: Dashboard PIBAL 2025 dengan Streamlit + Wind Rose

## Alur kerja lengkap

### 1. Siapkan data mentah
- Download kedua file dari Google Sheets: data jam 06.00 UTC dan jam 18.00 UTC
- Taruh di folder yang sama dengan `01_data_prep.py`, path-nya sudah dikonfigurasi di
  bagian `FILES` di atas script — sesuaikan kalau nama/lokasi filenya beda.

### 2. Catatan kualitas data (sudah ditangani otomatis oleh parser)
- Kolom digit tahun per baris kadang typo (mis. "23" padahal seharusnya "25" -> 2025).
  Parser **tidak** memakai kolom ini; tahun diambil dari nama file (hardcode 2025).
- Posisi baris header ("ddd"/"ff") bisa geser 1 baris di sheet tertentu (mis. sheet DES
  di file jam 18). Parser mendeteksi baris header secara otomatis, bukan hardcode nomor baris.
- Kolom Year & Month kadang cuma terisi di baris pertama tiap sheet -> di-forward-fill.
- Baris "RATA-RATA" dan baris "R A I N" (data hilang) otomatis di-skip.

### 3. Jalankan data prep (opsional — sudah disediakan hasilnya)
`pibal_long_2025.csv` di paket ini **sudah jadi hasil gabungan** kedua file (jam 06 &
18 UTC), total **5.831 baris observasi**, Januari-Desember 2025, 17 level ketinggian
(SURFACE s.d. 16000). Kalau datanya update, tinggal jalankan ulang:
```bash
python 01_data_prep.py
```

### 4. Install dependency
```bash
pip install -r requirements.txt
```

### 5. Jalankan dashboard
```bash
streamlit run app.py
```
Browser otomatis terbuka di `localhost:8501`.

### 6. Yang sudah ada di dashboard ini
Desain memakai identitas visual "lapisan atmosfer" — gradasi warna dari hangat
(permukaan) ke biru (atmosfer atas) dipakai konsisten di hero banner dan skala
wind rose. Tema terang (`plotly_white`) dengan teks gelap eksplisit supaya semua
label/angka kebaca jelas.

**Filter (sidebar)**: bulan, **jam observasi (06 UTC / 18 UTC / keduanya)**, ketinggian

**Tab 1 — Dashboard Utama**
- KPI cards custom: jumlah observasi, kecepatan rata-rata/maks, arah dominan, % angin tenang
- Wind rose diagram (16 arah mata angin x bin kecepatan, interaktif)
- Histogram distribusi kecepatan
- Tren bulanan kecepatan rata-rata
- Perbandingan antar ketinggian (surface s.d. 16000)

**Tab 2 — Wind Rose per Musim**
- 4 wind rose berdampingan untuk DJF (Des-Jan-Feb, muson barat), MAM (peralihan), JJA (Jun-Jul-Agt, muson timur), SON (peralihan)
- Tiap wind rose dilengkapi narasi singkat arah dominan & kecepatan rata-rata
- Berguna untuk analisis pola angin muson di laporan KP

**Tab 3 — Perbandingan Ketinggian (Small Multiples)**
- Grid wind rose (frekuensi arah, %) untuk beberapa ketinggian sekaligus dalam satu tampilan
- Bisa pilih ketinggian mana saja yang mau dibandingkan (disarankan maks 6-8 biar tetap terbaca)
- Membantu melihat pergeseran arah angin dominan seiring bertambahnya ketinggian

**Tab 4 — Ringkasan Naratif**
- Narasi otomatis yang digenerate dari data, contoh: "Bulan Juni didominasi angin dari arah Tenggara (SE) — muncul pada 42% observasi — dengan kecepatan rata-rata 8.2 knot. Persentase angin tenang (≤2 knot): 5%."
- Tersedia untuk keseluruhan periode terpilih, per bulan, dan per musim
- Bisa langsung disalin & disunting sebagai draf pembahasan di laporan KP
- Ambang "angin tenang" (calm) default di ≤2 knot — bisa diubah lewat variabel `CALM_THRESHOLD` di `app.py` sesuai definisi yang dipakai BMKG/instansi kamu

### 7. Pengembangan lanjutan lain (opsional, kalau mau eksplorasi lebih jauh)
- Uji statistik perbedaan pola angin antar musim (mis. Watson-Williams test untuk data sirkular)
- Overlay wind rose dengan data curah hujan/kondisi cuaca (kalau ada) untuk analisis korelasi
- Ekspor tiap wind rose sebagai gambar (Plotly punya tombol kamera bawaan di pojok kanan atas chart) untuk ditempel di laporan
- Tambah opsi ganti satuan kecepatan (knot ↔ m/s ↔ km/h) di sidebar

### 8. Deploy (kalau dosen/pembimbing mau lihat online)
- Push folder ini ke GitHub (public/private repo)
- Daftar di https://share.streamlit.io , connect ke repo, deploy gratis
