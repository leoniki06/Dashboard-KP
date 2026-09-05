"""
Dashboard Angin PIBAL 2025
Stasiun Meteorologi Klas I Juanda, Sidoarjo

Jalankan:
    streamlit run app.py

Butuh file:
    pibal_long_2025.csv
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# ============================================================
# PAGE
# ============================================================
st.set_page_config(
    page_title="Dashboard PIBAL 2025 — Juanda",
    page_icon="🌬️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# DESIGN SYSTEM
# ============================================================
C_NAVY = "#0B3D5C"
C_BLUE = "#2E86AB"
C_TEAL = "#00A5A0"
C_BG = "#F4F7FA"
C_WHITE = "#FFFFFF"
C_TEXT = "#183B56"
C_MUTED = "#607789"
C_BORDER = "#DCE6EC"
C_SOFT_BLUE = "#EAF4FB"

# Warna ini dipakai KONSISTEN di semua Wind Rose.
# 0–5, 5–10, 10–15, 15–20, 20–25, >25 knot
WIND_SCALE = [
    "#2166AC",
    "#4DAF4A",
    "#FFD400",
    "#FF8C00",
    "#E53935",
    "#8B0000",
]

BULAN_URUT = [
    "JAN", "FEB", "MAR", "APR", "MEI", "JUN",
    "JUL", "AGT", "SEP", "OKT", "NOV", "DES"
]

SECTOR_ORDER = [
    "N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
    "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"
]

SECTOR_ID_NAME = {
    "N": "Utara",
    "NNE": "Utara-Timur Laut",
    "NE": "Timur Laut",
    "ENE": "Timur-Timur Laut",
    "E": "Timur",
    "ESE": "Timur-Tenggara",
    "SE": "Tenggara",
    "SSE": "Selatan-Tenggara",
    "S": "Selatan",
    "SSW": "Selatan-Barat Daya",
    "SW": "Barat Daya",
    "WSW": "Barat-Barat Daya",
    "W": "Barat",
    "WNW": "Barat-Barat Laut",
    "NW": "Barat Laut",
    "NNW": "Utara-Barat Laut",
}

SEASON_MAP = {
    "DES": "DJF", "JAN": "DJF", "FEB": "DJF",
    "MAR": "MAM", "APR": "MAM", "MEI": "MAM",
    "JUN": "JJA", "JUL": "JJA", "AGT": "JJA",
    "SEP": "SON", "OKT": "SON", "NOV": "SON",
}

SEASON_ORDER = ["DJF", "MAM", "JJA", "SON"]

SEASON_LABEL = {
    "DJF": "DJF · Des/Jan/Feb · Muson Barat",
    "MAM": "MAM · Mar/Apr/Mei · Peralihan I",
    "JJA": "JJA · Jun/Jul/Agt · Muson Timur",
    "SON": "SON · Sep/Okt/Nov · Peralihan II",
}

SPEED_BINS = [0, 5, 10, 15, 20, 25, np.inf]
SPEED_LABELS = ["0–5", "5–10", "10–15", "15–20", "20–25", ">25"]
CALM_THRESHOLD = 2.0


# ============================================================
# CSS
# ============================================================
st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

    :root {{
        --navy: {C_NAVY};
        --blue: {C_BLUE};
        --teal: {C_TEAL};
        --bg: {C_BG};
        --white: {C_WHITE};
        --text: {C_TEXT};
        --muted: {C_MUTED};
        --border: {C_BORDER};
    }}

    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
    }}

    .stApp {{
        background: var(--bg);
    }}

    .block-container {{
        padding-top: 1.8rem;
        padding-bottom: 3rem;
        max-width: 1500px;
    }}

    h1, h2, h3, h4 {{
        font-family: 'Space Grotesk', sans-serif !important;
        color: var(--navy) !important;
    }}

    /* ---------- HERO ---------- */
    .hero {{
        position: relative;
        overflow: hidden;
        background: linear-gradient(135deg, #0B3D5C 0%, #145A7D 100%);
        border-radius: 18px;
        padding: 28px 32px;
        margin-bottom: 18px;
        box-shadow: 0 8px 24px rgba(11,61,92,.14);
    }}

    .hero::after {{
        content: "〰 〰 〰";
        position: absolute;
        right: 28px;
        bottom: 5px;
        color: rgba(255,255,255,.12);
        font-size: 58px;
        letter-spacing: 8px;
        transform: rotate(-8deg);
    }}

    .hero-kicker {{
        color: #9FE5E0;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: .12em;
        text-transform: uppercase;
        margin-bottom: 7px;
    }}

    .hero-title {{
        color: white !important;
        font-family: 'Space Grotesk', sans-serif;
        font-size: 32px;
        font-weight: 700;
        line-height: 1.15;
        margin: 0;
    }}

    .hero-sub {{
        color: rgba(255,255,255,.82);
        font-size: 13px;
        margin-top: 9px;
        max-width: 900px;
    }}

    /* ---------- KPI ---------- */
    .kpi {{
        background: white;
        border: 1px solid var(--border);
        border-radius: 15px;
        padding: 16px 17px;
        min-height: 104px;
        box-shadow: 0 3px 12px rgba(20,60,80,.06);
        position: relative;
        overflow: hidden;
    }}

    .kpi::before {{
        content: "";
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 4px;
        background: var(--blue);
    }}

    .kpi-icon {{
        font-size: 19px;
        margin-bottom: 5px;
    }}

    .kpi-label {{
        color: var(--muted);
        font-size: 10px;
        font-weight: 700;
        letter-spacing: .08em;
        text-transform: uppercase;
    }}

    .kpi-value {{
        color: var(--navy);
        font-family: 'Space Grotesk', sans-serif;
        font-size: 24px;
        font-weight: 700;
        margin-top: 2px;
    }}

    /* ---------- SECTION ---------- */
    .section-title {{
        font-family: 'Space Grotesk', sans-serif;
        color: var(--navy);
        font-size: 21px;
        font-weight: 700;
        margin: 7px 0 3px;
    }}

    .section-sub {{
        color: var(--muted);
        font-size: 12px;
        margin-bottom: 8px;
    }}

    .info {{
        background: var(--white);
        border: 1px solid var(--border);
        border-left: 4px solid var(--blue);
        border-radius: 12px;
        padding: 12px 15px;
        color: var(--text);
        font-size: 12.5px;
        line-height: 1.55;
        margin: 6px 0 14px;
    }}

    .insight {{
        background: #FFFFFF;
        border: 1px solid var(--border);
        border-left: 4px solid var(--teal);
        border-radius: 10px;
        padding: 10px 13px;
        color: var(--text);
        font-size: 12px;
        line-height: 1.5;
        margin-top: 3px;
    }}

    .mini-label {{
        color: var(--muted);
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: .07em;
        margin: 4px 0 5px;
    }}

    .legend-note {{
        background: #F8FBFD;
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 9px 12px;
        color: var(--muted);
        font-size: 11px;
        margin: 5px 0 10px;
    }}

    /* ---------- SIDEBAR ---------- */
    section[data-testid="stSidebar"] {{
        background: #EDF4F8;
        border-right: 1px solid var(--border);
    }}

    section[data-testid="stSidebar"] h2 {{
        font-size: 20px !important;
    }}

    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {{
        color: var(--text) !important;
    }}

    /* ---------- TABS ---------- */
    button[data-baseweb="tab"] {{
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        color: var(--muted);
        padding: 10px 15px;
    }}

    button[data-baseweb="tab"][aria-selected="true"] {{
        color: var(--navy);
    }}

    /* ---------- STREAMLIT TEXT CONTRAST ---------- */
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] li,
    [data-testid="stExpander"] p,
    [data-testid="stExpander"] summary {{
        color: var(--text);
    }}

    [data-testid="stCaptionContainer"] {{
        color: var(--muted) !important;
        opacity: 1 !important;
    }}

    hr {{
        border-color: var(--border) !important;
        margin: 12px 0 !important;
    }}

    /* Select / multiselect */
    div[data-baseweb="select"] > div {{
        border-radius: 9px;
        border-color: #CBD9E2;
    }}

    /* Remove excessive top whitespace in tabs */
    .stTabs [data-baseweb="tab-panel"] {{
        padding-top: 1rem;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# DATA
# ============================================================
@st.cache_data
def load_data():
    df = pd.read_csv("pibal_long_2025.csv")

    raw_altitudes = df["ketinggian"].astype(str).unique().tolist()
    numeric_altitudes = sorted(
        [x for x in raw_altitudes if x != "SURFACE"],
        key=lambda x: int(x)
    )

    df["ketinggian"] = pd.Categorical(
        df["ketinggian"].astype(str),
        categories=["SURFACE"] + numeric_altitudes,
        ordered=True,
    )

    df["sheet_bulan"] = pd.Categorical(
        df["sheet_bulan"],
        categories=BULAN_URUT,
        ordered=True,
    )

    df["musim"] = df["sheet_bulan"].map(SEASON_MAP)

    df["sector"] = df["arah_deg"].apply(
        lambda d: SECTOR_ORDER[int(((d + 11.25) % 360) // 22.5)]
    )

    df["speed_bin"] = pd.cut(
        df["kecepatan"],
        bins=SPEED_BINS,
        labels=SPEED_LABELS,
        right=False,
    )

    if "jam_observasi" not in df.columns:
        df["jam_observasi"] = "06 UTC"

    return df


df = load_data()


# ============================================================
# HELPERS
# ============================================================
def apply_plot_theme(fig, height=430, show_legend=True):
    """Tema Plotly yang konsisten dan kontras."""
    existing_title = ""
    try:
        if fig.layout.title and fig.layout.title.text:
            existing_title = fig.layout.title.text
    except Exception:
        pass
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(
            family="Inter, sans-serif",
            size=12,
            color=C_TEXT,
        ),
        title=dict(
            text=existing_title,
            font=dict(
                family="Space Grotesk, sans-serif",
                size=16,
                color=C_NAVY,
            ),
            x=0,
            xanchor="left",
        ),
        legend=dict(
            font=dict(size=11, color=C_TEXT),
            bgcolor="rgba(255,255,255,0.85)",
            bordercolor=C_BORDER,
            borderwidth=1,
        ),
        showlegend=show_legend,
        height=height,
        margin=dict(t=55, b=45, l=55, r=20),
        hoverlabel=dict(
            bgcolor="white",
            font=dict(color=C_TEXT),
            bordercolor=C_BORDER,
        ),
    )
    return fig


def windrose_pivot_pct(data):
    if data.empty:
        return pd.DataFrame(
            0.0,
            index=SECTOR_ORDER,
            columns=SPEED_LABELS,
        )

    pivot = (
        data.groupby(["sector", "speed_bin"], observed=False)
        .size()
        .unstack(fill_value=0)
    )

    pivot = pivot.reindex(
        index=SECTOR_ORDER,
        columns=SPEED_LABELS,
        fill_value=0,
    ).fillna(0)

    total = pivot.values.sum()

    if total == 0:
        return pivot.astype(float)

    return pivot / total * 100


def make_windrose(data, title="", height=510):
    """Wind Rose utama: arah + distribusi kecepatan dengan warna konsisten."""
    pivot_pct = windrose_pivot_pct(data)

    fig = go.Figure()

    for i, speed in enumerate(SPEED_LABELS):
        fig.add_trace(
            go.Barpolar(
                r=pivot_pct[speed].values,
                theta=SECTOR_ORDER,
                name=f"{speed} kt",
                marker_color=WIND_SCALE[i],
                marker_line_color="white",
                marker_line_width=0.55,
                hovertemplate=(
                    "<b>%{theta}</b><br>"
                    f"Kecepatan: {speed} kt<br>"
                    "Frekuensi: %{r:.1f}%<extra></extra>"
                ),
            )
        )

    fig.update_layout(
        title=title,
        barmode="stack",
        polar=dict(
            bgcolor="white",
            radialaxis=dict(
                ticksuffix="%",
                color=C_TEXT,
                gridcolor=C_BORDER,
                linecolor=C_BORDER,
                tickfont=dict(size=10, color=C_TEXT),
            ),
            angularaxis=dict(
                direction="clockwise",
                rotation=90,
                color=C_TEXT,
                gridcolor=C_BORDER,
                linecolor=C_BORDER,
                tickfont=dict(size=10, color=C_TEXT),
            ),
        ),
        legend_title=dict(text="Kecepatan"),
    )

    return apply_plot_theme(fig, height=height)


def calm_percentage(data, threshold=CALM_THRESHOLD):
    if data.empty:
        return np.nan
    return (data["kecepatan"] <= threshold).mean() * 100


def dominant_stats(data):
    if data.empty:
        return None

    sector = data["sector"].mode().iloc[0]
    return {
        "sector": sector,
        "name": SECTOR_ID_NAME[sector],
        "pct": (data["sector"] == sector).mean() * 100,
        "avg": data["kecepatan"].mean(),
        "max": data["kecepatan"].max(),
        "calm": calm_percentage(data),
    }


def narasi_arah_dominan(data, label):
    stats = dominant_stats(data)

    if stats is None:
        return f"<b>{label}</b>: tidak ada data observasi."

    return (
        f"<b>{label}</b> · arah dominan "
        f"<b>{stats['name']} ({stats['sector']})</b> "
        f"sebesar {stats['pct']:.0f}% observasi · "
        f"rata-rata <b>{stats['avg']:.1f} kt</b> · "
        f"angin tenang ≤{CALM_THRESHOLD:.0f} kt: "
        f"<b>{stats['calm']:.0f}%</b>."
    )


def kpi_card(col, icon, label, value):
    col.markdown(
        f"""
        <div class="kpi">
            <div class="kpi-icon">{icon}</div>
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def info_box(text):
    st.markdown(f'<div class="info">{text}</div>', unsafe_allow_html=True)


def insight_box(text):
    st.markdown(
        f'<div class="insight">{text}</div>',
        unsafe_allow_html=True,
    )


def section_title(title, subtitle=None):
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(
            f'<div class="section-sub">{subtitle}</div>',
            unsafe_allow_html=True,
        )


def filtered_data():
    return df[
        (df["sheet_bulan"].isin(bulan_pilih))
        & (df["jam_observasi"].isin(jam_pilih))
        & (df["ketinggian"] == ketinggian_pilih)
    ]


CARA_BACA_WINDROSE = """
<b>📖 Cara membaca Wind Rose</b><br>
Kelopak menunjukkan <b>arah asal angin</b>, sedangkan panjang kelopak menunjukkan
frekuensi kejadian (%). Warna menunjukkan <b>rentang kecepatan angin</b>:
biru → hijau → kuning → oranye → merah. Jadi, semakin keluar kelopak,
semakin sering arah tersebut terjadi.
"""


# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("## 🔎 Filter Data")
    st.caption("Gunakan filter untuk mengubah seluruh visualisasi dashboard.")

    st.markdown("**Periode**")
    bulan_pilih = st.multiselect(
        "Bulan",
        options=BULAN_URUT,
        default=BULAN_URUT,
        label_visibility="collapsed",
    )

    jam_list = sorted(df["jam_observasi"].astype(str).unique().tolist())

    st.markdown("**Waktu observasi**")
    jam_pilih = st.multiselect(
        "Jam Observasi",
        options=jam_list,
        default=jam_list,
        label_visibility="collapsed",
    )

    ketinggian_list = [
        str(k)
        for k in df["ketinggian"].cat.categories
        if str(k) in df["ketinggian"].astype(str).unique()
    ]

    st.markdown("**Ketinggian utama**")
    ketinggian_pilih = st.selectbox(
        "Ketinggian",
        options=ketinggian_list,
        label_visibility="collapsed",
    )

    st.divider()

    st.markdown(
        """
        <div class="legend-note">
        <b>Dataset</b><br>
        PIBAL Stasiun Meteorologi Klas I Juanda, Sidoarjo · 2025<br><br>
        <b>Observasi</b><br>
        06.00 & 18.00 UTC · permukaan hingga lapisan atas atmosfer<br><br>
        <b>Calm</b><br>
        Kecepatan ≤ 2 knot
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# FILTERED DATA
# ============================================================
df_filtered = filtered_data()


# ============================================================
# HERO
# ============================================================
st.markdown(
    """
    <div class="hero">
        <div class="hero-kicker">ANALISIS ANGIN ATAS · PIBAL 2025</div>
        <div class="hero-title">🌬️ Dashboard Angin PIBAL — Juanda</div>
        <div class="hero-sub">
            Stasiun Meteorologi Klas I Juanda, Sidoarjo
            &nbsp;•&nbsp; Observasi Pilot Balon
            &nbsp;•&nbsp; 06.00 & 18.00 UTC
            &nbsp;•&nbsp; Permukaan s.d. 16.000 m
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# KPI
# ============================================================
stats = dominant_stats(df_filtered)

k1, k2, k3, k4, k5 = st.columns(5)

kpi_card(k1, "📊", "Jumlah Observasi", f"{len(df_filtered):,}")
kpi_card(
    k2,
    "💨",
    "Kecepatan Rata-rata",
    f"{df_filtered['kecepatan'].mean():.1f} kt" if not df_filtered.empty else "—",
)
kpi_card(
    k3,
    "⚡",
    "Kecepatan Maksimum",
    f"{df_filtered['kecepatan'].max():.1f} kt" if not df_filtered.empty else "—",
)
kpi_card(
    k4,
    "🧭",
    "Arah Dominan",
    f"{stats['sector']} · {stats['name']}" if stats else "—",
)
kpi_card(
    k5,
    "🌤️",
    f"Angin Tenang ≤ {CALM_THRESHOLD:.0f} kt",
    f"{stats['calm']:.0f}%" if stats else "—",
)

st.write("")


# ============================================================
# TABS
# ============================================================
tab1, tab2, tab3, tab4 = st.tabs(
    [
        "📊  Dashboard Utama",
        "🍂  Pola Musiman",
        "🗼  Profil Ketinggian",
        "📝  Ringkasan",
    ]
)


# ============================================================
# TAB 1 — DASHBOARD UTAMA
# ============================================================
with tab1:
    section_title(
        "Gambaran Pola Angin",
        f"Analisis untuk ketinggian {ketinggian_pilih} berdasarkan periode dan jam yang dipilih.",
    )

    info_box(CARA_BACA_WINDROSE)

    if df_filtered.empty:
        st.warning("Tidak ada data untuk kombinasi filter yang dipilih.")
    else:
        c1, c2 = st.columns([1.55, 1])

        with c1:
            st.plotly_chart(
                make_windrose(
                    df_filtered,
                    f"Wind Rose · {ketinggian_pilih}",
                    height=500,
                ),
                use_container_width=True,
                config={"displayModeBar": False},
            )
            insight_box(
                narasi_arah_dominan(
                    df_filtered,
                    f"Ketinggian {ketinggian_pilih}",
                )
            )

        with c2:
            section_title(
                "Distribusi Kecepatan",
                "Sebaran nilai kecepatan angin pada filter aktif.",
            )

            fig_hist = px.histogram(
                df_filtered,
                x="kecepatan",
                nbins=18,
                labels={
                    "kecepatan": "Kecepatan (knot)",
                    "count": "Jumlah observasi",
                },
            )

            fig_hist.update_traces(
                marker_color=C_BLUE,
                marker_line_color="white",
                marker_line_width=0.6,
            )

            fig_hist.update_xaxes(
                title_font=dict(color=C_TEXT),
                tickfont=dict(color=C_MUTED),
                gridcolor=C_BORDER,
                zeroline=False,
            )
            fig_hist.update_yaxes(
                title_font=dict(color=C_TEXT),
                tickfont=dict(color=C_MUTED),
                gridcolor=C_BORDER,
                zeroline=False,
            )

            st.plotly_chart(
                apply_plot_theme(fig_hist, height=390, show_legend=False),
                use_container_width=True,
                config={"displayModeBar": False},
            )

            insight_box(
                "💡 Batang yang lebih tinggi menunjukkan rentang kecepatan "
                "yang lebih sering diamati."
            )

        st.divider()

        cc1, cc2 = st.columns(2)

        with cc1:
            section_title(
                "Tren Kecepatan Rata-rata",
                "Perubahan rata-rata kecepatan angin sepanjang bulan yang dipilih.",
            )

            trend = (
                df_filtered.groupby(
                    "sheet_bulan",
                    observed=True
                )["kecepatan"]
                .mean()
                .reindex(BULAN_URUT)
                .dropna()
                .reset_index()
            )

            fig_trend = px.line(
                trend,
                x="sheet_bulan",
                y="kecepatan",
                markers=True,
                labels={
                    "sheet_bulan": "Bulan",
                    "kecepatan": "Kecepatan rata-rata (knot)",
                },
            )

            fig_trend.update_traces(
                line=dict(color=C_NAVY, width=3),
                marker=dict(color=C_BLUE, size=8),
            )

            fig_trend.update_xaxes(
                title_font=dict(color=C_TEXT),
                tickfont=dict(color=C_MUTED),
                gridcolor=C_BORDER,
                zeroline=False,
            )
            fig_trend.update_yaxes(
                title_font=dict(color=C_TEXT),
                tickfont=dict(color=C_MUTED),
                gridcolor=C_BORDER,
                zeroline=False,
            )

            st.plotly_chart(
                apply_plot_theme(fig_trend, height=360, show_legend=False),
                use_container_width=True,
                config={"displayModeBar": False},
            )

            if not trend.empty:
                hi = trend.loc[trend["kecepatan"].idxmax(), "sheet_bulan"]
                lo = trend.loc[trend["kecepatan"].idxmin(), "sheet_bulan"]
                insight_box(
                    f"📈 Rata-rata tertinggi terjadi pada <b>{hi}</b>, "
                    f"sedangkan terendah pada <b>{lo}</b>."
                )

        with cc2:
            section_title(
                "Kecepatan Antar Ketinggian",
                "Rata-rata kecepatan pada setiap lapisan ketinggian.",
            )

            df_all_alt = df[
                (df["sheet_bulan"].isin(bulan_pilih))
                & (df["jam_observasi"].isin(jam_pilih))
            ]

            avg_by_alt = (
                df_all_alt.groupby(
                    "ketinggian",
                    observed=True
                )["kecepatan"]
                .mean()
                .reset_index()
            )

            avg_by_alt["ketinggian"] = avg_by_alt["ketinggian"].astype(str)

            fig_alt = px.bar(
                avg_by_alt,
                x="ketinggian",
                y="kecepatan",
                labels={
                    "ketinggian": "Ketinggian",
                    "kecepatan": "Kecepatan rata-rata (knot)",
                },
            )

            fig_alt.update_traces(
                marker_color=C_BLUE,
                marker_line_color="white",
                marker_line_width=0.5,
            )

            fig_alt.update_xaxes(
                title_font=dict(color=C_TEXT),
                tickfont=dict(color=C_MUTED),
                gridcolor=C_BORDER,
                zeroline=False,
            )
            fig_alt.update_yaxes(
                title_font=dict(color=C_TEXT),
                tickfont=dict(color=C_MUTED),
                gridcolor=C_BORDER,
                zeroline=False,
            )

            st.plotly_chart(
                apply_plot_theme(fig_alt, height=360, show_legend=False),
                use_container_width=True,
                config={"displayModeBar": False},
            )

            insight_box(
                "🗼 Grafik ini membantu melihat perubahan kecepatan rata-rata "
                "dari permukaan menuju lapisan atmosfer yang lebih tinggi."
            )

        with st.expander("Lihat data mentah yang sudah difilter"):
            st.dataframe(
                df_filtered,
                use_container_width=True,
                hide_index=True,
            )


# ============================================================
# TAB 2 — MUSIM
# ============================================================
with tab2:
    section_title(
        "Pola Angin Berdasarkan Musim",
        f"Ketinggian {ketinggian_pilih} · warna kecepatan konsisten dengan Dashboard Utama.",
    )

    info_box(
        "🍂 Pembagian musim menggunakan DJF, MAM, JJA, dan SON. "
        "DJF dan JJA merepresentasikan periode muson, sedangkan MAM dan SON "
        "merupakan periode peralihan."
    )

    df_season_base = df[
        (df["ketinggian"] == ketinggian_pilih)
        & (df["jam_observasi"].isin(jam_pilih))
        & (df["sheet_bulan"].isin(bulan_pilih))
    ]

    r1c1, r1c2 = st.columns(2)
    r2c1, r2c2 = st.columns(2)

    season_slots = {
        "DJF": r1c1,
        "MAM": r1c2,
        "JJA": r2c1,
        "SON": r2c2,
    }

    for season in SEASON_ORDER:
        d_season = df_season_base[df_season_base["musim"] == season]

        with season_slots[season]:
            st.plotly_chart(
                make_windrose(
                    d_season,
                    SEASON_LABEL[season],
                    height=440,
                ),
                use_container_width=True,
                config={"displayModeBar": False},
            )
            insight_box(
                narasi_arah_dominan(
                    d_season,
                    season,
                )
            )


# ============================================================
# TAB 3 — KETINGGIAN
# ============================================================
with tab3:
    section_title(
        "Profil Angin Antar Ketinggian",
        "Bandingkan arah dan distribusi kecepatan angin pada beberapa lapisan atmosfer.",
    )

    info_box(
        "🗼 Setiap diagram menggunakan skala warna yang sama: "
        "<b>biru = kecepatan rendah</b> hingga <b>merah = kecepatan tinggi</b>. "
        "Dengan begitu, pola antar ketinggian dapat dibandingkan secara langsung."
    )

    default_alt = [
        a for a in ["SURFACE", "1000", "3000", "5000", "7000", "9000"]
        if a in ketinggian_list
    ]

    alt_pilih_multi = st.multiselect(
        "Ketinggian yang dibandingkan",
        options=ketinggian_list,
        default=default_alt or ketinggian_list[:6],
        help="Disarankan 6–8 ketinggian agar grid tetap nyaman dibaca.",
    )

    df_multi_base = df[
        (df["sheet_bulan"].isin(bulan_pilih))
        & (df["jam_observasi"].isin(jam_pilih))
    ]

    if not alt_pilih_multi:
        st.info("Pilih minimal satu ketinggian.")
    else:
        ncols = 3
        nrows = int(np.ceil(len(alt_pilih_multi) / ncols))

        specs = [
            [{"type": "polar"} for _ in range(ncols)]
            for _ in range(nrows)
        ]

        fig_multi = make_subplots(
            rows=nrows,
            cols=ncols,
            specs=specs,
            subplot_titles=[
                f"Ketinggian {a}" for a in alt_pilih_multi
            ],
            horizontal_spacing=0.055,
            vertical_spacing=0.10,
        )

        for i, alt in enumerate(alt_pilih_multi):
            r, c = divmod(i, ncols)

            d_alt = df_multi_base[
                df_multi_base["ketinggian"].astype(str) == str(alt)
            ]

            pivot = windrose_pivot_pct(d_alt)

            # PENTING:
            # Tab ini sekarang memakai distribusi speed_bin yang SAMA
            # dengan Wind Rose utama dan Tab Musiman.
            for speed_idx, speed in enumerate(SPEED_LABELS):
                fig_multi.add_trace(
                    go.Barpolar(
                        r=pivot[speed].values,
                        theta=SECTOR_ORDER,
                        name=f"{speed} kt",
                        marker_color=WIND_SCALE[speed_idx],
                        marker_line_color="white",
                        marker_line_width=0.4,
                        showlegend=(i == 0),
                        hovertemplate=(
                            f"<b>Ketinggian {alt}</b><br>"
                            "<b>%{theta}</b><br>"
                            f"Kecepatan: {speed} kt<br>"
                            "Frekuensi: %{r:.1f}%<extra></extra>"
                        ),
                    ),
                    row=r + 1,
                    col=c + 1,
                )

        fig_multi.update_polars(
            bgcolor="white",
            radialaxis=dict(
                ticksuffix="%",
                color=C_TEXT,
                gridcolor=C_BORDER,
                linecolor=C_BORDER,
                tickfont=dict(size=8, color=C_MUTED),
            ),
            angularaxis=dict(
                direction="clockwise",
                rotation=90,
                color=C_TEXT,
                gridcolor=C_BORDER,
                linecolor=C_BORDER,
                tickfont=dict(size=8, color=C_MUTED),
            ),
        )

        fig_multi.update_annotations(
            font=dict(
                color=C_NAVY,
                size=13,
                family="Space Grotesk, sans-serif",
            )
        )

        fig_multi.update_layout(
            barmode="stack",
            template="plotly_white",
            paper_bgcolor="white",
            plot_bgcolor="white",
            font=dict(
                family="Inter, sans-serif",
                color=C_TEXT,
                size=11,
            ),
            legend=dict(
                title="Kecepatan (kt)",
                orientation="h",
                yanchor="bottom",
                y=1.035,
                xanchor="center",
                x=0.5,
                font=dict(size=10, color=C_TEXT),
                bgcolor="rgba(255,255,255,.92)",
                bordercolor=C_BORDER,
                borderwidth=1,
            ),
            height=max(360 * nrows, 430),
            margin=dict(t=75, b=25, l=15, r=15),
        )

        st.plotly_chart(
            fig_multi,
            use_container_width=True,
            config={"displayModeBar": False},
        )

        insight_box(
            "🎨 <b>Legenda warna berlaku untuk seluruh dashboard:</b> "
            "0–5 kt biru · 5–10 kt hijau · 10–15 kt kuning · "
            "15–20 kt oranye · 20–25 kt merah · >25 kt merah tua."
        )


# ============================================================
# TAB 4 — RINGKASAN
# ============================================================
with tab4:
    section_title(
        "Ringkasan Otomatis",
        "Narasi dibuat langsung dari data yang sedang aktif dan dapat dijadikan draf pembahasan.",
    )

    if df_filtered.empty:
        st.warning("Tidak ada data untuk dibuatkan ringkasan.")
    else:
        st.markdown("### Ringkasan periode terpilih")
        insight_box(
            narasi_arah_dominan(
                df_filtered,
                f"Periode terpilih · {ketinggian_pilih}",
            )
        )

        st.markdown("### Ringkasan per bulan")

        bulan_lines = []

        for bulan in BULAN_URUT:
            if bulan not in bulan_pilih:
                continue

            d_bulan = df[
                (df["sheet_bulan"] == bulan)
                & (df["ketinggian"] == ketinggian_pilih)
                & (df["jam_observasi"].isin(jam_pilih))
            ]

            bulan_lines.append(
                f"<li>{narasi_arah_dominan(d_bulan, bulan)}</li>"
            )

        if bulan_lines:
            insight_box(
                "<ul style='margin:0;padding-left:18px;'>"
                + "".join(bulan_lines)
                + "</ul>"
            )

        st.markdown("### Ringkasan per musim")

        musim_lines = []

        for season in SEASON_ORDER:
            d_season = df[
                (df["ketinggian"] == ketinggian_pilih)
                & (df["musim"] == season)
                & (df["sheet_bulan"].isin(bulan_pilih))
                & (df["jam_observasi"].isin(jam_pilih))
            ]

            musim_lines.append(
                f"<li>{narasi_arah_dominan(d_season, season)}</li>"
            )

        insight_box(
            "<ul style='margin:0;padding-left:18px;'>"
            + "".join(musim_lines)
            + "</ul>"
        )

        st.divider()
st.caption(
    "Dashboard PIBAL 2025 · Stasiun Meteorologi Klas I Juanda, Sidoarjo"
)
