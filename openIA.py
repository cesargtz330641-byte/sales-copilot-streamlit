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
# DATOS
# =========================

df = pd.read_excel("ChatBox.xlsx")

# =========================
# SESSION
# =========================

if "page" not in st.session_state:
    st.session_state.page = "selector"

if "repre" not in st.session_state:
    st.session_state.repre = None

# =========================
# SELECTOR
# =========================

if st.session_state.page == "selector":

    st.title("📱 Sales Mobile Pro")

    reps = sorted(df["Repre"].dropna().unique())

    st.write("Selecciona un representado:")

    for r in reps:
        if st.button(
            r,
            use_container_width=True
        ):
            st.session_state.repre = r
            st.session_state.page = "dashboard"
            st.rerun()

# =========================
# DASHBOARD
# =========================

if st.session_state.page == "dashboard":

    data = df[
        (df["Repre"] == st.session_state.repre)
        & (df["Anio"] == 2026)
    ].copy()

    if st.button("⬅ Volver"):
        st.session_state.page = "selector"
        st.rerun()

    venta_ytd = data["Venta"].sum()

    obj1 = data["Objetivo 1"].sum()
    obj2 = data["Objetivo 2"].sum()

    gap1 = venta_ytd - obj1
    gap2 = venta_ytd - obj2

    pct1 = 0 if obj1 == 0 else (gap1 / obj1) * 100
    pct2 = 0 if obj2 == 0 else (gap2 / obj2) * 100

    color1 = "#D9534F" if gap1 < 0 else "#28A745"
    color2 = "#D9534F" if gap2 < 0 else "#28A745"

    st.markdown(
        f"""
        <div style="
            border:2px solid #d9d9d9;
            border-radius:28px;
            padding:18px;
            margin-top:5px;
            margin-bottom:10px;
            background-color:white;
        ">

            <div style="
                font-size:16px;
                color:#666;
                margin-bottom:2px;
            ">
                {st.session_state.repre}
            </div>

            <div style="
                font-size:14px;
                color:#999;
            ">
                Volumen YTD 2026
            </div>

            <div style="
                font-size:52px;
                font-weight:700;
                color:#1E40AF;
                line-height:1;
                margin-top:8px;
                margin-bottom:18px;
            ">
                {venta_ytd:,.0f}
            </div>

            <div style="
                display:flex;
                justify-content:space-between;
                font-size:15px;
                margin-bottom:4px;
            ">
                <span><b>Obj 1</b> {obj1:,.0f}</span>
                <span style="color:{color1};">
                    {gap1:,.0f}
                </span>
                <span>
                    {pct1:.0f}%
                </span>
            </div>

            <div style="
                display:flex;
                justify-content:space-between;
                font-size:15px;
            ">
                <span><b>Obj 2</b> {obj2:,.0f}</span>
                <span style="color:{color2};">
                    {gap2:,.0f}
                </span>
                <span>
                    {pct2:.0f}%
                </span>
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    # =========================
    # TENDENCIA
    # =========================

    st.subheader("📈 Tendencia")

    chart = (
        data.groupby("Mes")[["Venta", "Objetivo 1"]]
        .sum()
        .sort_index()
    )

    st.line_chart(
        chart,
        use_container_width=True
    )