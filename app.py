import datetime
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ==========================================
# CONFIGURACIÓN DE LA PÁGINA
# ==========================================
st.set_page_config(
    page_title="Dashboard de Tráfico y Afluencia Diaria",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==========================================
# GENERACIÓN / CARGA DE DATOS
# ==========================================
@st.cache_data
def load_data() -> pd.DataFrame:
    """Genera y estructura el conjunto de datos de 29 días según el esquema especificado."""
    date_range = pd.date_range(start="2025-12-24", end="2026-01-21", freq="D")
    
    # Mapeo de valores de muestra exactos
    known_samples = {
        "2026-01-21": 31,
        "2026-01-20": 28,
        "2026-01-12": 8,
        "2026-01-01": 14,
        "2025-12-30": 35,
        "2025-12-24": 14,
    }
    
    # Generación sintética determinista para el resto de días (rango 8 a 35)
    np.random.seed(42)
    synthetic_values = np.random.randint(10, 33, size=len(date_range))
    
    records = []
    for idx, dt in enumerate(date_range):
        date_str = dt.strftime("%Y-%m-%d")
        val = known_samples.get(date_str, int(synthetic_values[idx]))
        records.append({"Fecha": dt.date(), "Visitantes": val})
        
    df = pd.DataFrame(records)
    
    # Enriquecimiento temporal
    dias_espanol = {
        "Monday": "Lunes",
        "Tuesday": "Martes",
        "Wednesday": "Miércoles",
        "Thursday": "Jueves",
        "Friday": "Viernes",
        "Saturday": "Sábado",
        "Sunday": "Domingo",
    }
    df["Dia_Semana"] = df["Fecha"].apply(lambda d: dias_espanol[d.strftime("%A")])
    df["Dia_Num"] = df["Fecha"].apply(lambda d: d.weekday())  # 0=Lunes, 6=Domingo
    
    return df


df_raw = load_data()

# ==========================================
# BARRA LATERAL (FILTROS)
# ==========================================
st.sidebar.header("🎛️ Controles de Filtro")
st.sidebar.markdown("Personaliza los parámetros del análisis:")

# 1. Selector de Rango de Fechas
min_date = df_raw["Fecha"].min()
max_date = df_raw["Fecha"].max()

selected_dates = st.sidebar.date_input(
    "Periodo de Análisis:",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

# Validación de rango de fecha seleccionado
if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
    start_date, end_date = selected_dates
else:
    start_date, end_date = min_date, max_date

# 2. Filtro Multiselección por Día de la Semana
dias_ordenados = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
selected_days = st.sidebar.multiselect(
    "Días de la Semana:",
    options=dias_ordenados,
    default=dias_ordenados,
    help="Filtra para comparar días laborables vs. fines de semana.",
)

# 3. Umbral de Capacidad / Alerta
umbral_alerta = st.sidebar.slider(
    "Umbral de Capacidad / Alerta (Visitantes):",
    min_value=0,
    max_value=40,
    value=25,
    step=1,
    help="Línea de referencia visual para detectar saturación de capacidad.",
)

# Filtrado del DataFrame
df_filtered = df_raw[
    (df_raw["Fecha"] >= start_date)
    & (df_raw["Fecha"] <= end_date)
    & (df_raw["Dia_Semana"].isin(selected_days))
].copy()

# ==========================================
# ENCABEZADO Y CONTEXTO
# ==========================================
st.title("📈 Dashboard de Tráfico y Afluencia Diaria de Visitantes")
st.caption("Análisis temporal del flujo de visitas y detección de patrones de asistencia.")
st.markdown(
    """
    Herramienta visual ejecutiva diseñada para optimizar la toma de decisiones operativas, 
    gestión de dotación de personal y control de aforo diario.
    """
)
st.markdown("---")

# Verificación de datos tras filtros
if df_filtered.empty:
    st.warning("⚠️ No se encontraron registros con los filtros seleccionados. Por favor, ajusta los criterios en la barra lateral.")
    st.stop()

# ==========================================
# TARJETAS DE MÉTRICAS (KPIs)
# ==========================================
total_visitantes = df_filtered["Visitantes"].sum()
promedio_diario = df_filtered["Visitantes"].mean()

row_max = df_filtered.loc[df_filtered["Visitantes"].idxmax()]
max_visitantes = row_max["Visitantes"]
max_fecha = row_max["Fecha"].strftime("%d/%m/%Y")

row_min = df_filtered.loc[df_filtered["Visitantes"].idxmin()]
min_visitantes = row_min["Visitantes"]
min_fecha = row_min["Fecha"].strftime("%d/%m/%Y")

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.metric(
        label="Total de Visitantes",
        value=f"{total_visitantes:,}",
        help="Volumen acumulado de accesos en el periodo filtrado.",
    )

with kpi2:
    st.metric(
        label="Promedio Diario",
        value=f"{promedio_diario:.1f}",
        help="Media aritmética de visitantes por día.",
    )

with kpi3:
    st.metric(
        label="Pico Máximo de Afluencia",
        value=f"{max_visitantes} visitas",
        delta=f"Récord: {max_fecha}",
        delta_color="normal",
        help="Mayor afluencia registrada dentro del periodo.",
    )

with kpi4:
    st.metric(
        label="Mínimo Registrado",
        value=f"{min_visitantes} visitas",
        delta=f"Mínimo: {min_fecha}",
        delta_color="off",
        help="Menor concurrencia registrada en el periodo.",
    )

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# SECCIÓN A: EVOLUCIÓN TEMPORAL
# ==========================================
st.subheader("📅 Evolución Temporal del Tráfico Diario")

# Preparar orden cronológico
df_sorted = df_filtered.sort_values(by="Fecha").copy()
df_sorted["Fecha_Str"] = df_sorted["Fecha"].apply(lambda d: d.strftime("%Y-%m-%d"))

fig_timeline = go.Figure()

# Área y línea principal
fig_timeline.add_trace(
    go.Scatter(
        x=df_sorted["Fecha"],
        y=df_sorted["Visitantes"],
        mode="lines+markers",
        name="Visitantes",
        line=dict(color="#1f77b4", width=3),
        marker=dict(size=7, color="#0d47a1"),
        fill="tozeroy",
        fillcolor="rgba(31, 119, 180, 0.15)",
        customdata=np.stack((df_sorted["Dia_Semana"], df_sorted["Fecha_Str"]), axis=-1),
        hovertemplate="<b>Fecha:</b> %{customdata[1]} (%{customdata[0]})<br>"
                      + "<b>Visitantes:</b> %{y}<extra></extra>",
    )
)

# Línea de Promedio
fig_timeline.add_hline(
    y=promedio_diario,
    line_dash="dot",
    line_color="#ff7f0e",
    line_width=2,
    annotation_text=f"Promedio ({promedio_diario:.1f})",
    annotation_position="top right",
)

# Línea de Umbral de Capacidad / Alerta
fig_timeline.add_hline(
    y=umbral_alerta,
    line_dash="dash",
    line_color="#d62728",
    line_width=2,
    annotation_text=f"Umbral Alerta ({umbral_alerta})",
    annotation_position="bottom right",
)

fig_timeline.update_layout(
    height=400,
    margin=dict(l=20, r=20, t=30, b=20),
    xaxis_title="Fecha",
    yaxis_title="Cantidad de Visitantes",
    hovermode="x unified",
    template="plotly_white",
    yaxis=dict(range=[0, max(df_sorted["Visitantes"].max() + 5, umbral_alerta + 5)]),
)

st.plotly_chart(fig_timeline, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# SECCIÓN B: ANÁLISIS DE PATRONES Y DISTRIBUCIÓN
# ==========================================
col_b1, col_b2 = st.columns(2)

with col_b1:
    st.subheader("📊 Patrón de Afluencia por Día")
    
    # Agrupación por día de la semana manteniendo orden Lunes -> Domingo
    df_dow = (
        df_filtered.groupby(["Dia_Semana", "Dia_Num"])["Visitantes"]
        .mean()
        .reset_index()
        .sort_values(by="Dia_Num")
    )
    
    fig_bar = px.bar(
        df_dow,
        x="Dia_Semana",
        y="Visitantes",
        text_auto=".1f",
        labels={"Dia_Semana": "Día de la Semana", "Visitantes": "Promedio de Visitantes"},
        color="Visitantes",
        color_continuous_scale="Blues",
    )
    
    fig_bar.update_layout(
        height=380,
        margin=dict(l=20, r=20, t=30, b=20),
        xaxis_title="Día",
        yaxis_title="Promedio de Visitantes",
        coloraxis_showscale=False,
        template="plotly_white",
    )
    fig_bar.update_traces(
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>Promedio: %{y:.1f} visitantes<extra></extra>",
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with col_b2:
    st.subheader("📦 Distribución y Dispersión de Visitas")
    
    fig_box = go.Figure()
    
    # Boxplot con puntos (strip plot overlay)
    fig_box.add_trace(
        go.Box(
            y=df_filtered["Visitantes"],
            name="Afluencia",
            boxpoints="all",
            jitter=0.4,
            pointpos=-1.6,
            marker=dict(color="#2ca02c", size=7, opacity=0.7),
            line=dict(color="#1b5e20", width=2),
            fillcolor="rgba(44, 160, 44, 0.2)",
            customdata=df_filtered["Fecha"].apply(lambda d: d.strftime("%Y-%m-%d")),
            hovertemplate="<b>Fecha:</b> %{customdata}<br><b>Visitantes:</b> %{y}<extra></extra>",
        )
    )
    
    fig_box.update_layout(
        height=380,
        margin=dict(l=20, r=20, t=30, b=20),
        yaxis_title="Conteo Diario de Visitantes",
        template="plotly_white",
        showlegend=False,
        yaxis=dict(range=[0, max(df_filtered["Visitantes"].max() + 5, 40)]),
    )
    st.plotly_chart(fig_box, use_container_width=True)

# ==========================================
# TABLA DE DETALLE Y DESCARGA
# ==========================================
with st.expander("📄 Ver Detalle de Registros Diarios", expanded=False):
    st.markdown("A continuación se muestra el listado cronológico inverso de los registros filtrados:")
    
    # Preparación de tabla para visualización
    df_display = (
        df_filtered[["Fecha", "Dia_Semana", "Visitantes"]]
        .sort_values(by="Fecha", ascending=False)
        .reset_index(drop=True)
    )
    
    df_display["Estado_Capacidad"] = df_display["Visitantes"].apply(
        lambda x: "🚨 Alerta/Saturado" if x >= umbral_alerta else "✅ Normal"
    )
    
    # Configuración de visualización de tabla interactiva
    st.dataframe(
        df_display.style.format({"Fecha": lambda d: d.strftime("%Y-%m-%d")}),
        use_container_width=True,
        hide_index=True,
    )
    
    # Botón de Descarga CSV
    csv_data = df_display.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Descargar Datos Filtrados (CSV)",
        data=csv_data,
        file_name=f"reporte_afluencia_{datetime.date.today()}.csv",
        mime="text/csv",
    )