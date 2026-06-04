import streamlit as st
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

def format_short(num):

    abs_num = abs(num)

    if abs_num >= 1_000_000:
        return f"{num/1_000_000:.1f}M"

    if abs_num >= 1_000:
        return f"{num/1_000:.1f}K"

    return f"{num:,.0f}"


# =====================================
# SELECTOR
# =====================================

if st.session_state.page == "selector":

    st.title("📱 Sales Mobile Pro")

    st.write("Selecciona un representado")

    reps = sorted(
        df["Repre"]
        .dropna()
        .unique()
    )

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

    pct1 = 0 if obj1 == 0 else gap1 / obj1 * 100
    pct2 = 0 if obj2 == 0 else gap2 / obj2 * 100

    color1 = "#D9534F" if gap1 < 0 else "#28A745"
    color2 = "#D9534F" if gap2 < 0 else "#28A745"

    # =====================================
    # TARJETA
    # =====================================

    tarjeta = f"""
    <div style="
        background:white;
        border:1px solid #E5E7EB;
        border-radius:30px;
        padding:18px;
        margin-bottom:15px;
        box-shadow:0 2px 8px rgba(0,0,0,.05);
    ">

        <div style="
            font-size:15px;
            color:#666;
            margin-bottom:2px;
        ">
            {st.session_state.repre}
        </div>

        <div style="
            font-size:12px;
            color:#999;
        ">
            Volumen YTD 2026
        </div>

        <div style="
            font-size:56px;
            font-weight:700;
            color:#1D4ED8;
            line-height:1;
            margin-top:6px;
            margin-bottom:14px;
        ">
            {format_short(venta)}
        </div>

        <table width="100%" style="
            border-collapse:collapse;
            font-size:15px;
        ">

            <tr>
                <td style="padding:4px 0;">
                    <b>Obj 1</b>
                </td>

                <td align="right">
                    {format_short(obj1)}
                </td>

                <td align="right" style="
                    color:{color1};
                    font-weight:600;
                ">
                    {format_short(gap1)}
                </td>

                <td align="right">
                    {pct1:.0f}%
                </td>
            </tr>

            <tr>
                <td style="padding:4px 0;">
                    <b>Obj 2</b>
                </td>

                <td align="right">
                    {format_short(obj2)}
                </td>

                <td align="right" style="
                    color:{color2};
                    font-weight:600;
                ">
                    {format_short(gap2)}
                </td>

                <td align="right">
                    {pct2:.0f}%
                </td>
            </tr>

        </table>

    </div>
    """

    st.markdown(
        tarjeta,
        unsafe_allow_html=True
    )

    # =====================================
    # TENDENCIA
    # =====================================

    chart = (
        data
        .groupby("Mes")[["Venta", "Objetivo 1"]]
        .sum()
        .sort_index()
    )

    st.line_chart(
        chart,
        use_container_width=True
    )