import streamlit as st
import pandas as pd

# =====================================

# SEGURIDAD

# =====================================

PASSWORD = "Ventas2026"

password = st.text_input(
"🔐 Contraseña",
type="password"
)

if password != PASSWORD:
st.stop()

# =====================================

# CONFIG

# =====================================

st.set_page_config(
page_title="Sales Copilot",
layout="wide"
)

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

# PANTALLA 1

# =====================================

if st.session_state.page == "selector":

```
st.title("📊 Sales Copilot")

st.write("Selecciona un representado")

reps = sorted(df["Repre"].dropna().unique())

for r in reps:

    if st.button(
        f"📈 {r}",
        use_container_width=True
    ):
        st.session_state.repre = r
        st.session_state.page = "dashboard"
        st.rerun()
```

# =====================================

# PANTALLA 2

# =====================================

if st.session_state.page == "dashboard":

```
data = df[
    df["Repre"] == st.session_state.repre
].copy()

st.title(
    f"📊 {st.session_state.repre}"
)

st.caption(
    "Ventas acumuladas YTD 2026"
)

if st.button("⬅ Volver"):
    st.session_state.page = "selector"
    st.rerun()

# =====================================
# KPIs
# =====================================

ventas_2026 = data[
    data["Anio"] == 2026
]["Venta"].sum()

objetivo_2026 = data[
    data["Anio"] == 2026
]["Objetivo 1"].sum()

ventas_2025 = data[
    data["Anio"] == 2025
]["Venta"].sum()

gap = ventas_2026 - objetivo_2026

crecimiento = (
    (ventas_2026 / ventas_2025) - 1
    if ventas_2025 > 0
    else 0
)

st.subheader("📊 KPIs")

# FILA 1
col1, col2 = st.columns(2)

with col1:
    st.metric(
        "Ventas YTD 2026",
        f"${ventas_2026:,.0f}"
    )

with col2:
    st.metric(
        "Objetivo YTD 2026",
        f"${objetivo_2026:,.0f}"
    )

# FILA 2
col3, col4 = st.columns(2)

with col3:
    st.metric(
        "Gap YTD",
        f"${gap:,.0f}"
    )

with col4:
    st.metric(
        "Crecimiento vs 2025",
        f"{crecimiento:.1%}"
    )

st.divider()

# =====================================
# TENDENCIA
# =====================================

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
    "Objetivo 2026": objetivo_mes
}).fillna(0)

st.line_chart(
    chart_df,
    use_container_width=True
)

st.divider()

# =====================================
# OPORTUNIDADES
# =====================================

st.subheader("🎯 Oportunidades")

data_2026 = data[
    data["Anio"] == 2026
].copy()

data_2026["Gap"] = (
    data_2026["Venta"]
    - data_2026["Objetivo 1"]
)

# REGIÓN
gap_region = (
    data_2026
    .groupby("Region")["Gap"]
    .sum()
    .sort_values()
)

peor_region = gap_region.index[0]
valor_region = gap_region.iloc[0]

# CANAL
gap_canal = (
    data_2026
    .groupby("Canal")["Gap"]
    .sum()
    .sort_values()
)

peor_canal = gap_canal.index[0]
valor_canal = gap_canal.iloc[0]

# CLIENTE
gap_cliente = (
    data_2026
    .groupby("Cliente")["Gap"]
    .sum()
    .sort_values()
)

peor_cliente = gap_cliente.index[0]
valor_cliente = gap_cliente.iloc[0]

col1, col2 = st.columns(2)

with col1:
    st.metric(
        "Mayor Gap Región",
        peor_region,
        f"${valor_region:,.0f}"
    )

with col2:
    st.metric(
        "Mayor Gap Canal",
        peor_canal,
        f"${valor_canal:,.0f}"
    )

st.metric(
    "Mayor Gap Cliente",
    peor_cliente,
    f"${valor_cliente:,.0f}"
)