import streamlit as st
import pandas as pd

# =========================
# CONFIG
# =========================

st.set_page_config(
    page_title="Sales Mobile Pro",
    layout="centered"
)

# =========================
# LOGIN
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
# CARGA DE DATOS
# =========================

df = pd.read_excel("ChatBox.xlsx")

# =========================
# FILTRO YTD 2026
# =========================

data = df[df["Anio"] == 2026].copy()

# =========================
# CALCULOS
# =========================

venta_ytd = data["Venta"].sum()

obj1_ytd = data["Objetivo 1"].sum()
obj2_ytd = data["Objetivo 2"].sum()

gap_obj1 = venta_ytd - obj1_ytd
gap_obj2 = venta_ytd - obj2_ytd

pct_obj1 = 0 if obj1_ytd == 0 else (gap_obj1 / obj1_ytd) * 100
pct_obj2 = 0 if obj2_ytd == 0 else (gap_obj2 / obj2_ytd) * 100

# =========================
# DASHBOARD REPRE
# =========================

if st.session_state.page == "dashboard":

    data = df[
        (df["Repre"] == st.session_state.repre) &
        (df["Anio"] == 2026)
    ].copy()

    st.title(f"📊 {st.session_state.repre}")

    if st.button("⬅ Volver"):
        st.session_state.page = "selector"
        st.rerun()

    # =========================
    # YTD
    # =========================

    venta_ytd = data["Venta"].sum()

    obj1_ytd = data["Objetivo 1"].sum()
    obj2_ytd = data["Objetivo 2"].sum()

    gap1 = venta_ytd - obj1_ytd
    gap2 = venta_ytd - obj2_ytd

    pct1 = 0 if obj1_ytd == 0 else gap1 / obj1_ytd * 100
    pct2 = 0 if obj2_ytd == 0 else gap2 / obj2_ytd * 100

    # =========================
    # TARJETA PRINCIPAL
    # =========================

    st.subheader("💰 Venta YTD 2026")

    st.metric(
        label="Venta",
        value=f"${venta_ytd:,.0f}"
    )

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            label="Objetivo 1",
            value=f"${obj1_ytd:,.0f}",
            delta=f"{gap1:,.0f} ({pct1:.1f}%)"
        )

    with col2:
        st.metric(
            label="Objetivo 2",
            value=f"${obj2_ytd:,.0f}",
            delta=f"{gap2:,.0f} ({pct2:.1f}%)"
        )