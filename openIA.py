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
    col1, col2 = st.columns(2)

    col1.metric("Ventas", f"{data['Venta'].sum():,.0f}")
    col2.metric("Objetivo", f"{data['Objetivo 1'].sum():,.0f}")

    col3, col4 = st.columns(2)

    col3.metric("Gap", f"{data['Gap'].sum():,.0f}")
    col4.metric("Meses", data["Mes"].nunique())

    st.divider()

    # =========================
    # 📈 GRÁFICO COMPACTO
    # =========================
    st.subheader("📈 Tendencia")

    chart = data.groupby("Mes")[["Venta", "Objetivo 1"]].sum()
    st.line_chart(chart)

    st.divider()

    # =========================
    # 🎯 INSIGHTS CORTOS (MOBILE FRIENDLY)
    # =========================
    st.subheader("🧠 Insights")

    total_gap = data["Gap"].sum()

    worst = data.groupby("Mes")["Gap"].sum().idxmin()
    best = data.groupby("Mes")["Gap"].sum().idxmax()

    if total_gap > 0:
        st.success("🟢 Above target")
    else:
        st.error("🔴 Below target")

    st.write(f"📉 Peor mes: **{worst}**")
    st.write(f"📈 Mejor mes: **{best}**")

    # concentración
    top_month = data.groupby("Mes")["Venta"].sum().max()
    concentration = top_month / data["Venta"].sum()

    if concentration > 0.4:
        st.warning("⚠️ Alta dependencia de un mes")

    st.divider()

    # =========================
    # 📊 TOP / BOTTOM (MOBILE STYLE)
    # =========================
    st.subheader("📊 Ranking mensual")

    rank = data.groupby("Mes")["Venta"].sum().sort_values(ascending=False)

    for mes, val in rank.items():
        st.write(f"📅 Mes {mes}: **{val:,.0f}**")