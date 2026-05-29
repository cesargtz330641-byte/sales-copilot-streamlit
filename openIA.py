import streamlit as st
import pandas as pd

# =========================
# 🔐 LOGIN SIMPLE
# =========================

PASSWORD = "Ventas2026"

password = st.text_input(
    "Ingresa la contraseña",
    type="password"
)

if password != PASSWORD:
    st.warning("Acceso restringido")
    st.stop()

# =========================
# 📂 CARGA DE DATOS
# =========================

df = pd.read_excel("ChatBox.xlsx")

df["Gap"] = df["Venta"] - df["Objetivo 1"]

# =========================
# 📱 CONFIG MOBILE
# =========================
st.set_page_config(page_title="Sales Mobile Pro", layout="centered")

# =========================
# 🧠 STATE
# =========================
if "page" not in st.session_state:
    st.session_state.page = "selector"

if "repre" not in st.session_state:
    st.session_state.repre = None

# =========================
# 🟢 PANTALLA 1: SELECTOR MOBILE
# =========================
if st.session_state.page == "selector":

    st.title("📱 Sales Mobile Pro")

    st.write("Selecciona un representado:")

    reps = sorted(df["Repre"].dropna().unique())

    for r in reps:
        if st.button(f"📊 {r}", use_container_width=True):
            st.session_state.repre = r
            st.session_state.page = "dashboard"
            st.rerun()

# =========================
# 🔵 DASHBOARD MOBILE
# =========================
if st.session_state.page == "dashboard":

    data = df[df["Repre"] == st.session_state.repre].copy()

    st.title(f"📊 {st.session_state.repre}")

    if st.button("⬅ Volver"):
        st.session_state.page = "selector"
        st.rerun()

    # =========================
    # 📊 KPIs COMO TARJETAS
    # =========================
# =========================
# KPIs
# =========================

ventas_2026 = data[data["Anio"] == 2026]["Venta"].sum()

objetivo_2026 = data[data["Anio"] == 2026]["Objetivo 1"].sum()

ventas_2025 = data[data["Anio"] == 2025]["Venta"].sum()

gap = ventas_2026 - objetivo_2026

crecimiento = (
    (ventas_2026 / ventas_2025) - 1
    if ventas_2025 > 0
    else 0
)

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Ventas YTD 2026",
    f"{ventas_2026:,.0f}"
)

col2.metric(
    "Objetivo YTD 2026",
    f"{objetivo_2026:,.0f}"
)

col3.metric(
    "Gap YTD",
    f"{gap:,.0f}"
)

col4.metric(
    "Crecimiento vs 2025",
    f"{crecimiento:.1%}"
)

    # =========================
    # 📈 GRÁFICO COMPACTO
    # =========================
# =========================
# TENDENCIA
# =========================

st.subheader("📈 Tendencia mensual")

ventas_2026_mes = (
    data[data["Anio"] == 2026]
    .groupby("Mes")["Venta"]
    .sum()
)

ventas_2025_mes = (
    data[data["Anio"] == 2025]
    .groupby("Mes")["Venta"]
    .sum()
)

objetivo_mes = (
    data[data["Anio"] == 2026]
    .groupby("Mes")["Objetivo 1"]
    .sum()
)

chart_df = pd.DataFrame({
    "Ventas 2026": ventas_2026_mes,
    "Ventas 2025": ventas_2025_mes,
    "Objetivo": objetivo_mes
}).fillna(0)

st.line_chart(chart_df)

    