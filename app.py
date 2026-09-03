import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import matplotlib
import datetime

# RULE 1: First Streamlit call must be set_page_config
st.set_page_config(
    page_title="Reporte de Tráfico de Visitantes ST_B2C",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# RULE 2: In-memory dataset
raw_data = [
    { "fecha": "2026-01-21", "visitantes": 31 },
    { "fecha": "2026-01-20", "visitantes": 28 },
    { "fecha": "2026-01-19", "visitantes": 26 },
    { "fecha": "2026-01-18", "visitantes": 25 },
    { "fecha": "2026-01-17", "visitantes": 27 },
    { "fecha": "2026-01-16", "visitantes": 18 },
    { "fecha": "2026-01-15", "visitantes": 22 },
    { "fecha": "2026-01-14", "visitantes": 15 },
    { "fecha": "2026-01-13", "visitantes": 15 },
    { "fecha": "2026-01-12", "visitantes": 8 },
    { "fecha": "2026-01-11", "visitantes": 9 },
    { "fecha": "2026-01-10", "visitantes": 15 },
    { "fecha": "2026-01-09", "visitantes": 16 },
    { "fecha": "2026-01-08", "visitantes": 12 },
    { "fecha": "2026-01-07", "visitantes": 16 },
    { "fecha": "2026-01-06", "visitantes": 14 },
    { "fecha": "2026-01-05", "visitantes": 24 },
    { "fecha": "2026-01-04", "visitantes": 15 },
    { "fecha": "2026-01-03", "visitantes": 8 },
    { "fecha": "2026-01-02", "visitantes": 15 },
    { "fecha": "2026-01-01", "visitantes": 14 },
    { "fecha": "2025-12-31", "visitantes": 10 },
    { "fecha": "2025-12-30", "visitantes": 35 },
    { "fecha": "2025-12-29", "visitantes": 13 },
    { "fecha": "2025-12-28", "visitantes": 13 },
    { "fecha": "2025-12-27", "visitantes": 26 },
    { "fecha": "2025-12-26", "visitantes": 26 },
    { "fecha": "2025-12-25", "visitantes": 12 },
    { "fecha": "2025-12-24", "visitantes": 14 }
]
df_default = pd.DataFrame(raw_data)

# RULE 3: Optional file uploader in Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/000000/dashboard.png", width=80)
    st.header("Carga de Archivos")
    uploaded_file = st.file_uploader("Sube un nuevo archivo de tráfico (XLSX o CSV)", type=["xlsx", "csv"])

# Determine DataFrame to use
if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        st.sidebar.success("¡Datos cargados con éxito!")
    except Exception as e:
        st.sidebar.error(f"Error al cargar archivo: {e}")
        df = df_default.copy()
else:
    df = df_default.copy()

# RULE 6: Defensive typing and renaming helper
cols_lower = {col.lower(): col for col in df.columns}
if 'fecha' not in df.columns and 'date' in cols_lower:
    df = df.rename(columns={cols_lower['date']: 'fecha'})
if 'visitantes' not in df.columns and 'visitors' in cols_lower:
    df = df.rename(columns={cols_lower['visitors']: 'visitantes'})

# Ensure existence and convert types defensively
if 'fecha' in df.columns:
    df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
else:
    st.error("Error: No se encontró la columna 'fecha' en los datos.")
    st.stop()

if 'visitantes' in df.columns:
    df['visitantes'] = pd.to_numeric(df['visitantes'], errors='coerce')
else:
    st.error("Error: No se encontró la columna 'visitantes' en los datos.")
    st.stop()

# Drop any potential parsing nulls
df = df.dropna(subset=['fecha', 'visitantes'])
df = df.sort_values(by='fecha')

# Dynamic calculations for sidebar controls
df['dia_semana'] = df['fecha'].dt.day_name()
days_translation = {
    'Monday': 'Lunes', 'Tuesday': 'Martes', 'Wednesday': 'Miércoles',
    'Thursday': 'Jueves', 'Friday': 'Viernes', 'Saturday': 'Sábado', 'Sunday': 'Domingo'
}
df['dia_semana_es'] = df['dia_semana'].map(days_translation)

min_date_val = df['fecha'].min().to_pydatetime() if not df.empty else datetime.date(2025, 12, 24)
max_date_val = df['fecha'].max().to_pydatetime() if not df.empty else datetime.date(2026, 1, 21)
min_traffic_val = int(df['visitantes'].min()) if not df.empty else 8
max_traffic_val = int(df['visitantes'].max()) if not df.empty else 35

# Sidebar filter elements
with st.sidebar:
    st.markdown("---")
    st.header("Filtros de Control")

    date_range = st.date_input(
        "Rango de Análisis",
        value=(min_date_val, max_date_val),
        min_value=min_date_val,
        max_value=max_date_val
    )

    traffic_range = st.slider(
        "Filtrar por Volumen de Tráfico",
        min_value=min_traffic_val,
        max_value=max_traffic_val,
        value=(min_traffic_val, max_traffic_val),
        help="Filtra los días que se encuentren dentro de este rango de visitas."
    )

    available_days = df['dia_semana_es'].unique().tolist()
    selected_days = st.multiselect(
        "Días de la Semana",
        options=available_days,
        default=available_days
    )

    reset_filters = st.button("Restablecer Filtros", width='stretch')
    if reset_filters:
        st.rerun()

# Apply filters
df_filtered = df.copy()

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
    df_filtered = df_filtered[
        (df_filtered['fecha'].dt.date >= start_date) &
        (df_filtered['fecha'].dt.date <= end_date)
    ]
elif isinstance(date_range, datetime.date):
    df_filtered = df_filtered[df_filtered['fecha'].dt.date == date_range]

df_filtered = df_filtered[
    (df_filtered['visitantes'] >= traffic_range[0]) &
    (df_filtered['visitantes'] <= traffic_range[1])
]

if selected_days:
    df_filtered = df_filtered[df_filtered['dia_semana_es'].isin(selected_days)]

# RULE 6: Validate empty DataFrames after interactive filtering
if df_filtered.empty:
    st.warning("⚠️ No hay datos disponibles para el rango o combinación de filtros seleccionada. Intente flexibilizar los filtros en la barra lateral.")
    st.stop()

# Upper Visual Structure
st.title("📊 Reporte de Tráfico de Visitantes ST_B2C")
st.caption("⚡ Canal de ventas B2C | Dashboard Corporativo de Rendimiento")

with st.expander("ℹ️ Detalles del Reporte y Cobertura Temporal", expanded=True):
    col_meta1, col_meta2 = st.columns([2, 1])
    with col_meta1:
        st.markdown("**Resumen General:** Monitoreo del tráfico diario de visitantes para el canal digital B2C, registrando el comportamiento durante la temporada de fin de año 2025 e inicios de 2026.")
    with col_meta2:
        start_date_str = df_filtered['fecha'].min().strftime('%Y-%m-%d')
        end_date_str = df_filtered['fecha'].max().strftime('%Y-%m-%d')
        num_days = df_filtered['fecha'].nunique()
        st.markdown(f"**Periodo de Análisis Actual:** `{start_date_str}` al `{end_date_str}` ({num_days} días)")

# Global KPIs (Calculated dynamically over the active filtered frame)
col1, col2, col3, col4 = st.columns(4)

total_visitors = int(df_filtered['visitantes'].sum())
avg_visitors = df_filtered['visitantes'].mean()

max_idx = df_filtered['visitantes'].idxmax()
max_val = int(df_filtered['visitantes'].max())
max_date = df_filtered.loc[max_idx, 'fecha'].strftime('%Y-%m-%d')

min_idx = df_filtered['visitantes'].idxmin()
min_val = int(df_filtered['visitantes'].min())
min_date = df_filtered.loc[min_idx, 'fecha'].strftime('%Y-%m-%d')

with col1:
    st.metric(
        label="Total de Visitantes",
        value=f"{total_visitors} visitas",
        help="Suma acumulada de visitantes durante el periodo filtrado."
    )

with col2:
    st.metric(
        label="Promedio Diario",
        value=f"{avg_visitors:.1f} visitas/día",
        help="Media aritmética de visitas registradas por día."
    )

with col3:
    st.metric(
        label="Pico Máximo de Tráfico",
        value=f"{max_val} visitas",
        delta=f"Fecha: {max_date}",
        delta_color="normal",
        help="Máximo volumen diario detectado en el dataset filtrado."
    )

with col4:
    st.metric(
        label="Pico Mínimo de Tráfico",
        value=f"{min_val} visitas",
        delta=f"Fecha: {min_date}",
        delta_color="inverse",
        help="Mínimo volumen diario detectado en el dataset filtrado."
    )

# Visual tabs implementation
tab_visual, tab_datos = st.tabs([
    "📈 Análisis de Comportamiento Temporal", 
    "🗃️ Registro de Datos de Tráfico (st_b2c_trafico_diario)"
])

with tab_visual:
    st.subheader("Análisis Cronológico de Visitas Diarias")
    
    # Pre-formatting for categorical chronological axis values
    df_filtered_plot = df_filtered.copy()
    df_filtered_plot['fecha_str'] = df_filtered_plot['fecha'].dt.strftime('%Y-%m-%d')
    
    # Area chart
    fig_line = px.area(
        df_filtered_plot, 
        x="fecha_str", 
        y="visitantes",
        title="Evolución de Tráfico Diario vs. Media Histórica",
        labels={"fecha_str": "Fecha de Registro", "visitantes": "Número de Visitantes"},
        line_shape="spline",
        color_discrete_sequence=["#1f77b4"]
    )
    
    # Semantically-bound metadata reference line
    fig_line.add_hline(
        y=18, 
        line_dash="dash", 
        line_color="#FF4B4B", 
        annotation_text="Media Histórica Global (18 visitas/día)", 
        annotation_position="top left"
    )
    
    # RULE 5: Rule compliance with custom horizontal legends
    fig_line.update_layout(
        hovermode="x unified",
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(gridcolor="rgba(0,0,0,0.1)"),
        xaxis=dict(gridcolor="rgba(0,0,0,0.1)"),
        legend=dict(orientation='h', yanchor='bottom', y=-0.25, xanchor='center', x=0.5)
    )
    
    st.plotly_chart(fig_line, width='stretch')
    
    # Bar Chart for distribution
    st.subheader("Distribución de Frecuencias de Tráfico")
    fig_hist = px.bar(
        df_filtered_plot,
        x="fecha_str",
        y="visitantes",
        color="visitantes",
        color_continuous_scale=px.colors.sequential.Viridis,
        title="Intensidad de Visitas Diarias",
        labels={"fecha_str": "Fecha", "visitantes": "Visitantes"}
    )
    fig_hist.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(gridcolor="rgba(0,0,0,0.1)"),
        xaxis=dict(gridcolor="rgba(0,0,0,0.1)"),
        legend=dict(orientation='h', yanchor='bottom', y=-0.25, xanchor='center', x=0.5)
    )
    st.plotly_chart(fig_hist, width='stretch')

with tab_datos:
    st.subheader("Explorador de Registros: st_b2c_trafico_diario")
    st.markdown("Detalle cronológico de visitas diarias recibidas en el portal ST_B2C.")
    
    # RULE 4: Dataframe configuration and rendering
    st.dataframe(
        df_filtered[['fecha', 'dia_semana_es', 'visitantes']],
        column_config={
            "fecha": st.column_config.DateColumn(
                "Fecha del Evento",
                format="YYYY-MM-DD",
            ),
            "dia_semana_es": st.column_config.TextColumn(
                "Día de la Semana"
            ),
            "visitantes": st.column_config.NumberColumn(
                "Visitantes Registrados",
                help="Cantidad de accesos únicos durante el día",
                format="%d visitas",
            )
        },
        width='stretch',
        hide_index=True
    )
    
    # Download Button
    csv = df_filtered[['fecha', 'visitantes']].to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Descargar Datos en CSV",
        data=csv,
        file_name="st_b2c_trafico_diario_filtrado.csv",
        mime="text/csv",
        width='stretch'
    )

# Semantic Relationships (Data Governance Explanations)
st.markdown("---")
with st.expander("⚙️ Gobernanza de Datos y Relaciones Semánticas"):
    st.markdown("""
    *   **Regla de Agregación (Suma):** El KPI de **Total de Visitantes (522)** se calcula dinámicamente mediante la sumatoria de la columna `visitantes` de la tabla `st_b2c_trafico_diario`.
    *   **Regla de Comparación (Media):** La métrica de **Promedio Diario (18)** sirve como umbral crítico para clasificar el rendimiento de cada jornada. Los días por debajo de este límite se consideran con desempeño por debajo de la media y los superiores representan repuntes o picos estacionales de tráfico.
    """)