import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import matplotlib

# RULE 1: FIRST Streamlit call must be set_page_config
st.set_page_config(
    page_title="Dashboard Tráfico B2C",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# RULE 2: Embedded dataset
EMBEDDED_RECORDS = [
    {"fecha": "2026-01-21", "visitantes": 31},
    {"fecha": "2026-01-20", "visitantes": 28},
    {"fecha": "2026-01-19", "visitantes": 26},
    {"fecha": "2026-01-18", "visitantes": 25},
    {"fecha": "2026-01-17", "visitantes": 27},
    {"fecha": "2026-01-16", "visitantes": 18},
    {"fecha": "2026-01-15", "visitantes": 22},
    {"fecha": "2026-01-14", "visitantes": 15},
    {"fecha": "2026-01-13", "visitantes": 15},
    {"fecha": "2026-01-12", "visitantes": 8},
    {"fecha": "2026-01-11", "visitantes": 9},
    {"fecha": "2026-01-10", "visitantes": 15},
    {"fecha": "2026-01-09", "visitantes": 16},
    {"fecha": "2026-01-08", "visitantes": 12},
    {"fecha": "2026-01-07", "visitantes": 16},
    {"fecha": "2026-01-06", "visitantes": 14},
    {"fecha": "2026-01-05", "visitantes": 24},
    {"fecha": "2026-01-04", "visitantes": 15},
    {"fecha": "2026-01-03", "visitantes": 8},
    {"fecha": "2026-01-02", "visitantes": 15},
    {"fecha": "2026-01-01", "visitantes": 14},
    {"fecha": "2025-12-31", "visitantes": 10},
    {"fecha": "2025-12-30", "visitantes": 35},
    {"fecha": "2025-12-29", "visitantes": 13},
    {"fecha": "2025-12-28", "visitantes": 13},
    {"fecha": "2025-12-27", "visitantes": 26},
    {"fecha": "2025-12-26", "visitantes": 26},
    {"fecha": "2025-12-25", "visitantes": 12},
    {"fecha": "2025-12-24", "visitantes": 14}
]

# Helper function to load and clean raw data
def prepare_dataframe(df_raw):
    df = df_raw.copy()
    # Defensive casting & cleaning (Rule 6)
    if 'fecha' in df.columns:
        df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
        df = df.dropna(subset=['fecha'])
    if 'visitantes' in df.columns:
        df['visitantes'] = pd.to_numeric(df['visitantes'], errors='coerce')
        df = df.dropna(subset=['visitantes'])
    
    # Feature Engineering for business intelligence
    if 'fecha' in df.columns:
        dias_semana_es = {
            0: 'Lunes', 1: 'Martes', 2: 'Miércoles', 3: 'Jueves', 
            4: 'Viernes', 5: 'Sábado', 6: 'Domingo'
        }
        df['dia_semana_num'] = df['fecha'].dt.dayofweek
        df['dia_semana'] = df['dia_semana_num'].map(dias_semana_es)
    return df

# RULE 3: Optional File Uploader in Sidebar
st.sidebar.header("📥 Carga de Datos Adicionales")
uploaded_file = st.sidebar.file_uploader("Sube un archivo de reemplazo (XLSX, CSV)", type=['xlsx', 'csv'])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df_input = pd.read_csv(uploaded_file)
        else:
            df_input = pd.read_excel(uploaded_file)
        
        # Verify required columns exist (Rule 6)
        if 'fecha' not in df_input.columns or 'visitantes' not in df_input.columns:
            st.sidebar.error("El archivo debe contener las columnas 'fecha' y 'visitantes'")
            df_active = prepare_dataframe(pd.DataFrame(EMBEDDED_RECORDS))
        else:
            df_active = prepare_dataframe(df_input)
            st.sidebar.success("Archivo cargado y procesado exitosamente.")
    except Exception as e:
        st.sidebar.error(f"Error procesando el archivo: {e}")
        df_active = prepare_dataframe(pd.DataFrame(EMBEDDED_RECORDS))
else:
    df_active = prepare_dataframe(pd.DataFrame(EMBEDDED_RECORDS))

# Ensure fallback in case df_active is completely empty after parsing
if df_active.empty:
    st.error("Error: El conjunto de datos activo está vacío. Cargando los datos en memoria por defecto.")
    df_active = prepare_dataframe(pd.DataFrame(EMBEDDED_RECORDS))

# ==============================================================================
# HEADER, METADATA & HISTORIC KPIs
# ==============================================================================
st.title("📈 Reporte de Tráfico de Visitantes B2C")
st.subheader("Monitoreo de Flujo de Canales Digitales | Canal B2C (ST_B2C)")

st.info(
    "**Resumen Ejecutivo:** Monitoreo diario del flujo de visitantes del canal B2C "
    "durante un período de 29 días, que abarca el cierre de diciembre de 2025 y las "
    "primeras semanas de enero de 2026."
)

# Header Row: Metadata dates
min_date_active = df_active['fecha'].min().date()
max_date_active = df_active['fecha'].max().date()

meta_col1, meta_col2 = st.columns(2)
with meta_col1:
    st.write(f"📅 **Fecha de Inicio del Reporte:** `{min_date_active}`")
with meta_col2:
    st.write(f"📅 **Fecha de Fin del Reporte:** `{max_date_active}`")

# Static / Historical summary from initial metadata
st.markdown("### Métricas Históricas de Referencia")
kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
with kpi_col1:
    st.metric(
        label="👤 Total de Visitantes", 
        value="522", 
        help="Suma total acumulada de visitas en el período analizado de 29 días."
    )
with kpi_col2:
    st.metric(
        label="📊 Promedio Diario", 
        value="18 visitantes/día", 
        help="Media de tráfico diario registrado."
    )
with kpi_col3:
    st.metric(
        label="🚀 Pico Máximo de Tráfico", 
        value="35 visitantes", 
        help="Registrado el día 2025-12-30."
    )
with kpi_col4:
    st.metric(
        label="📉 Pico Mínimo de Tráfico", 
        value="8 visitantes", 
        help="Registrado los días 2026-01-03 y 2026-01-12."
    )

st.markdown("---")

# ==============================================================================
# SIDEBAR FILTERS (Rule 6: Reactive & Dynamic)
# ==============================================================================
st.sidebar.header("🎛️ Filtros Interactivos")

# 1. Date Range Filter
date_range = st.sidebar.date_input(
    "Selecciona Rango de Fechas:",
    value=(min_date_active, max_date_active),
    min_value=min_date_active,
    max_value=max_date_active
)

# Parse reactive date inputs safely
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date_active, max_date_active

# 2. Volume Range Filter (Slider)
min_vis = int(df_active['visitantes'].min())
max_vis = int(df_active['visitantes'].max())
visitor_range = st.sidebar.slider(
    "Filtrar por rango de visitantes diarios:",
    min_value=min_vis,
    max_value=max_vis,
    value=(min_vis, max_vis)
)

# 3. Weekday Filter (Multiselect)
if 'dia_semana' in df_active.columns:
    unique_days = list(df_active['dia_semana'].unique())
    selected_days = st.sidebar.multiselect(
        "Filtrar por Día de la Semana:",
        options=unique_days,
        default=unique_days
    )
else:
    selected_days = []

# Apply reactive filters defensively
df_filtered = df_active[
    (df_active['fecha'].dt.date >= start_date) & 
    (df_active['fecha'].dt.date <= end_date) &
    (df_active['visitantes'] >= visitor_range[0]) &
    (df_active['visitantes'] <= visitor_range[1])
]

if 'dia_semana' in df_filtered.columns and len(selected_days) > 0:
    df_filtered = df_filtered[df_filtered['dia_semana'].isin(selected_days)]

# RULE 6: Empty dataframe validation before plotting
if df_filtered.empty:
    st.warning("⚠️ No existen registros para la combinación de filtros seleccionada en la barra lateral.")
    st.stop()

# ==============================================================================
# TABS AND VISUALIZATIONS
# ==============================================================================
tab1, tab2, tab3 = st.tabs([
    "📈 Análisis de Tendencia", 
    "📊 Comportamiento y Distribución", 
    "📋 Datos Consolidados"
])

# ------------------------------------------------------------------------------
# TAB 1: Análisis de Tendencia
# ------------------------------------------------------------------------------
with tab1:
    st.subheader("Evolución Temporal de Visitas")
    
    # Real-time reactive statistics
    dr_col1, dr_col2, dr_col3 = st.columns(3)
    with dr_col1:
        st.metric("Total Visitantes (Rango)", int(df_filtered['visitantes'].sum()))
    with dr_col2:
        st.metric("Promedio Diario (Rango)", f"{df_filtered['visitantes'].mean():.1f}")
    with dr_col3:
        st.metric("Máximo Tráfico (Rango)", int(df_filtered['visitantes'].max()))

    # Line Chart of Trends
    fig_line = px.line(
        df_filtered.sort_values('fecha'),
        x='fecha',
        y='visitantes',
        title='Tráfico de Visitantes a lo largo del tiempo',
        labels={'fecha': 'Fecha', 'visitantes': 'Visitantes'},
        markers=True,
        template='plotly_white'
    )
    
    # Add baseline average line
    avg_val = df_filtered['visitantes'].mean()
    fig_line.add_hline(
        y=avg_val, 
        line_dash="dash", 
        line_color="red", 
        annotation_text=f"Promedio: {avg_val:.1f}",
        annotation_position="bottom right"
    )
    
    # Add peak annotation if present in the current filter scope
    peak_record = df_filtered[df_filtered['visitantes'] == df_filtered['visitantes'].max()]
    if not peak_record.empty:
        peak_row = peak_record.iloc[0]
        fig_line.add_annotation(
            x=peak_row['fecha'],
            y=peak_row['visitantes'],
            text=f"Máximo: {int(peak_row['visitantes'])}",
            showarrow=True,
            arrowhead=2,
            ax=0,
            ay=-40,
            bgcolor="rgba(255, 235, 204, 0.9)",
            bordercolor="orange"
        )

    # RULE 5: Rule-compliant horizontal legend positioning
    fig_line.update_layout(
        legend=dict(orientation='h', yanchor='bottom', y=-0.25, xanchor='center', x=0.5),
        margin=dict(l=40, r=40, t=60, b=40)
    )
    st.plotly_chart(fig_line, width='stretch')

# ------------------------------------------------------------------------------
# TAB 2: Comportamiento y Distribución
# ------------------------------------------------------------------------------
with tab2:
    st.subheader("Análisis Estacional y Desglose de Tráfico")
    
    dist_col1, dist_col2 = st.columns(2)
    
    with dist_col1:
        st.markdown("#### Distribución del Volumen Diario")
        fig_bar_dist = px.bar(
            df_filtered.sort_values('fecha'),
            x='fecha',
            y='visitantes',
            color='visitantes',
            color_continuous_scale='Blues',
            labels={'fecha': 'Día', 'visitantes': 'Visitantes'},
            title='Volumen Diario de Tráfico B2C'
        )
        fig_bar_dist.update_layout(
            legend=dict(orientation='h', yanchor='bottom', y=-0.25, xanchor='center', x=0.5)
        )
        st.plotly_chart(fig_bar_dist, width='stretch')
        
    with dist_col2:
        st.markdown("#### Análisis por Día de la Semana")
        if 'dia_semana' in df_filtered.columns:
            # Force chronological weekday order
            orden_dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
            df_weekly = (
                df_filtered.groupby(['dia_semana', 'dia_semana_num'])['visitantes']
                .mean()
                .reset_index()
                .sort_values('dia_semana_num')
            )
            
            fig_week = px.bar(
                df_weekly,
                x='dia_semana',
                y='visitantes',
                labels={'dia_semana': 'Día de la Semana', 'visitantes': 'Promedio de Visitantes'},
                color='visitantes',
                color_continuous_scale='Viridis',
                title='Promedio de Visitantes por Día de la Semana'
            )
            fig_week.update_layout(
                legend=dict(orientation='h', yanchor='bottom', y=-0.25, xanchor='center', x=0.5)
            )
            st.plotly_chart(fig_week, width='stretch')
        else:
            st.info("Columna 'dia_semana' no disponible para el desglose estacional.")

# ------------------------------------------------------------------------------
# TAB 3: Datos Consolidados
# ------------------------------------------------------------------------------
with tab3:
    st.subheader("Explorador y Gobierno de Datos")
    st.write("Tabla interactiva con el set de datos filtrado. Permite ordenación rápida y filtrado interno.")
    
    # RULE 4: Dataframe presentation with width stretch / container width and modern progress columns
    st.dataframe(
        df_filtered[['fecha', 'visitantes', 'dia_semana']].sort_values(by='fecha', ascending=False),
        column_config={
            "fecha": st.column_config.DateColumn(
                "Fecha de Operación",
                format="YYYY-MM-DD"
            ),
            "visitantes": st.column_config.ProgressColumn(
                "Tráfico (Visitantes)",
                help="Volumen diario de visitas registradas en la plataforma",
                format="%d",
                min_value=0,
                max_value=int(df_active['visitantes'].max())
            ),
            "dia_semana": st.column_config.TextColumn(
                "Día de la Semana"
            )
        },
        width='stretch',
        hide_index=True
    )
    
    # Raw Data Export Button
    csv_data = df_filtered[['fecha', 'visitantes']].to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Descargar datos filtrados (CSV)",
        data=csv_data,
        file_name="reporte_trafico_b2c.csv",
        mime="text/csv",
        width='stretch'
    )