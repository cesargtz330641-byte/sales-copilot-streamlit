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
# DASHBOARD
# =========================

st.title("📊 Sales Mobile Pro")

st.subheader("Venta YTD 2026")

st.metric(
    label="Venta",
    value=f"${venta_ytd:,.0f}"
)

st.divider()

st.metric(
    label="Objetivo 1",
    value=f"${obj1_ytd:,.0f}",
    delta=f"{gap_obj1:,.0f} ({pct_obj1:.1f}%)"
)

st.metric(
    label="Objetivo 2",
    value=f"${obj2_ytd:,.0f}",
    delta=f"{gap_obj2:,.0f} ({pct_obj2:.1f}%)"
)