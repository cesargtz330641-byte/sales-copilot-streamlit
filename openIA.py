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
# CSS MOBILE
# =====================================

st.markdown("""
<style>

/* Reduce espacios de Streamlit */
.block-container {
    padding-top: 1rem;
    padding-bottom: 1rem;
}

/* Tarjeta */
.card {
    background: white;
    border: 1px solid #E5E7EB;
    border-radius: 24px;
    padding: 16px;
    margin-bottom: 12px;
}

/* Nombre representante */
.rep {
    font-size: 16px;
    color: #666;
    margin-bottom: 0px;
}

/* Subtitulo */
.sub {
    font-size: 12px;
    color: #999;
    margin-bottom: 6px;
}

/* Numero principal */
.venta {
    font-size: 56px;
    font-weight: 700;
    color: #1D4ED8;
    line-height: 1;
    margin-bottom: 10px;
}

/* Filas de objetivos */
.row {
    display: flex;
    justify-content: space-between;
    font-size: 15px;
    padding-top: 4px;
    padding-bottom: 4px;
}

.negativo {
    color: #DC2626;
    font-weight: 600;
}

.positivo {
    color: #16A34A;
    font-weight: 600;
}

</style>
""", unsafe_allow_html=True)

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
        (df["Repre"] == st.session_state.repre) &
        (df["Anio"] == 2026)
    ].copy()

    if st.button("⬅ Volver"):
        st.session_state.page = "selector"
        st.rerun()

    # =====================================
    # KPIs
    # =====================================

    venta = data["Venta"].sum()

    obj1 = data["Objetivo 1"].sum()
    obj2 = data["Objetivo 2"].sum()

    gap1 = venta - obj1
    gap2 = venta - obj2

    pct1 = 0 if obj1 == 0 else (gap1 / obj1) * 100
    pct2 = 0 if obj2 == 0 else (gap2 / obj2) * 100

    clase1 = "positivo" if gap1 >= 0 else "negativo"
    clase2 = "positivo" if gap2 >= 0 else "negativo"

    # =====================================
    # TARJETA
    # =====================================

    st.markdown(f"""
    <div class="card">

        <div class="rep">
            {st.session_state.repre}
        </div>

        <div class="sub">
            Volumen YTD 2026
        </div>

        <div class="venta">
            {short_number(venta)}
        </div>

        <div class="row">
            <span><b>O1</b> {short_number(obj1)}</span>
            <span class="{clase1}">
                {short_number(gap1)}
            </span>
            <span>
                {pct1:.0f}%
            </span>
        </div>

        <div class="row">
            <span><b>O2</b> {short_number(obj2)}</span>
            <span class="{clase2}">
                {short_number(gap2)}
            </span>
            <span>
                {pct2:.0f}%
            </span>
        </div>

    </div>
    """, unsafe_allow_html=True)

    # =====================================
    # TENDENCIA
    # =====================================

    tendencia = (
        data
        .groupby("Mes")[["Venta", "Objetivo 1"]]
        .sum()
        .sort_index()
    )

    st.line_chart(
        tendencia,
        use_container_width=True
    )