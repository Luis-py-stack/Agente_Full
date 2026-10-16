import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# -----------------------------------------------------------------------------
# 1. CONFIGURACIÓN DE PÁGINA (Debe ser la PRIMERA instrucción de Streamlit)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Reporte de Tráfico de Visitantes B2C",
    page_icon="📊",
    layout="wide"
)

# -----------------------------------------------------------------------------
# 2. DATOS POR DEFECTO (Autonomía de datos desde JSON)
# -----------------------------------------------------------------------------
DEFAULT_RECORDS = [
    {"Fecha": "2026-01-21 00:00:00", "Visitantes": 31},
    {"Fecha": "2026-01-20 00:00:00", "Visitantes": 28},
    {"Fecha": "2026-01-19 00:00:00", "Visitantes": 26},
    {"Fecha": "2026-01-18 00:00:00", "Visitantes": 25},
    {"Fecha": "2026-01-17 00:00:00", "Visitantes": 27},
    {"Fecha": "2026-01-16 00:00:00", "Visitantes": 18},
    {"Fecha": "2026-01-15 00:00:00", "Visitantes": 22},
    {"Fecha": "2026-01-14 00:00:00", "Visitantes": 15},
    {"Fecha": "2026-01-13 00:00:00", "Visitantes": 15},
    {"Fecha": "2026-01-12 00:00:00", "Visitantes": 8},
    {"Fecha": "2026-01-11 00:00:00", "Visitantes": 9},
    {"Fecha": "2026-01-10 00:00:00", "Visitantes": 15},
    {"Fecha": "2026-01-09 00:00:00", "Visitantes": 16},
    {"Fecha": "2026-01-08 00:00:00", "Visitantes": 12},
    {"Fecha": "2026-01-07 00:00:00", "Visitantes": 16},
    {"Fecha": "2026-01-06 00:00:00", "Visitantes": 14},
    {"Fecha": "2026-01-05 00:00:00", "Visitantes": 24},
    {"Fecha": "2026-01-04 00:00:00", "Visitantes": 15},
    {"Fecha": "2026-01-03 00:00:00", "Visitantes": 8},
    {"Fecha": "2026-01-02 00:00:00", "Visitantes": 15},
    {"Fecha": "2026-01-01 00:00:00", "Visitantes": 14},
    {"Fecha": "2025-12-31 00:00:00", "Visitantes": 10},
    {"Fecha": "2025-12-30 00:00:00", "Visitantes": 35},
    {"Fecha": "2025-12-29 00:00:00", "Visitantes": 13},
    {"Fecha": "2025-12-28 00:00:00", "Visitantes": 13},
    {"Fecha": "2025-12-27 00:00:00", "Visitantes": 26},
    {"Fecha": "2025-12-26 00:00:00", "Visitantes": 26},
    {"Fecha": "2025-12-25 00:00:00", "Visitantes": 12},
    {"Fecha": "2025-12-24 00:00:00", "Visitantes": 14}
]

DIAS_ORDEN = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
DIAS_MAP = {0: 'Lunes', 1: 'Martes', 2: 'Miércoles', 3: 'Jueves', 4: 'Viernes', 5: 'Sábado', 6: 'Domingo'}

# -----------------------------------------------------------------------------
# 3. BARRA LATERAL (Carga de Datos y Filtros)
# -----------------------------------------------------------------------------
st.sidebar.header("⚙️ Configuración y Filtros")

uploaded_file = st.sidebar.file_uploader(
    "Cargar datos personalizados (CSV o Excel)",
    type=["csv", "xlsx"],
    help="Cargue un archivo con columnas 'Fecha' y 'Visitantes'."
)

# Carga de DataFrame
if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df_raw = pd.read_csv(uploaded_file)
        else:
            df_raw = pd.read_excel(uploaded_file)
        st.sidebar.success("✅ Archivo cargado con éxito.")
    except Exception as e:
        st.sidebar.error(f"Error al leer el archivo: {e}")
        df_raw = pd.DataFrame(DEFAULT_RECORDS)
else:
    df_raw = pd.DataFrame(DEFAULT_RECORDS)

# Tipado defensivo y preparación de datos
if 'Fecha' not in df_raw.columns or 'Visitantes' not in df_raw.columns:
    st.error("El conjunto de datos debe contener las columnas 'Fecha' y 'Visitantes'.")
    st.stop()

df_base = df_raw.copy()
df_base['Fecha'] = pd.to_datetime(df_base['Fecha'], errors='coerce')
df_base['Visitantes'] = pd.to_numeric(df_base['Visitantes'], errors='coerce')

# Eliminar registros nulos producidos por conversiones
df_base = df_base.dropna(subset=['Fecha', 'Visitantes']).sort_values('Fecha').reset_index(drop=True)

if df_base.empty:
    st.error("No hay registros válidos con columnas 'Fecha' y 'Visitantes'.")
    st.stop()

# Adición de columnas derivadas
df_base['Fecha_Corta'] = df_base['Fecha'].dt.strftime('%Y-%m-%d')
df_base['Día_Semana'] = df_base['Fecha'].dt.dayofweek.map(DIAS_MAP)

# Controles de Filtros Interactivos
st.sidebar.markdown("---")
st.sidebar.subheader("🔍 Filtros Dinámicos")

# Reset Filtros Button Logic
if st.sidebar.button("🔄 Restablecer Filtros"):
    st.session_state.clear()
    st.rerun()

# 1. Filtro Rango de Fechas
min_f = df_base['Fecha'].min().date()
max_f = df_base['Fecha'].max().date()

rango_fechas = st.sidebar.date_input(
    "Rango de Fechas:",
    value=(min_f, max_f),
    min_value=min_f,
    max_value=max_f,
    key="filter_dates"
)

if isinstance(rango_fechas, (list, tuple)) and len(rango_fechas) == 2:
    f_inicio, f_fin = rango_fechas
else:
    f_inicio, f_fin = min_f, max_f

# 2. Filtro Rango de Visitantes
min_v = int(df_base['Visitantes'].min())
max_v = int(df_base['Visitantes'].max())

rango_vis = st.sidebar.slider(
    "Volumen de Visitantes:",
    min_value=min_v,
    max_value=max_v,
    value=(min_v, max_v),
    key="filter_visitors"
)

# 3. Filtro Día de la Semana
dias_presentes = [d for d in DIAS_ORDEN if d in df_base['Día_Semana'].unique()]
dias_seleccionados = st.sidebar.multiselect(
    "Días de la semana:",
    options=dias_presentes,
    default=dias_presentes,
    key="filter_days"
)

# Aplicar Filtros Reactivos
mask = (
    (df_base['Fecha'].dt.date >= f_inicio) &
    (df_base['Fecha'].dt.date <= f_fin) &
    (df_base['Visitantes'] >= rango_vis[0]) &
    (df_base['Visitantes'] <= rango_vis[1]) &
    (df_base['Día_Semana'].isin(dias_seleccionados))
)

df_filtrado = df_base[mask].copy()

# Validar DataFrame vacío tras filtros
if df_filtrado.empty:
    st.warning("⚠️ No se encontraron registros que coincidan con los filtros seleccionados. Intente ampliar el rango.")
    st.stop()

# -----------------------------------------------------------------------------
# 4. ENCABEZADO Y METADATOS
# -----------------------------------------------------------------------------
st.title("📊 Reporte de Tráfico de Visitantes B2C")
st.caption("Entidad / Canal: Canal ST_B2C | Cobertura Temporal: 2025-12-24 a 2026-01-21 (29 Días)")

with st.expander("ℹ️ Resumen Ejecutivo del Documento", expanded=False):
    st.write(
        "Registro diario del flujo de visitantes en la plataforma/tienda B2C (ST_B2C) "
        "durante un periodo de 29 días, abarcando desde finales de diciembre de 2025 "
        "hasta finales de enero de 2026."
    )

# -----------------------------------------------------------------------------
# 5. TARJETAS DE MÉTRICAS (KPIs DIRECTIVAS)
# -----------------------------------------------------------------------------
total_vis = df_filtrado['Visitantes'].sum()
prom_vis = df_filtrado['Visitantes'].mean()
max_vis = df_filtrado['Visitantes'].max()
min_vis = df_filtrado['Visitantes'].min()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Total de Visitantes",
        value=f"{total_vis:,.0f}",
        help="Suma acumulada de visitas en el periodo filtrado"
    )

with col2:
    st.metric(
        label="Promedio Diario",
        value=f"{prom_vis:.2f}",
        help="Media de afluencia por jornada"
    )

with col3:
    st.metric(
        label="Máximo Diario",
        value=f"{max_vis:,.0f}",
        help="Pico más alto registrado de visitantes"
    )

with col4:
    st.metric(
        label="Mínimo Diario",
        value=f"{min_vis:,.0f}",
        help="Nivel más bajo de visitantes registrado"
    )

st.markdown("---")

# -----------------------------------------------------------------------------
# 6. ESTRUCTURA DE PESTAÑAS
# -----------------------------------------------------------------------------
tab1, tab2, tab3 = st.tabs([
    "📈 Tendencia y Tráfico Diario",
    "📊 Análisis Comportamental y Distribución",
    "📋 Explorador de Datos Crudos"
])

# =============================================================================
# PESTAÑA 1: Tendencia y Tráfico Diario
# =============================================================================
with tab1:
    st.subheader("Evolución Cronológica de Visitantes")
    
    # Gráfico 1: Serie Temporal de Línea
    fig_line = px.line(
        df_filtrado,
        x="Fecha",
        y="Visitantes",
        text="Visitantes",
        title="Tendencia Diaria de Tráfico B2C",
        markers=True
    )
    
    fig_line.update_traces(
        textposition="top center",
        line=dict(width=3, color="#1f77b4"),
        marker=dict(size=8)
    )
    
    # Línea promedio de referencia
    promedio_val = float(df_filtrado['Visitantes'].mean()) if not df_filtrado.empty else 0.0
    fig_line.add_hline(
        y=promedio_val,
        line_dash="dash",
        line_color="#ff7f0e",
        annotation_text=f"Promedio ({promedio_val:.2f})",
        annotation_position="bottom right"
    )
    
    fig_line.update_layout(
        xaxis_title="Fecha",
        yaxis_title="Número de Visitantes",
        legend=dict(orientation='h', yanchor='bottom', y=-0.25, xanchor='center', x=0.5),
        margin=dict(l=20, r=20, t=50, b=20)
    )
    
    st.plotly_chart(fig_line, use_container_width=True)
    
    # Gráfico 2: Volumetría por Jornada (Barras)
    st.subheader("Volumetría Comparativa por Día")
    
    fig_bar = px.bar(
        df_filtrado,
        x="Fecha_Corta",
        y="Visitantes",
        color="Visitantes",
        color_continuous_scale="Viridis",
        title="Flujo Diario de Visitantes (Gradiente por Intensidad)",
        text="Visitantes"
    )
    
    fig_bar.update_traces(textposition="outside")
    fig_bar.update_layout(
        xaxis_title="Fecha (AAAA-MM-DD)",
        yaxis_title="Visitantes",
        legend=dict(orientation='h', yanchor='bottom', y=-0.25, xanchor='center', x=0.5),
        margin=dict(l=20, r=20, t=50, b=20)
    )
    
    st.plotly_chart(fig_bar, use_container_width=True)

# =============================================================================
# PESTAÑA 2: Análisis Comportamental y Distribución
# =============================================================================
with tab2:
    st.subheader("Patrón Semanal y Análisis de Distribución")
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        # Agrupación por día de la semana
        df_dia_agrup = (
            df_filtrado.groupby('Día_Semana', as_index=False)['Visitantes']
            .agg(['mean', 'sum', 'count'])
            .reset_index()
        )
        
        # Reordenamiento lógico de días
        df_dia_agrup['Día_Semana'] = pd.Categorical(
            df_dia_agrup['Día_Semana'],
            categories=DIAS_ORDEN,
            ordered=True
        )
        df_dia_agrup = df_dia_agrup.sort_values('Día_Semana').dropna(subset=['Día_Semana'])
        
        fig_box = px.box(
            df_filtrado,
            x="Día_Semana",
            y="Visitantes",
            points="all",
            category_orders={"Día_Semana": DIAS_ORDEN},
            color="Día_Semana",
            title="Distribución y Dispersión por Día de la Semana"
        )
        fig_box.update_layout(
            xaxis_title="Día de la Semana",
            yaxis_title="Visitantes",
            showlegend=False,
            legend=dict(orientation='h', yanchor='bottom', y=-0.25, xanchor='center', x=0.5)
        )
        st.plotly_chart(fig_box, use_container_width=True)

    with col_b:
        fig_hist = px.histogram(
            df_filtrado,
            x="Visitantes",
            nbins=10,
            title="Frecuencia de Rangos de Visitantes",
            color_discrete_sequence=["#2ca02c"],
            text_auto=True
        )
        fig_hist.update_layout(
            xaxis_title="Rango de Visitantes Diarios",
            yaxis_title="Frecuencia (Días)",
            legend=dict(orientation='h', yanchor='bottom', y=-0.25, xanchor='center', x=0.5)
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    # Tabla resumen por día
    if not df_dia_agrup.empty:
        st.subheader("Resumen Promedio por Día de la Semana")
        df_dia_display = df_dia_agrup.rename(columns={
            'Día_Semana': 'Día de la Semana',
            'mean': 'Promedio Visitantes',
            'sum': 'Total Visitantes',
            'count': 'Días Registrados'
        })
        df_dia_display['Promedio Visitantes'] = df_dia_display['Promedio Visitantes'].round(2)
        st.dataframe(df_dia_display, use_container_width=True)

# =============================================================================
# PESTAÑA 3: Explorador de Datos Crudos
# =============================================================================
with tab3:
    st.subheader("Registros Detallados de Tráfico")
    
    # Formatear dataset para exploración visual
    df_export = df_filtrado[['Fecha_Corta', 'Día_Semana', 'Visitantes']].copy()
    df_export.columns = ['Fecha', 'Día de la Semana', 'Visitantes']
    
    st.dataframe(
        df_export,
        column_config={
            "Fecha": st.column_config.DateColumn("Fecha de Registro", format="YYYY-MM-DD"),
            "Día de la Semana": st.column_config.TextColumn("Día"),
            "Visitantes": st.column_config.ProgressColumn(
                "Nº de Visitantes",
                help="Volumen diario de visitas",
                format="%d",
                min_value=0,
                max_value=int(df_base['Visitantes'].max()) if not df_base.empty else 100
            )
        },
        use_container_width=True
    )
    
    col_down1, col_down2 = st.columns([1, 3])
    with col_down1:
        st.download_button(
            label="📥 Descargar Dataset (CSV)",
            data=df_export.to_csv(index=False).encode('utf-8'),
            file_name="trafico_b2c_st_b2c.csv",
            mime="text/csv"
        )

    with st.expander("🔍 Estadísticas Descriptivas del Dataset Activo", expanded=False):
        st.write(df_filtrado[['Visitantes']].describe().T)