import streamlit as st
import pandas as pd
import plotly.express as px
import datetime

# ---------------------------------------------------------
# RULE 1: Configuración de página de Streamlit (Primera instrucción)
# ---------------------------------------------------------
st.set_page_config(
    page_title="Reporte de Tráfico y Visitantes ST_B2C",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# RULE 2: Autonomía de Datos - DataFrames en memoria
# ---------------------------------------------------------
DEFAULT_RECORDS = [
    { "Fecha": "2026-01-21", "Visitantes": 31 },
    { "Fecha": "2026-01-20", "Visitantes": 28 },
    { "Fecha": "2026-01-19", "Visitantes": 26 },
    { "Fecha": "2026-01-18", "Visitantes": 25 },
    { "Fecha": "2026-01-17", "Visitantes": 27 },
    { "Fecha": "2026-01-16", "Visitantes": 18 },
    { "Fecha": "2026-01-15", "Visitantes": 22 },
    { "Fecha": "2026-01-14", "Visitantes": 15 },
    { "Fecha": "2026-01-13", "Visitantes": 15 },
    { "Fecha": "2026-01-12", "Visitantes": 8 },
    { "Fecha": "2026-01-11", "Visitantes": 9 },
    { "Fecha": "2026-01-10", "Visitantes": 15 },
    { "Fecha": "2026-01-09", "Visitantes": 16 },
    { "Fecha": "2026-01-08", "Visitantes": 12 },
    { "Fecha": "2026-01-07", "Visitantes": 16 },
    { "Fecha": "2026-01-06", "Visitantes": 14 },
    { "Fecha": "2026-01-05", "Visitantes": 24 },
    { "Fecha": "2026-01-04", "Visitantes": 15 },
    { "Fecha": "2026-01-03", "Visitantes": 8 },
    { "Fecha": "2026-01-02", "Visitantes": 15 },
    { "Fecha": "2026-01-01", "Visitantes": 14 },
    { "Fecha": "2025-12-31", "Visitantes": 10 },
    { "Fecha": "2025-12-30", "Visitantes": 35 },
    { "Fecha": "2025-12-29", "Visitantes": 13 },
    { "Fecha": "2025-12-28", "Visitantes": 13 },
    { "Fecha": "2025-12-27", "Visitantes": 26 },
    { "Fecha": "2025-12-26", "Visitantes": 26 },
    { "Fecha": "2025-12-25", "Visitantes": 12 },
    { "Fecha": "2025-12-24", "Visitantes": 14 }
]

@st.cache_data
def get_default_data():
    df = pd.DataFrame(DEFAULT_RECORDS)
    df['Fecha'] = pd.to_datetime(df['Fecha'])
    df = df.sort_values(by='Fecha').reset_index(drop=True)
    return df

# ---------------------------------------------------------
# RULE 3: File Uploader opcional en el sidebar
# ---------------------------------------------------------
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3090/3090011.png", width=70)
st.sidebar.title("Configuración de Datos")
st.sidebar.markdown("Cargue un archivo propio o use los datos por defecto del sistema.")

uploaded_file = st.sidebar.file_uploader(
    "Subir archivo de tráfico", 
    type=['csv', 'xlsx'], 
    help="Debe contener columnas 'Fecha' y 'Visitantes'"
)

# Lógica de carga de datos (Defensiva)
df_base = None
if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df_uploaded = pd.read_csv(uploaded_file)
        else:
            df_uploaded = pd.read_excel(uploaded_file)
        
        # Estandarizar nombres de columnas
        df_uploaded.columns = [str(col).strip().capitalize() for col in df_uploaded.columns]
        
        if "Fecha" in df_uploaded.columns and "Visitantes" in df_uploaded.columns:
            df_base = df_uploaded
            st.sidebar.success("¡Datos cargados exitosamente!")
        else:
            st.sidebar.error("Error: El archivo debe poseer columnas 'Fecha' y 'Visitantes'.")
    except Exception as e:
        st.sidebar.error(f"Error procesando archivo: {e}")

if df_base is None:
    df_base = get_default_data()

# ---------------------------------------------------------
# RULE 6: Tipado Defensivo y Preparación de Atributos
# ---------------------------------------------------------
if 'Fecha' in df_base.columns:
    df_base['Fecha'] = pd.to_datetime(df_base['Fecha'], errors='coerce')
    df_base = df_base.dropna(subset=['Fecha'])

if 'Visitantes' in df_base.columns:
    df_base['Visitantes'] = pd.to_numeric(df_base['Visitantes'], errors='coerce').fillna(0).astype(int)

# Ingeniería de Variables básica
df_base['Dia_Semana'] = df_base['Fecha'].dt.day_name()
df_base['Dia_Semana_Num'] = df_base['Fecha'].dt.dayofweek
df_base = df_base.sort_values(by='Fecha').reset_index(drop=True)

# ---------------------------------------------------------
# CONTROLES INTERACTIVOS (Sidebar)
# ---------------------------------------------------------
st.sidebar.markdown("---")
st.sidebar.subheader("Filtros Analíticos")

# Filtro 1: Rango de Fechas
min_date = df_base['Fecha'].min().date()
max_date = df_base['Fecha'].max().date()

selected_dates = st.sidebar.date_input(
    "Rango Temporal",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Filtro 2: Selector de Volumen de Tráfico
min_vis = int(df_base['Visitantes'].min())
max_vis = int(df_base['Visitantes'].max())
selected_traffic = st.sidebar.slider(
    "Rango de Visitantes Diarios",
    min_value=min_vis,
    max_value=max_vis,
    value=(min_vis, max_vis)
)

# Filtro 3: Selección por Día de la Semana
dias_semana_disponibles = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
selected_days = st.sidebar.multiselect(
    "Días de la semana permitidos",
    options=dias_semana_disponibles,
    default=dias_semana_disponibles
)

# Aplicar filtrado reactivo
if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
    start_date, end_date = selected_dates
else:
    start_date, end_date = min_date, max_date

df_filtered = df_base[
    (df_base['Fecha'].dt.date >= start_date) & 
    (df_base['Fecha'].dt.date <= end_date) &
    (df_base['Visitantes'] >= selected_traffic[0]) &
    (df_base['Visitantes'] <= selected_traffic[1]) &
    (df_base['Dia_Semana'].isin(selected_days))
]

# RULE 6: Validación estricta de DataFrame vacío antes de operar o graficar
if df_filtered.empty:
    st.warning("⚠️ No existen registros para la combinación de filtros seleccionada. Amplíe los límites en el panel izquierdo.")
    st.stop()

# ---------------------------------------------------------
# CABECERA PRINCIPAL Y METADATOS
# ---------------------------------------------------------
st.title("📊 Reporte de Tráfico y Visitantes ST_B2C")
st.markdown(f"**Canal de Análisis:** Canal B2C (ST_B2C) | **Periodo Actual:** Desde {start_date} hasta {end_date}")

with st.expander("ℹ️ Resumen Metodológico del Tablero", expanded=False):
    st.markdown("""
    Este dashboard inteligente muestra el registro diario del volumen de visitantes para el canal B2C. 
    Permite filtrar la información dinámicamente y recalcular indicadores en tiempo real. 
    Los cambios interactivos del panel de navegación se reflejan inmediatamente en las métricas superiores, 
    pestañas de comportamiento analítico e informes listos para exportar.
    """)

# ---------------------------------------------------------
# TARJETAS DE INDICADORES CLAVE (KPIs Dinámicos)
# ---------------------------------------------------------
kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

# Cálculo de Baselines para deltas dinámicos contextualmente
base_total = df_base['Visitantes'].sum()
base_avg = df_base['Visitantes'].mean()
base_max = df_base['Visitantes'].max()
base_min = df_base['Visitantes'].min()
base_days = len(df_base)

# KPI 1: Total Visitantes
total_filtered = df_filtered['Visitantes'].sum()
delta_total = int(total_filtered - base_total)
kpi1.metric(
    label="Total de Visitantes",
    value=f"{total_filtered:,} pax",
    delta=f"{delta_total} vs Base" if delta_total != 0 else "Estable",
    help="Suma total acumulada de visitas en el periodo filtrado actual."
)

# KPI 2: Promedio Diario de Visitantes
avg_filtered = df_filtered['Visitantes'].mean() if len(df_filtered) > 0 else 0
delta_avg = round(avg_filtered - base_avg, 1)
kpi2.metric(
    label="Promedio Diario",
    value=f"{round(avg_filtered, 1)} pax/d",
    delta=f"{delta_avg} vs Base" if delta_avg != 0 else "Estable",
    help="Promedio diario de visitantes obtenido de las muestras seleccionadas."
)

# KPI 3: Tráfico Máximo Diario
max_filtered = df_filtered['Visitantes'].max() if len(df_filtered) > 0 else 0
delta_max = int(max_filtered - base_max)
kpi3.metric(
    label="Tráfico Máximo",
    value=f"{max_filtered} pax",
    delta=f"{delta_max} vs Máx Histórico" if delta_max != 0 else "Récord Máximo",
    help="Punto con mayor volumen diario de tráfico en el rango actual."
)

# KPI 4: Tráfico Mínimo Diario
min_filtered = df_filtered['Visitantes'].min() if len(df_filtered) > 0 else 0
delta_min = int(min_filtered - base_min)
kpi4.metric(
    label="Tráfico Mínimo",
    value=f"{min_filtered} pax",
    delta=f"{delta_min} vs Mín Histórico" if delta_min != 0 else "Récord Mínimo",
    help="Punto de menor flujo de tráfico dentro del rango."
)

# KPI 5: Días Totales Evaluados
days_filtered = len(df_filtered)
delta_days = int(days_filtered - base_days)
kpi5.metric(
    label="Días Evaluados",
    value=f"{days_filtered} días",
    delta=f"{delta_days} vs Base" if delta_days != 0 else "Periodo Completo",
    help="Número total de días que satisfacen las reglas de filtro activas."
)

st.markdown("---")

# ---------------------------------------------------------
# PESTAÑAS DEL CUADRO DE MANDO
# ---------------------------------------------------------
tab_analytics, tab_data_explorer = st.tabs([
    "📈 Dashboard Analítico y Tendencias", 
    "📂 Explorador de Registros y Descarga"
])

# ---------------------------------------------------------
# PESTAÑA 1: ANALÍTICA INTERACTIVA
# ---------------------------------------------------------
with tab_analytics:
    st.subheader("Tendencias de Tráfico Temporal (Canal B2C)")
    
    # Gráfico 1: Evolución Temporal Completa
    fig_line = px.line(
        df_filtered,
        x='Fecha',
        y='Visitantes',
        title='Evolución del Volumen de Tráfico Diario',
        labels={'Fecha': 'Fecha de Operación', 'Visitantes': 'Visitantes Registrados'},
        markers=True,
        text='Visitantes',
        template='plotly_white'
    )
    
    # Línea de tendencia de promedio dinámico
    fig_line.add_hline(
        y=avg_filtered, 
        line_dash="dash", 
        line_color="#E74C3C",
        annotation_text=f"Media: {round(avg_filtered, 1)} pax", 
        annotation_position="top left"
    )
    
    fig_line.update_traces(textposition="top center", line_color="#2980B9", marker=dict(size=8))
    fig_line.update_layout(
        hovermode="x unified", 
        height=450,
        margin=dict(l=40, r=40, t=50, b=40)
    )
    
    # RULE 5: Mostrar gráfico Plotly de forma responsiva
    st.plotly_chart(fig_line, use_container_width=True)
    
    st.markdown("---")
    
    # Gráfico 2 & 3: Distribución y Análisis Estacional
    col_chart_1, col_chart_2 = st.columns(2)
    
    with col_chart_1:
        st.subheader("Estacionalidad por Día de la Semana")
        
        # Agrupación y ordenamiento correcto de días laborables
        df_weekday = df_filtered.groupby(['Dia_Semana', 'Dia_Semana_Num'])['Visitantes'].mean().reset_index()
        df_weekday = df_weekday.sort_values(by='Dia_Semana_Num')
        
        fig_bar_week = px.bar(
            df_weekday,
            x='Dia_Semana',
            y='Visitantes',
            title='Tráfico Promedio por Día de la Semana',
            labels={'Dia_Semana': 'Día de la Semana', 'Visitantes': 'Media de Visitantes'},
            color='Visitantes',
            color_continuous_scale='Blues',
            template='plotly_white'
        )
        fig_bar_week.update_layout(
            height=380,
            coloraxis_showscale=False
        )
        st.plotly_chart(fig_bar_week, use_container_width=True)
        
    with col_chart_2:
        st.subheader("Análisis de Densidad y Outliers")
        
        fig_hist = px.histogram(
            df_filtered,
            x='Visitantes',
            nbins=12,
            title='Distribución y Frecuencia de Tráfico Diario',
            labels={'Visitantes': 'Rango de Visitantes', 'count': 'Frecuencia en Días'},
            marginal='box',
            color_discrete_sequence=['#27AE60'],
            template='plotly_white'
        )
        fig_hist.update_layout(
            height=380
        )
        st.plotly_chart(fig_hist, use_container_width=True)

# ---------------------------------------------------------
# PESTAÑA 2: EXPLORACIÓN DE DATOS CRUDOS
# ---------------------------------------------------------
with tab_data_explorer:
    st.subheader("Explorador Detallado de Registros de Tráfico")
    st.markdown("Se muestran los registros que concuerdan con la segmentación. Utilice las columnas para ordenar o buscar datos.")

    # RULE 4: Renderizado robusto de tablas con st.dataframe
    st.dataframe(
        df_filtered,
        column_order=["Fecha", "Dia_Semana", "Visitantes"],
        column_config={
            "Fecha": st.column_config.DateColumn(
                "Fecha de Registro",
                format="YYYY-MM-DD",
                help="Día correspondiente al volumen captado."
            ),
            "Dia_Semana": st.column_config.TextColumn(
                "Día de la Semana",
                help="Nombre estándar en inglés del día evaluado."
            ),
            "Visitantes": st.column_config.NumberColumn(
                "Visitantes Registrados",
                format="%d pax",
                help="Cantidad total observada."
            )
        },
        use_container_width=True,
        hide_index=True
    )
    
    st.markdown("### Exportar Resultados")
    csv_out = df_filtered.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Descargar set de datos en formato CSV",
        data=csv_out,
        file_name='reporte_trafico_B2C_filtrado.csv',
        mime='text/csv',
        help="Guarde los datos actuales filtrados directamente en su máquina en formato CSV."
    )