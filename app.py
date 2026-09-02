import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# ==========================================
# 1. CONFIGURACIÓN DE PÁGINA Y ESTILOS
# ==========================================
st.set_page_config(
    page_title="Panel de Control de Afluencia Diaria de Visitantes",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados para mejorar el diseño UX/UI
st.markdown("""
    <style>
        .main-header {
            font-size: 2.2rem;
            font-weight: 700;
            color: #1E293B;
            margin-bottom: 0px;
        }
        .sub-header {
            font-size: 1.05rem;
            color: #64748B;
            margin-bottom: 25px;
        }
        div[data-testid="metric-container"] {
            background-color: #F8FAFC;
            border: 1px solid #E2E8F0;
            padding: 15px 20px;
            border-radius: 10px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        }
        div[data-testid="metric-container"] label {
            color: #475569 !important;
            font-size: 0.85rem !important;
            font-weight: 600 !important;
        }
        div[data-testid="metric-container"] [data-testid="stMetricValue"] {
            color: #0F172A !important;
            font-size: 1.8rem !important;
            font-weight: 700 !important;
        }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. CARGA Y PROCESAMIENTO DE DATOS
# ==========================================
@st.cache_data
def load_data() -> pd.DataFrame:
    # Datos sintéticos estructurados cubriendo exactamente los 29 registros (2025-12-24 a 2026-01-21)
    # Incluyendo exactamente los valores del sample_data
    known_data = {
        "2025-12-24": 14,
        "2025-12-25": 10,
        "2025-12-26": 22,
        "2025-12-27": 28,
        "2025-12-28": 25,
        "2025-12-29": 30,
        "2025-12-30": 35,
        "2025-12-31": 18,
        "2026-01-01": 14,
        "2026-01-02": 26,
        "2026-01-03": 32,
        "2026-01-04": 29,
        "2026-01-05": 33,
        "2026-01-06": 16,
        "2026-01-07": 21,
        "2026-01-08": 19,
        "2026-01-09": 24,
        "2026-01-10": 27,
        "2026-01-11": 15,
        "2026-01-12": 8,
        "2026-01-13": 17,
        "2026-01-14": 20,
        "2026-01-15": 22,
        "2026-01-16": 25,
        "2026-01-17": 29,
        "2026-01-18": 18,
        "2026-01-19": 21,
        "2026-01-20": 24,
        "2026-01-21": 31
    }
    
    dates = pd.date_range(start="2025-12-24", end="2026-01-21", freq="D")
    data_list = [{"Fecha": d.strftime("%Y-%m-%d"), "Visitantes": known_data.get(d.strftime("%Y-%m-%d"), 20)} for d in dates]
    
    df = pd.DataFrame(data_list)
    df["Fecha"] = pd.to_datetime(df["Fecha"])
    
    # Enriquecimiento de datos
    dias_semana_map = {
        0: "Lunes", 1: "Martes", 2: "Miércoles", 3: "Jueves",
        4: "Viernes", 5: "Sábado", 6: "Domingo"
    }
    df["Día_Num"] = df["Fecha"].dt.dayofweek
    df["Día_Semana"] = df["Día_Num"].map(dias_semana_map)
    df["Tipo_Dia"] = df["Día_Num"].apply(
        lambda x: "Fines de Semana (Sábado y Domingo)" if x >= 5 else "Días Laborales (Lunes a Viernes)"
    )
    
    return df

df_raw = load_data()

# ==========================================
# 3. BARRA LATERAL (FILTROS Y CONTROLES)
# ==========================================
st.sidebar.title("⚙️ Filtros y Parámetros")
st.sidebar.markdown("Personalice los criterios para segmentar el tráfico diario.")

# Filtro de Fechas
min_date = df_raw["Fecha"].min().date()
max_date = df_raw["Fecha"].max().date()

date_range = st.sidebar.date_input(
    "Rango de Fechas:",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Validación de selección de rango
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

# Filtro por Tipo de Día
tipos_disponibles = [
    "Días Laborales (Lunes a Viernes)",
    "Fines de Semana (Sábado y Domingo)"
]
selected_tipos = st.sidebar.multiselect(
    "Tipo de Día:",
    options=tipos_disponibles,
    default=tipos_disponibles
)

# Controles de Suavizado (Media Móvil)
st.sidebar.markdown("---")
st.sidebar.subheader("📈 Suavizado de Tendencia")
enable_ma = st.sidebar.checkbox("Activar Media Móvil", value=True)
ma_window = 3
if enable_ma:
    ma_window = st.sidebar.slider("Ventana de Media Móvil (Días):", min_value=2, max_value=7, value=3)

# Aplicar Filtros
df_filtered = df_raw[
    (df_raw["Fecha"].dt.date >= start_date) &
    (df_raw["Fecha"].dt.date <= end_date) &
    (df_raw["Tipo_Dia"].isin(selected_tipos))
].copy()

# Ordenar por fecha para cálculos de series temporales
df_filtered = df_filtered.sort_values("Fecha").reset_index(drop=True)

if enable_ma and not df_filtered.empty:
    df_filtered["Media_Movil"] = df_filtered["Visitantes"].rolling(window=ma_window, min_periods=1).mean().round(1)

# ==========================================
# 4. ENCABEZADO Y KPIS
# ==========================================
st.markdown('<p class="main-header">Panel de Control de Afluencia Diaria de Visitantes</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Monitoreo del tráfico diario, detección de picos de asistencia y análisis de patrones de comportamiento semanal.</p>', unsafe_allow_html=True)

if df_filtered.empty:
    st.warning("⚠️ No existen registros para los filtros seleccionados. Por favor, ajuste el rango de fechas o el tipo de día.")
    st.stop()

# Cálculos de Métricas Clave
total_visitantes = df_filtered["Visitantes"].sum()
promedio_diario = df_filtered["Visitantes"].mean()

idx_max = df_filtered["Visitantes"].idxmax()
max_row = df_filtered.loc[idx_max]
max_val = max_row["Visitantes"]
max_date_str = max_row["Fecha"].strftime("%d/%m/%Y")

idx_min = df_filtered["Visitantes"].idxmin()
min_row = df_filtered.loc[idx_min]
min_val = min_row["Visitantes"]
min_date_str = min_row["Fecha"].strftime("%d/%m/%Y")

# Render de Métricas (4 Columnas)
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.metric(
        label="Total Visitantes Acumulados",
        value=f"{total_visitantes:,}".replace(",", ".")
    )

with kpi2:
    st.metric(
        label="Promedio Diario",
        value=f"{promedio_diario:.1f}"
    )

with kpi3:
    st.metric(
        label="Pico Máximo de Afluencia",
        value=f"{max_val} visitantes",
        delta=f"Fecha: {max_date_str}",
        delta_color="off"
    )

with kpi4:
    st.metric(
        label="Día de Menor Afluencia",
        value=f"{min_val} visitantes",
        delta=f"Fecha: {min_date_str}",
        delta_color="off"
    )

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# 5. VISUALIZACIONES PRINCIPALES
# ==========================================

# --- Sección 1: Análisis Temporal y Tendencias (Ancho Completo) ---
st.subheader("1. Serie Temporal y Tendencia de Visitas")

fig_main = go.Figure()

# Curva principal con área sombreada
fig_main.add_trace(go.Scatter(
    x=df_filtered["Fecha"],
    y=df_filtered["Visitantes"],
    name="Visitantes Diarios",
    mode="lines+markers",
    line=dict(color="#2563EB", width=2.5),
    marker=dict(size=6, color="#1D4ED8"),
    fill="tozeroy",
    fillcolor="rgba(37, 99, 235, 0.08)",
    hovertemplate="<b>Fecha:</b> %{x|%d/%m/%Y}<br><b>Visitantes:</b> %{y}<extra></extra>"
))

# Media móvil opcional
if enable_ma:
    fig_main.add_trace(go.Scatter(
        x=df_filtered["Fecha"],
        y=df_filtered["Media_Movil"],
        name=f"Media Móvil ({ma_window}d)",
        mode="lines",
        line=dict(color="#F97316", width=2, dash="dot"),
        hovertemplate=f"<b>Media Móvil ({ma_window}d):</b> %{{y:.1f}}<extra></extra>"
    ))

# Días festivos destacados
festivos = {
    "2025-12-25": "Navidad 🎄",
    "2026-01-01": "Año Nuevo 🎆",
    "2026-01-06": "Reyes Magos 👑"
}

for fecha_festivo, nombre_festivo in festivos.items():
    sub_fest = df_filtered[df_filtered["Fecha"].dt.strftime("%Y-%m-%d") == fecha_festivo]
    if not sub_fest.empty:
        val_fest = sub_fest["Visitantes"].values[0]
        fig_main.add_trace(go.Scatter(
            x=[sub_fest["Fecha"].values[0]],
            y=[val_fest],
            mode="markers+text",
            marker=dict(size=11, color="#DC2626", symbol="diamond"),
            name=f"Festivo: {nombre_festivo}",
            text=[nombre_festivo],
            textposition="top center",
            hovertemplate=f"<b>{nombre_festivo}</b><br>Fecha: %{{x|%d/%m/%Y}}<br>Visitantes: %{{y}}<extra></extra>",
            showlegend=False
        ))

fig_main.update_layout(
    template="plotly_white",
    height=420,
    margin=dict(l=20, r=20, t=30, b=20),
    hovermode="x unified",
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    ),
    xaxis=dict(
        title="Fecha",
        showgrid=True,
        gridcolor="#F1F5F9"
    ),
    yaxis=dict(
        title="Cantidad de Visitantes",
        showgrid=True,
        gridcolor="#F1F5F9"
    )
)

st.plotly_chart(fig_main, use_container_width=True)

# --- Sección 2: Análisis de Comportamiento y Distribución (2 Columnas) ---
st.subheader("2. Comportamiento Semanal y Crecimiento Acumulado")
col_chart_a, col_chart_b = st.columns(2)

orden_dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

# Columna A: Promedio por Día de la Semana
with col_chart_a:
    df_dow = df_filtered.groupby("Día_Semana", as_index=False)["Visitantes"].mean()
    df_dow["Día_Semana"] = pd.Categorical(df_dow["Día_Semana"], categories=orden_dias, ordered=True)
    df_dow = df_dow.sort_values("Día_Semana").dropna()

    fig_bar = px.bar(
        df_dow,
        x="Día_Semana",
        y="Visitantes",
        title="Promedio de Visitantes por Día de la Semana",
        labels={"Día_Semana": "Día", "Visitantes": "Promedio de Visitas"},
        color="Visitantes",
        color_continuous_scale="Blues",
        text_auto=".1f"
    )
    fig_bar.update_layout(
        template="plotly_white",
        height=380,
        margin=dict(l=20, r=20, t=50, b=20),
        coloraxis_showscale=False
    )
    fig_bar.update_traces(
        textfont_size=12,
        textposition="outside",
        cliponaxis=False
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# Columna B: Crecimiento Acumulado del Período
with col_chart_b:
    df_cum = df_filtered.copy()
    df_cum["Acumulado"] = df_cum["Visitantes"].cumsum()

    fig_cum = go.Figure()
    fig_cum.add_trace(go.Scatter(
        x=df_cum["Fecha"],
        y=df_cum["Acumulado"],
        mode="lines+markers",
        line=dict(color="#0D9488", width=2.5),
        fill="tozeroy",
        fillcolor="rgba(13, 148, 136, 0.1)",
        hovertemplate="<b>Fecha:</b> %{x|%d/%m/%Y}<br><b>Total Acumulado:</b> %{y}<extra></extra>"
    ))
    fig_cum.update_layout(
        template="plotly_white",
        title="Crecimiento Acumulado de Visitantes",
        height=380,
        margin=dict(l=20, r=20, t=50, b=20),
        xaxis=dict(title="Fecha", showgrid=True, gridcolor="#F1F5F9"),
        yaxis=dict(title="Visitantes Acumulados", showgrid=True, gridcolor="#F1F5F9")
    )
    st.plotly_chart(fig_cum, use_container_width=True)

# ==========================================
# 6. SECCIÓN DE DATOS DETALLADOS (EXPANDER)
# ==========================================
with st.expander("📄 Ver Vista de Datos Detallada y Exportación", expanded=False):
    st.markdown("Consulte los registros correspondientes al período y filtros aplicados:")
    
    df_display = df_filtered.copy()
    df_display["Fecha_Formateada"] = df_display["Fecha"].dt.strftime("%Y-%m-%d")
    
    columnas_mostrar = ["Fecha_Formateada", "Día_Semana", "Tipo_Dia", "Visitantes"]
    if enable_ma and "Media_Movil" in df_display.columns:
        columnas_mostrar.append("Media_Movil")

    df_export = df_display[columnas_mostrar].rename(columns={
        "Fecha_Formateada": "Fecha",
        "Día_Semana": "Día de la Semana",
        "Tipo_Dia": "Tipo de Día",
        "Media_Movil": f"Media Móvil ({ma_window}d)"
    })

    st.dataframe(
        df_export,
        use_container_width=True,
        hide_index=True
    )

    # Descarga CSV
    csv_data = df_export.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Descargar Datos Filtrados (CSV)",
        data=csv_data,
        file_name=f"afluencia_visitantes_{start_date}_{end_date}.csv",
        mime="text/csv"
    )