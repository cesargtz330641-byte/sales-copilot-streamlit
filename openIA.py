import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
from datetime import datetime
import altair as alt

# =====================================
# CONFIG
# =====================================

st.set_page_config(page_title="Sales Mobile Pro", layout="centered")

# =====================================
# LOGIN
# =====================================

PASSWORD = "Ventas2026"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    password = st.text_input("Ingresa la contraseña", type="password")

    if password == PASSWORD:
        st.session_state.authenticated = True
        st.rerun()

    st.warning("Acceso restringido")
    st.stop()

# =====================================
# DATA
# =====================================

df = pd.read_excel("ChatBox.xlsx")
df.columns = df.columns.str.strip()

# =====================================
# SESSION
# =====================================

if "page" not in st.session_state:
    st.session_state.page = "selector"

if "repre" not in st.session_state:
    st.session_state.repre = None

# =====================================
# SELECTOR
# =====================================

if st.session_state.page == "selector":

    st.title("📱 Sales Mobile Pro")

    reps = sorted(df["Repre"].dropna().unique())

    for r in reps:
        if st.button(f"📊 {r}", use_container_width=True):
            st.session_state.repre = r
            st.session_state.page = "dashboard"
            st.rerun()

# =====================================
# DASHBOARD
# =====================================

if st.session_state.page == "dashboard":

    data_2026 = df[
        (df["Repre"] == st.session_state.repre)
        & (df["Anio"] == 2026)
    ].copy()

    data_2025 = df[
        (df["Repre"] == st.session_state.repre)
        & (df["Anio"] == 2025)
    ].copy()

    col1, col2 = st.columns([1, 6])

    with col1:
        if st.button("⬅", use_container_width=True):
          st.session_state.page = "selector"
          st.rerun()

    with col2:
     st.markdown(" ")

    # =====================================
    # MES ACTUAL (YTD LIMIT)
    # =====================================

    mes_actual = datetime.now().month

    data_2026["Mes"] = pd.to_numeric(data_2026["Mes"], errors="coerce")
    data_2025["Mes"] = pd.to_numeric(data_2025["Mes"], errors="coerce")

    # ==============================
    # KPI YTD (CORRECTO)
    # ==============================

    real_ytd = data_2026.loc[data_2026["Mes"] <= mes_actual, "Real"].sum()
    le1_ytd = data_2026.loc[data_2026["Mes"] <= mes_actual, "LE1"].sum()
    ly_ytd = data_2025.loc[data_2025["Mes"] <= mes_actual, "Real"].sum()

    diff_le1 = real_ytd - le1_ytd
    diff_ly = real_ytd - ly_ytd

    pct_le1 = 0 if le1_ytd == 0 else (diff_le1 / le1_ytd) * 100
    pct_ly = 0 if ly_ytd == 0 else (diff_ly / ly_ytd) * 100

    def fmt(v, p):
        icon = "▲" if v > 0 else "▼" if v < 0 else "●"
        color = "#16A34A" if v > 0 else "#D9534F" if v < 0 else "#6B7280"
        return f"<span style='color:{color};font-weight:bold;margin-left:6px;'>{icon} {v:,.0f} ({p:.1f}%)</span>"

    st.subheader(st.session_state.repre)

    # =====================================
    # CARD KPI
    # =====================================

    card_html = f"""
    <div style="
        font-family:Arial;
        background:white;
        border:1px solid #E5E7EB;
        border-radius:18px;
        padding:12px;
        display:inline-block;
        width:380px;
    ">

        <div style="font-size:12px;color:#999;">Volumen YTD 2026</div>

        <div style="font-size:42px;font-weight:bold;color:#1D4ED8;">
            {real_ytd:,.0f}
        </div>

        <div style="font-size:12px;margin-top:6px;">
            <b>LE1:</b> {le1_ytd:,.0f}
            {fmt(diff_le1, pct_le1)}
        </div>

        <div style="font-size:12px;margin-top:4px;">
            <b>2025:</b> {ly_ytd:,.0f}
            {fmt(diff_ly, pct_ly)}
        </div>

    </div>
    """

    components.html(card_html, height=140)
    st.markdown("<div style='margin-top:-30px'></div>", unsafe_allow_html=True)

    # =====================================
    # TENDENCIA
    # =====================================

    
    st.markdown("### Evolución mensual")

    meses_map = {
        1:"Ene",2:"Feb",3:"Mar",4:"Abr",
        5:"May",6:"Jun",7:"Jul",8:"Ago",
        9:"Sep",10:"Oct",11:"Nov",12:"Dic"
    }

    t2026 = data_2026.groupby("Mes", as_index=False)[["Real","LE1"]].sum()
    t2025 = data_2025.groupby("Mes", as_index=False)[["Real"]].sum().rename(columns={"Real":"Real_2025"})

    tendencia = pd.DataFrame({"Mes": range(1,13)})
    tendencia = tendencia.merge(t2026, on="Mes", how="left").merge(t2025, on="Mes", how="left")

    tendencia = tendencia.fillna(0)

    tendencia["Mes_txt"] = tendencia["Mes"].map(meses_map)

    # ==========================
# GRAFICA EN MILES + FUTURO EN BLANCO
# ==========================

tendencia["Real_k"] = tendencia["Real"] / 1000
tendencia["LE1_k"] = tendencia["LE1"] / 1000
tendencia["LY_k"] = tendencia["Real_2025"] / 1000

# 🔥 CLAVE: futuros como NaN (no 0)
tendencia.loc[tendencia["Mes"] > mes_actual, "Real_k"] = np.nan

chart = alt.Chart(tendencia).mark_line().encode(
    x=alt.X(
        "Mes_txt:N",
        sort=list(meses_map.values()),
        axis=alt.Axis(title=None)
    ),
    y=alt.Y(
        "Real_k:Q",
        axis=alt.Axis(
            title="Ventas en k"
        )
    ),
    color=alt.value("#1D4ED8")
) + alt.Chart(tendencia).mark_line(strokeDash=[5,5]).encode(
    x=alt.X("Mes_txt:N", sort=list(meses_map.values())),
    y="LE1_k:Q",
    color=alt.value("#16A34A")
) + alt.Chart(tendencia).mark_line(strokeDash=[2,2]).encode(
    x=alt.X("Mes_txt:N", sort=list(meses_map.values())),
    y="LY_k:Q",
    color=alt.value("#999999")
)

st.altair_chart(chart, use_container_width=True)