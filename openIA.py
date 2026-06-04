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

    password = st.text_input(
        "Ingresa la contraseña",
        type="password"
    )

    if password == PASSWORD:
        st.session_state.authenticated = True
        st.rerun()

    st.warning("Acceso restringido")
    st.stop()

# =====================================
# DATA
# =====================================

df = pd.read_excel("ChatBox.xlsx")

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

        if st.button(
            f"📊 {r}",
            use_container_width=True
        ):
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

    card_html = f"""
    <div style="
        font-family:Arial,sans-serif;
        background:white;
        border:1px solid #E5E7EB;
        border-radius:18px;
        padding:12px;
        display:inline-block;
    ">

        <div style="
            font-size:12px;
            color:#999;
            margin-bottom:4px;
        ">
            Volumen YTD 2026
        </div>

        <div style="
            font-size:42px;
            font-weight:bold;
            color:#1D4ED8;
            line-height:1;
            margin-bottom:10px;
        ">
            {venta:,.0f}
        </div>

        <div style="
            display:flex;
            gap:8px;
            font-size:12px;
            margin-bottom:4px;
            align-items:center;
            flex-wrap:wrap;
        ">
            <span><b>Objetivo 1</b></span>
            <span>{obj1:,.0f}</span>
            <span style="color:{color1};font-weight:bold;">
                {gap1:,.0f}
            </span>
            <span style="color:{color1};font-weight:bold;">
                {pct1:.0f}%
            </span>
        </div>

        <div style="
            display:flex;
            gap:8px;
            font-size:12px;
            align-items:center;
            flex-wrap:wrap;
        ">
            <span><b>Objetivo 2</b></span>
            <span>{obj2:,.0f}</span>
            <span style="color:{color2};font-weight:bold;">
                {gap2:,.0f}
            </span>
            <span style="color:{color2};font-weight:bold;">
                {pct2:.0f}%
            </span>
        </div>

    </div>
    """

    components.html(card_html, height=140, scrolling=False)

    # =====================================
    # TENDENCIA (CORREGIDA BIEN)
    # =====================================

    st.subheader("Tendencia")

    mes_actual = datetime.now().month

meses_nombre = {
    1:"Ene",2:"Feb",3:"Mar",4:"Abr",
    5:"May",6:"Jun",7:"Jul",8:"Ago",
    9:"Sep",10:"Oct",11:"Nov",12:"Dic"
}

orden_meses = list(meses_nombre.keys())

# =========================
# AGRUPAR (SIN TOCAR MES)
# =========================
tendencia = (
    data
    .groupby("Mes", as_index=False)[["Venta","Objetivo 1","Objetivo 2"]]
    .sum()
)

# =========================
# ASEGURAR ORDEN NUMÉRICO REAL
# =========================
tendencia = tendencia.sort_values("Mes")

# =========================
# OCULTAR FUTURO (SIN 0)
# =========================
tendencia["Venta"] = tendencia["Venta"].where(
    tendencia["Mes"] <= mes_actual
)

# =========================
# MAPEAR A TEXTO SOLO AL FINAL
# =========================
tendencia["Mes"] = tendencia["Mes"].map(meses_nombre)

# =========================
# ASEGURAR LOS 12 MESES SIEMPRE
# =========================
base = pd.DataFrame({
    "Mes": list(meses_nombre.values())
})

tendencia = base.merge(
    tendencia,
    on="Mes",
    how="left"
)

st.line_chart(
    tendencia.set_index("Mes")[["Venta","Objetivo 1","Objetivo 2"]]
)