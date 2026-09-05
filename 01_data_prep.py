"""
01_data_prep.py
Menggabungkan data PIBAL dari 2 file (jam 06.00 UTC dan jam 18.00 UTC),
masing-masing berisi 12 sheet bulan, menjadi 1 dataset long/tidy.

Struktur asli per sheet bulan (konsisten di kedua file):
  - Baris 9 : label ketinggian ("SURFACE", "1 0 0 0", "2 0 0 0", ...)
  - Baris 10: label "ddd"/"ff" berpasangan per ketinggian
  - Baris 11 dst: data observasi.
      Kolom A,B = 2 digit tahun (kadang typo/tidak konsisten -> TIDAK dipakai,
                  tahun diambil dari nama file / hardcode 2025)
      Kolom C   = bulan (M) -- kadang cuma terisi di baris pertama -> forward-fill
      Kolom D,E = 2 digit tanggal
      Kolom F   = jam (H)
  - Baris "RATA-RATA" di akhir sheet -> di-skip
  - Baris berisi "R A I N" (huruf, bukan angka) -> di-skip

Jam observasi (06 atau 18 UTC) diambil dari file mana datanya berasal,
BUKAN dari kolom H per baris, karena header "JAM" di sheet tidak selalu
terisi (lebih robust pakai konfigurasi eksplisit di bawah).

Cara pakai:
    python 01_data_prep.py

Output:
    pibal_long_2025.csv  (kolom tambahan: jam_observasi -> "06 UTC" / "18 UTC")
"""

import openpyxl
import pandas as pd
import numpy as np
import re

# ------------------------------------------------------------------
# KONFIGURASI — daftar file yang mau digabung + label jam observasinya
# ------------------------------------------------------------------
FILES = [
    {"path": "/mnt/user-data/uploads/DATA_PIBAL_TAHUN_2025_06.xlsx", "jam": "06 UTC"},
    {"path": "/mnt/user-data/uploads/DATA_PIBAL_TAHUN_2025_18.xlsx", "jam": "18 UTC"},
]

MONTH_SHEETS = ["JAN", "FEB", "MAR", "APR", "MEI", "JUN",
                "JUL", "AGT", "SEP", "OKT", "NOV", "DES"]
MONTH_NUM = {m: i + 1 for i, m in enumerate(MONTH_SHEETS)}

TAHUN_DEFAULT = 2025  # dari nama file "DATA PIBAL TAHUN 2025..."


def find_header_rows(ws, search_limit=15):
    """Cari baris 'ddd/ff' secara dinamis (posisinya bisa geser antar sheet),
    lalu kembalikan (header_row_altitude, header_row_ddd_ff, data_start_row)."""
    for r in range(1, search_limit + 1):
        row_vals = [ws.cell(row=r, column=c).value for c in range(1, ws.max_column + 1)]
        if any(str(v).strip().lower() == "ddd" for v in row_vals if v is not None):
            return r - 1, r, r + 1
    # fallback ke posisi standar kalau tidak ketemu
    return 9, 10, 11


def clean_altitude_label(label):
    if label is None:
        return None
    s = str(label).strip()
    if s.upper() == "SURFACE":
        return "SURFACE"
    s = re.sub(r"\s+", "", s)
    return s


def parse_sheet(ws, sheet_name, jam_label):
    max_col = ws.max_column
    max_row = ws.max_row

    header_row_altitude, header_row_ddd_ff, data_start_row = find_header_rows(ws)

    altitude_row = [ws.cell(row=header_row_altitude, column=c).value for c in range(1, max_col + 1)]
    ddf_row = [ws.cell(row=header_row_ddd_ff, column=c).value for c in range(1, max_col + 1)]

    last_alt = None
    filled_altitude = []
    for v in altitude_row:
        if v is not None and str(v).strip() != "":
            last_alt = clean_altitude_label(v)
        filled_altitude.append(last_alt)

    ddd_ff_pairs = []
    for idx, label in enumerate(ddf_row):
        if label is not None and str(label).strip().lower() == "ddd":
            ddd_ff_pairs.append((idx, idx + 1, filled_altitude[idx]))

    month = MONTH_NUM[sheet_name]
    records = []
    for r in range(data_start_row, max_row + 1):
        col_d = ws.cell(row=r, column=4).value  # digit tanggal 1
        col_e = ws.cell(row=r, column=5).value  # digit tanggal 2

        if not isinstance(col_d, (int, float)) or not isinstance(col_e, (int, float)):
            continue  # baris kosong / "RATA-RATA" / bukan data

        try:
            day = int(f"{int(col_d)}{int(col_e)}")
            if day < 1 or day > 31:
                continue
        except Exception:
            continue

        for ddd_idx, ff_idx, ketinggian in ddd_ff_pairs:
            arah = ws.cell(row=r, column=ddd_idx + 1).value
            speed = ws.cell(row=r, column=ff_idx + 1).value

            if arah is None or speed is None:
                continue
            if not isinstance(arah, (int, float)) or not isinstance(speed, (int, float)):
                continue  # skip baris "R A I N" dsb

            records.append({
                "year": TAHUN_DEFAULT,
                "month": month,
                "day": day,
                "jam_observasi": jam_label,
                "sheet_bulan": sheet_name,
                "ketinggian": ketinggian,
                "arah_deg": float(arah),
                "kecepatan": float(speed),
            })

    return pd.DataFrame(records)


def main():
    all_data = []
    for f in FILES:
        wb = openpyxl.load_workbook(f["path"], data_only=True)
        for sheet_name in MONTH_SHEETS:
            if sheet_name not in wb.sheetnames:
                print(f"[SKIP] {f['path']} - sheet {sheet_name} tidak ditemukan")
                continue
            ws = wb[sheet_name]
            df_sheet = parse_sheet(ws, sheet_name, f["jam"])
            all_data.append(df_sheet)
            print(f"[OK] {f['jam']} / {sheet_name}: {len(df_sheet)} baris observasi")

    df = pd.concat(all_data, ignore_index=True)

    df = df[(df["arah_deg"] >= 0) & (df["arah_deg"] <= 360)]
    df = df[df["kecepatan"] >= 0]

    df.to_csv("pibal_long_2025.csv", index=False)
    print(f"\nTotal: {len(df)} baris -> pibal_long_2025.csv")
    print("\nJumlah observasi per jam:")
    print(df.groupby("jam_observasi").size())
    print("\nJumlah observasi per bulan x jam:")
    print(df.groupby(["sheet_bulan", "jam_observasi"]).size().unstack(fill_value=0))
    print("\nContoh data:")
    print(df.head(10))


if __name__ == "__main__":
    main()
