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
    st.write("Selecciona un representado:")

    reps = sorted(df["Repre"].dropna().unique())

    for r in reps:
        if st.button(
            f"📊 {r}",
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
        (df["Repre"] == st.session_state.repre) &
        (df["Anio"] == 2026)
    ].copy()

    if st.button("⬅ Volver"):
        st.session_state.page = "selector"
        st.rerun()

    # =========================
    # CALCULOS
    # =========================

    venta_ytd = data["Venta"].sum()

    obj1_ytd = data["Objetivo 1"].sum()
    obj2_ytd = data["Objetivo 2"].sum()

    gap1 = venta_ytd - obj1_ytd
    gap2 = venta_ytd - obj2_ytd

    pct1 = 0 if obj1_ytd == 0 else (gap1 / obj1_ytd) * 100
    pct2 = 0 if obj2_ytd == 0 else (gap2 / obj2_ytd) * 100

    # =========================
    # HEADER
    # =========================

    st.subheader(st.session_state.repre)

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

        col1, col2, col3 = st.columns([1.2, 1, 0.8])

        col1.write("Obj1")
        col2.write(f"{gap1/1000:,.0f}k")
        col3.write(f"{pct1:.0f}%")

        col1.caption(f"Meta {obj1_ytd:,.0f}")

        col1, col2, col3 = st.columns([1.2, 1, 0.8])

        col1.write("Obj2")
        col2.write(f"{gap2/1000:,.0f}k")
        col3.write(f"{pct2:.0f}%")

        col1.caption(f"Meta {obj2_ytd:,.0f}")

    # =========================
    # TENDENCIA
    # =========================

    st.subheader("📈 Tendencia")

    tendencia = (
        data.groupby("Mes")[["Venta", "Objetivo 1"]]
        .sum()
        .sort_index()
    )

    st.line_chart(
        tendencia,
        use_container_width=True
    )