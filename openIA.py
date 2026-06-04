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
# UI FIX (SOLO DISEÑO)
# =====================================

st.markdown("""
<style>
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}

.block-container {
    padding-top: 0.5rem;
    padding-bottom: 0rem;
}

div[data-testid="stVerticalBlock"] {
    gap: 0.25rem;
}

iframe {
    margin-top: 0px !important;
}

h3 {
    margin-top: 0px !important;
    margin-bottom: 4px !important;
}
</style>
""", unsafe_allow_html=True)

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
# SELECTOR (GRID 2 COLUMNAS)
# =====================================

if st.session_state.page == "selector":

    st.markdown("### 📊 App Representados")
    st.markdown(
    "<div style='font-size:15px;color:#9CA3AF;margin-bottom:8px;'>Selecciona un representante</div>",
    unsafe_allow_html=True
)

    cols = st.columns(2)

    reps = sorted(df["Repre"].dropna().unique())

    for i, r in enumerate(reps):
        with cols[i % 2]:
            if st.button(r, use_container_width=True):
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

    # =====================================
    # BACK BUTTON + HEADER
    # =====================================

    col1, col2 = st.columns([1, 8])

    with col1:
        if st.button("⬅"):
            st.session_state.page = "selector"
            st.rerun()

    with col2:
        st.markdown(f"### {st.session_state.repre}")

    # =====================================
    # KPI
    # =====================================

    mes_actual = datetime.now().month

    data["Mes"] = pd.to_numeric(data["Mes"], errors="coerce")
    data_ly["Mes"] = pd.to_numeric(data_ly["Mes"], errors="coerce")

    real_ytd = data.loc[data["Mes"] <= mes_actual, "Real"].sum()
    le1_ytd = data.loc[data["Mes"] <= mes_actual, "LE1"].sum()
    ly_ytd = data_ly.loc[data_ly["Mes"] <= mes_actual, "Real"].sum()

    diff_le1 = real_ytd - le1_ytd
    diff_ly = real_ytd - ly_ytd

    def fmt(v):
        icon = "▲" if v > 0 else "▼" if v < 0 else "●"
        color = "#16A34A" if v > 0 else "#D9534F" if v < 0 else "#6B7280"
        return f"<span style='color:{color};font-weight:600'>{icon} {v:,.0f}</span>"

    def fmt_pct(v):
        color = "#16A34A" if v > 0 else "#D9534F" if v < 0 else "#6B7280"
        return f"<span style='color:{color};font-weight:600'>({v:.1f}%)</span>"

    card_html = f"""
    <div style="
    font-family:Arial;
    background:white;
    border:1px solid #E5E7EB;
    border-radius:14px;
    padding:10px;
    max-width:210px;
    width:100%;
    box-sizing:border-box;
    display:inline-block;
">

        <div style="font-size:11px;color:#888;">Volumen CJ9L YTD</div>

        <div style="font-size:32px;font-weight:bold;color:#1D4ED8;">
            {real_ytd:,.0f}
        </div>

        <div style="font-size:11px;">
            LE1: {le1_ytd:,.0f} {fmt(diff_le1)} {fmt_pct((diff_le1/le1_ytd)*100 if le1_ytd else 0)}
        </div>

        <div style="font-size:11px;">
            2025: {ly_ytd:,.0f} {fmt(diff_ly)} {fmt_pct((diff_ly/ly_ytd)*100 if ly_ytd else 0)}
        </div>

    </div>
    """

    components.html(card_html, height=130)

    # =====================================
    # TÍTULO
    # =====================================

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    st.markdown(
        "<div style='font-size:13px;font-weight:600;color:#9CA3AF;'>Evolución mensual (K)</div>",
        unsafe_allow_html=True
    )

    # =====================================
    # DATA TENDENCIA (SEGURO Y SIN ERRORES)
    # =====================================

    meses_map = {
        1:"Ene",2:"Feb",3:"Mar",4:"Abr",
        5:"May",6:"Jun",7:"Jul",8:"Ago",
        9:"Sep",10:"Oct",11:"Nov",12:"Dic"
    }

    t2026 = data.groupby("Mes", as_index=False)[["Real","LE1"]].sum()
    t2025 = data_ly.groupby("Mes", as_index=False)[["Real"]].sum().rename(columns={"Real":"Real_2025"})

    tendencia = pd.DataFrame({"Mes": range(1, 13)})

    tendencia = tendencia.merge(t2026, on="Mes", how="left")
    tendencia = tendencia.merge(t2025, on="Mes", how="left")

    # NO rellenar ventas reales futuras
    tendencia["Real"] = tendencia["Real"]
    tendencia["LE1"] = tendencia["LE1"].fillna(0)
    tendencia["Real_2025"] = tendencia["Real_2025"].fillna(0)

    tendencia["Mes_txt"] = tendencia["Mes"].map(meses_map)

    orden_meses = list(meses_map.values())

    tendencia["Real_k"] = tendencia["Real"] / 1000
    tendencia["LE1_k"] = tendencia["LE1"] / 1000
    tendencia["LY_k"] = tendencia["Real_2025"] / 1000

    tendencia.loc[tendencia["Mes"] > mes_actual, "Real_k"] = np.nan

    # =====================================
    # GRÁFICA CON LEYENDA
    # =====================================

    base = tendencia.melt(
        id_vars=["Mes_txt"],
        value_vars=["Real_k", "LY_k", "LE1_k"],
        var_name="Serie",
        value_name="Valor"
    )

    base["Serie"] = base["Serie"].map({
        "Real_k": "Volumen 2026",
        "LY_k": "Volumen 2025",
        "LE1_k": "LE1"
    })

    color_scale = alt.Scale(
        domain=["Volumen 2026", "LE1", "Volumen 2025"],
        range=["#2563EB", "#F59E0B", "#9CA3AF"]
    )

    chart = alt.Chart(base).mark_line(size=2.5).encode(
        x=alt.X("Mes_txt:N", sort=orden_meses, axis=alt.Axis(title=None)),
        y=alt.Y("Valor:Q", axis=alt.Axis(title=None)),
        color=alt.Color(
            "Serie:N",
            scale=color_scale,
            legend=alt.Legend(orient="bottom")
        )
    )

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    st.altair_chart(chart, use_container_width=True)