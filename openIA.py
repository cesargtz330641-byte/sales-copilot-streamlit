import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
from datetime import datetime

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

    if st.button("⬅ Volver"):
        st.session_state.page = "selector"
        st.rerun()

    # =====================================
    # KPIs
    # =====================================

    venta = data["Venta"].sum()
    obj1 = data["Objetivo 1"].sum()
    obj2 = data["Objetivo 2"].sum()

    gap1 = venta - obj1
    gap2 = venta - obj2

    pct1 = 0 if obj1 == 0 else (gap1 / obj1) * 100
    pct2 = 0 if obj2 == 0 else (gap2 / obj2) * 100

    color1 = "#D9534F" if gap1 < 0 else "#16A34A"
    color2 = "#D9534F" if gap2 < 0 else "#16A34A"

    st.subheader(st.session_state.repre)

    # =====================================
    # CARD
    # =====================================

    card_html = f"""
    <div style="
        font-family:Arial;
        background:white;
        border:1px solid #E5E7EB;
        border-radius:18px;
        padding:12px;
        display:inline-block;
    ">
        <div style="font-size:12px;color:#999;">Volumen YTD 2026</div>

        <div style="font-size:42px;font-weight:bold;color:#1D4ED8;">
            {venta:,.0f}
        </div>

        <div style="font-size:12px;">
            <b>Obj1:</b> {obj1:,.0f} |
            <span style="color:{color1};">{gap1:,.0f} ({pct1:.0f}%)</span>
        </div>

        <div style="font-size:12px;">
            <b>Obj2:</b> {obj2:,.0f} |
            <span style="color:{color2};">{gap2:,.0f} ({pct2:.0f}%)</span>
        </div>
    </div>
    """

    components.html(card_html, height=140)

    # =====================================
    # TENDENCIA (FIX DEFINITIVO)
    # =====================================

    st.subheader("Tendencia")

    mes_actual = datetime.now().month

    # asegurar numérico
    data["Mes_num"] = pd.to_numeric(data["Mes_num"], errors="coerce")

    tendencia = (
        data
        .groupby("Mes_num", as_index=False)[
            ["Venta","Objetivo 1","Objetivo 2"]
        ]
        .sum()
        .sort_values("Mes_num")
    )

    # 🔥 ocultar futuro SIN 0
    tendencia["Venta"] = tendencia["Venta"].where(
        tendencia["Mes_num"] <= mes_actual
    )

    # completar meses faltantes (Ene-Dic fijo)
    base = pd.DataFrame({"Mes_num": range(1,13)})

    tendencia = base.merge(tendencia, on="Mes_num", how="left")

    tendencia = tendencia.fillna(0)

    # 🔥 GRAFICA (ORDEN GARANTIZADO)
    st.line_chart(
        tendencia.set_index("Mes_num")[[
            "Venta","Objetivo 1","Objetivo 2"
        ]]
    )