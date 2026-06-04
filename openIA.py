import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
from datetime import datetime
import altair as alt

st.set_page_config(page_title="Sales Mobile Pro", layout="centered")

# =====================================
# UI GLOBAL FIX (CLAVE)
# =====================================

st.markdown("""
<style>
.block-container {
    padding-top: 0.8rem;
    padding-bottom: 0rem;
}

div[data-testid="stVerticalBlock"] {
    gap: 0.35rem;
}

/* Botones más compactos */
div[data-testid="stButton"] {
    margin: 0px;
    padding: 0px;
}

/* Reduce espacio markdown */
div[data-testid="stMarkdownContainer"] {
    margin: 0px;
}

/* Oculta espacios de charts */
iframe {
    margin-top: -10px;
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
    password = st.text_input("Acceso", type="password")

    if password == PASSWORD:
        st.session_state.authenticated = True
        st.rerun()

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

    st.markdown("### 📊 Sales Mobile Pro")

    reps = sorted(df["Repre"].dropna().unique())

    for r in reps:
        if st.button(f"➡ {r}", use_container_width=True):
            st.session_state.repre = r
            st.session_state.page = "dashboard"
            st.rerun()

# =====================================
# DASHBOARD
# =====================================

if st.session_state.page == "dashboard":

    data_2026 = df[(df["Repre"] == st.session_state.repre) & (df["Anio"] == 2026)].copy()
    data_2025 = df[(df["Repre"] == st.session_state.repre) & (df["Anio"] == 2025)].copy()

    # =====================================
    # HEADER APP STYLE
    # =====================================

    col1, col2 = st.columns([1, 6])

    with col1:
        if st.button("⬅"):
            st.session_state.page = "selector"
            st.rerun()

    with col2:
        st.markdown(f"### {st.session_state.repre}")

    # =====================================
    # KPI YTD
    # =====================================

    mes_actual = datetime.now().month

    data_2026["Mes"] = pd.to_numeric(data_2026["Mes"], errors="coerce")
    data_2025["Mes"] = pd.to_numeric(data_2025["Mes"], errors="coerce")

    real_ytd = data_2026.loc[data_2026["Mes"] <= mes_actual, "Real"].sum()
    le1_ytd = data_2026.loc[data_2026["Mes"] <= mes_actual, "LE1"].sum()
    ly_ytd = data_2025.loc[data_2025["Mes"] <= mes_actual, "Real"].sum()

    diff_le1 = real_ytd - le1_ytd
    diff_ly = real_ytd - ly_ytd

    def fmt(v):
        icon = "▲" if v > 0 else "▼" if v < 0 else "●"
        color = "#16A34A" if v > 0 else "#D9534F" if v < 0 else "#6B7280"
        return f"<span style='color:{color};font-weight:600'>{icon} {v:,.0f}</span>"

    # KPI CARD MOBILE
    card_html = f"""
    <div style="
        font-family:Arial;
        background:white;
        border:1px solid #E5E7EB;
        border-radius:14px;
        padding:10px;
        width:100%;
    ">

        <div style="font-size:11px;color:#888;">
            Volumen YTD
        </div>

        <div style="font-size:34px;font-weight:bold;color:#1D4ED8;">
            {real_ytd:,.0f}
        </div>

        <div style="font-size:12px;margin-top:4px;">
            LE1: {le1_ytd:,.0f} {fmt(diff_le1)}
        </div>

        <div style="font-size:12px;">
            2025: {ly_ytd:,.0f} {fmt(diff_ly)}
        </div>

    </div>
    """

    components.html(card_html, height=150)

    # =====================================
    # TÍTULO LIMPIO
    # =====================================

    st.markdown("### Evolución mensual")

    # =====================================
    # TENDENCIA
    # =====================================

    meses_map = {
        1:"Ene",2:"Feb",3:"Mar",4:"Abr",
        5:"May",6:"Jun",7:"Jul",8:"Ago",
        9:"Sep",10:"Oct",11:"Nov",12:"Dic"
    }

    t2026 = data_2026.groupby("Mes", as_index=False)[["Real","LE1"]].sum()
    t2025 = data_2025.groupby("Mes", as_index=False)[["Real"]].sum().rename(columns={"Real":"Real_2025"})

    tendencia = pd.DataFrame({"Mes": range(1,13)})
    tendencia = tendencia.merge(t2026, on="Mes", how="left").merge(t2025, on="Mes", how="left").fillna(0)

    tendencia["Mes_txt"] = tendencia["Mes"].map(meses_map)

    tendencia["Real_k"] = tendencia["Real"] / 1000
    tendencia["LE1_k"] = tendencia["LE1"] / 1000
    tendencia["LY_k"] = tendencia["Real_2025"] / 1000

    # cortar futuro
    tendencia.loc[tendencia["Mes"] > mes_actual, "Real_k"] = np.nan

    chart = alt.Chart(tendencia).mark_line().encode(
        x=alt.X("Mes_txt:N", sort=list(meses_map.values()), axis=alt.Axis(title=None)),
        y=alt.Y("Real_k:Q", axis=alt.Axis(title="(K)")),
        color=alt.value("#1D4ED8")
    ) + alt.Chart(tendencia).mark_line(strokeDash=[5,5]).encode(
        x="Mes_txt:N",
        y="LE1_k:Q",
        color=alt.value("#16A34A")
    ) + alt.Chart(tendencia).mark_line(strokeDash=[2,2]).encode(
        x="Mes_txt:N",
        y="LY_k:Q",
        color=alt.value("#999999")
    )

    st.altair_chart(chart, use_container_width=True)