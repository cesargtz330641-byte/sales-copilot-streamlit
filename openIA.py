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
# PANTALLA 1
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
# PANTALLA 2
# =========================

if st.session_state.page == "dashboard":

    data = df[
        (df["Repre"] == st.session_state.repre)
        & (df["Anio"] == 2026)
    ].copy()

    st.title(f"📊 {st.session_state.repre}")

    if st.button("⬅ Volver"):
        st.session_state.page = "selector"
        st.rerun()

    # =========================
    # CALCULOS YTD
    # =========================

    venta_ytd = data["Venta"].sum()

    obj1_ytd = data["Objetivo 1"].sum()
    obj2_ytd = data["Objetivo 2"].sum()

    gap1 = venta_ytd - obj1_ytd
    gap2 = venta_ytd - obj2_ytd

    pct1 = 0 if obj1_ytd == 0 else (gap1 / obj1_ytd) * 100
    pct2 = 0 if obj2_ytd == 0 else (gap2 / obj2_ytd) * 100

    # =========================
    # TARJETA PRINCIPAL
    # =========================

    with st.container(border=True):

        st.caption("Volumen YTD 2026")

        st.metric(
            label="",
            value=f"{venta_ytd:,.0f}"
        )

        st.divider()

        c1, c2, c3 = st.columns([1.2, 1, 0.7])

        c1.write("Obj 1")
        c2.write(f"{gap1:,.0f}")
        c3.write(f"{pct1:.0f}%")

        c1.caption(f"Meta: {obj1_ytd:,.0f}")

        st.divider()

        c1, c2, c3 = st.columns([1.2, 1, 0.7])

        c1.write("Obj 2")
        c2.write(f"{gap2:,.0f}")
        c3.write(f"{pct2:.0f}%")

        c1.caption(f"Meta: {obj2_ytd:,.0f}")

    # =========================
    # TENDENCIA
    # =========================

    st.subheader("📈 Tendencia")

    chart = (
        data.groupby("Mes")[["Venta", "Objetivo 1"]]
        .sum()
        .sort_index()
    )

    st.line_chart(chart)