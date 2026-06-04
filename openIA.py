import streamlit as st
import streamlit.components.v1 as components
import pandas as pd

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

password = st.text_input(
    "Ingresa la contraseña",
    type="password"
)

if password != PASSWORD:
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
# FUNCIONES
# =====================================

def short_number(x):

    if abs(x) >= 1_000_000:
        return f"{x/1_000_000:.1f}M"

    if abs(x) >= 1_000:
        return f"{x/1_000:.1f}K"

    return f"{x:,.0f}"

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

    # =====================================
    # TARJETA MOBILE
    # =====================================

    card_html = f"""
    <div style="
        font-family: Arial, sans-serif;
        background:white;
        border:1px solid #E5E7EB;
        border-radius:24px;
        padding:16px;
        margin:0;
    ">

        <div style="
            font-size:16px;
            color:#666;
        ">
            {st.session_state.repre}
        </div>

        <div style="
            font-size:12px;
            color:#999;
            margin-top:2px;
        ">
            Volumen YTD 2026
        </div>

        <div style="
            font-size:58px;
            font-weight:bold;
            color:#1D4ED8;
            line-height:1;
            margin-top:8px;
            margin-bottom:12px;
        ">
            {short_number(venta)}
        </div>

        <div style="
            display:flex;
            justify-content:space-between;
            font-size:15px;
            margin-bottom:6px;
        ">
            <span><b>O1</b> {short_number(obj1)}</span>
            <span style="color:{color1};font-weight:bold;">
                {short_number(gap1)}
            </span>
            <span>{pct1:.0f}%</span>
        </div>

        <div style="
            display:flex;
            justify-content:space-between;
            font-size:15px;
        ">
            <span><b>O2</b> {short_number(obj2)}</span>
            <span style="color:{color2};font-weight:bold;">
                {short_number(gap2)}
            </span>
            <span>{pct2:.0f}%</span>
        </div>

    </div>
    """

    components.html(
        card_html,
        height=180,
        scrolling=False
    )

    st.write("")

    # =====================================
    # TENDENCIA
    # =====================================

    tendencia = (
        data.groupby("Mes")[["Venta", "Objetivo 1"]]
        .sum()
        .sort_index()
    )

    st.line_chart(
        tendencia,
        use_container_width=True
    )