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
    # KPIs
    # =====================================

    real = data["Real"].sum()
    obj1 = data["LE1"].sum()

    gap1 = real - obj1
    pct1 = 0 if obj1 == 0 else (gap1 / obj1) * 100

    st.subheader(st.session_state.repre)

    # =====================================
    # TENDENCIA
    # =====================================

    mes_actual = datetime.now().month

    # asegurar numérico
    data["Mes"] = pd.to_numeric(data["Mes"], errors="coerce")
    data_ly["Mes"] = pd.to_numeric(data_ly["Mes"], errors="coerce")

    # 2026
    t2026 = (
        data.groupby("Mes", as_index=False)[["Real","LE1"]].sum()
    )

    # 2025
    t2025 = (
        data_ly.groupby("Mes", as_index=False)[["Real"]]
        .sum()
        .rename(columns={"Real": "Real_2025"})
    )

    # merge
    tendencia = t2026.merge(t2025, on="Mes", how="outer")

    # completar meses
    base = pd.DataFrame({"Mes": range(1,13)})
    tendencia = base.merge(tendencia, on="Mes", how="left").fillna(0)

    # ocultar futuro (sin 0 en real)
    tendencia["Real"] = tendencia["Real"].where(
        tendencia["Mes"] <= mes_actual
    )

    # etiquetas
    meses_map = {
        1:"Ene",2:"Feb",3:"Mar",4:"Abr",
        5:"May",6:"Jun",7:"Jul",8:"Ago",
        9:"Sep",10:"Oct",11:"Nov",12:"Dic"
    }

    tendencia["Mes_txt"] = tendencia["Mes"].map(meses_map)

    # =====================================
    # GRAFICA (CORREGIDA A TUS COLUMNAS)
    # =====================================

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