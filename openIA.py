import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
from datetime import datetime
import altair as alt

# =====================================
# CONFIG
# =====================================

st.set_page_config(
    page_title="Sales Mobile Pro",
    layout="centered"
)

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

    data = df[
        (df["Repre"] == st.session_state.repre)
        & (df["Anio"] == 2026)
    ].copy()

    data_ly = df[
        (df["Repre"] == st.session_state.repre)
        & (df["Anio"] == 2025)
    ].copy()

    if st.button("⬅ Volver"):
        st.session_state.page = "selector"
        st.rerun()

    # =====================================
    # KPIs BASE
    # =====================================

    real_2026 = data["Real"].sum()
    le1_2026 = data["LE1"].sum()
    real_2025 = data_ly["Real"].sum()

    diff_le1 = real_2026 - le1_2026
    diff_ly = real_2026 - real_2025

    pct_le1 = 0 if le1_2026 == 0 else (diff_le1 / le1_2026) * 100
    pct_ly = 0 if real_2025 == 0 else (diff_ly / real_2025) * 100

    def format_inline(value, pct):
        if value > 0:
            icon = "▲"
            color = "#16A34A"
        elif value < 0:
            icon = "▼"
            color = "#D9534F"
        else:
            icon = "●"
            color = "#6B7280"

        return f"""
        <span style="color:{color};font-weight:bold;margin-left:6px;">
            {icon} {value:,.0f} ({pct:.1f}%)
        </span>
        """

    st.subheader(st.session_state.repre)

    # =====================================
    # CARD KPI (INLINE)
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

        <div style="font-size:12px;color:#999;">
            Volumen YTD 2026
        </div>

        <div style="font-size:42px;font-weight:bold;color:#1D4ED8;">
            {real_2026:,.0f}
        </div>

        <div style="font-size:12px;margin-top:6px;">
            <b>LE1:</b> {le1_2026:,.0f}
            {format_inline(diff_le1, pct_le1)}
        </div>

        <div style="font-size:12px;margin-top:4px;">
            <b>2025:</b> {real_2025:,.0f}
            {format_inline(diff_ly, pct_ly)}
        </div>

    </div>
    """

    components.html(card_html, height=200)

    # =====================================
    # TENDENCIA
    # =====================================

    st.subheader("Tendencia")

    mes_actual = datetime.now().month

    meses_map = {
        1:"Ene",2:"Feb",3:"Mar",4:"Abr",
        5:"May",6:"Jun",7:"Jul",8:"Ago",
        9:"Sep",10:"Oct",11:"Nov",12:"Dic"
    }

    data["Mes"] = pd.to_numeric(data["Mes"], errors="coerce")
    data_ly["Mes"] = pd.to_numeric(data_ly["Mes"], errors="coerce")

    t2026 = data.groupby("Mes", as_index=False)[["Real","LE1"]].sum()
    t2025 = data_ly.groupby("Mes", as_index=False)[["Real"]].sum().rename(columns={"Real":"Real_2025"})

    tendencia = t2026.merge(t2025, on="Mes", how="outer")

    base = pd.DataFrame({"Mes": range(1,13)})
    tendencia = base.merge(tendencia, on="Mes", how="left").fillna(0)

    tendencia["Real"] = tendencia["Real"].where(tendencia["Mes"] <= mes_actual)

    tendencia["Mes_txt"] = tendencia["Mes"].map(meses_map)

    chart = alt.Chart(tendencia).mark_line().encode(
        x=alt.X("Mes_txt:N", sort=list(meses_map.values())),
        y="Real:Q",
        color=alt.value("#1D4ED8")
    ) + alt.Chart(tendencia).mark_line(strokeDash=[5,5]).encode(
        x=alt.X("Mes_txt:N", sort=list(meses_map.values())),
        y="LE1:Q",
        color=alt.value("#16A34A")
    ) + alt.Chart(tendencia).mark_line(strokeDash=[2,2]).encode(
        x=alt.X("Mes_txt:N", sort=list(meses_map.values())),
        y="Real_2025:Q",
        color=alt.value("#999999")
    )

    st.altair_chart(chart, use_container_width=True)