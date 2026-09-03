import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# -----------------------------------------------------------------------------
# 1. CONFIGURACIÓN DE PÁGINA (Debe ser la primera llamada de Streamlit)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Reporte de Tráfico Diario - Canal ST_B2C",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# 2. DATOS EN MEMORIA (Autonomía de datos completa según especificaciones)
# -----------------------------------------------------------------------------
raw_records = [
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
    {"Fecha": "2025-01-05 00:00:00", "Visitantes": 24}, # Se asume corrección de typo a 2026 o se conserva tal cual
    {"Fecha": "2026-01-05 00:00:00", "Visitantes": 24}, # Registro corregido implícito del JSON original
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

# Corrección y parseo del dataset base
df_default = pd.DataFrame(raw_records)
# Asegurar unicidad y formato uniforme de las fechas
df_default['Fecha'] = pd.to_datetime(df_default['Fecha']).dt.date
df_default = df_default.drop_duplicates(subset=['Fecha']).sort_values('Fecha').reset_index(drop=True)

# -----------------------------------------------------------------------------
# 3. BARRA LATERAL (FILTROS OPCIONALES Y FILE UPLOADER)
# -----------------------------------------------------------------------------
st.sidebar.header("⚙️ Configuración y Carga")

# File uploader opcional
uploaded_file = st.sidebar.file_uploader("Cargar archivo personalizado (xlsx, csv)", type=['xlsx', 'csv'])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df_loaded = pd.read_csv(uploaded_file)
        else:
            df_loaded = pd.read_excel(uploaded_file)
            
        # Validación básica de estructura para el archivo cargado
        if 'Fecha' in df_loaded.columns and 'Visitantes' in df_loaded.columns:
            df_loaded['Fecha'] = pd.to_datetime(df_loaded['Fecha']).dt.date
            df_loaded['Visitantes'] = pd.to_numeric(df_loaded['Visitantes'], errors='coerce').fillna(0).astype(int)
            df = df_loaded.sort_values('Fecha').reset_index(drop=True)
            st.sidebar.success("📁 ¡Archivo cargado con éxito!")
        else:
            st.sidebar.error("El archivo cargado debe contener las columnas 'Fecha' y 'Visitantes'.")
            df = df_default.copy()
    except Exception as e:
        st.sidebar.error(f"Error procesando archivo: {e}")
        df = df_default.copy()
else:
    df = df_default.copy()

# Filtros Dinámicos basados en el dataframe activo
st.sidebar.markdown("---")
st.sidebar.subheader("🎯 Filtros de Datos")

if 'Fecha' in df.columns and 'Visitantes' in df.columns and not df.empty:
    min_date = df['Fecha'].min()
    max_date = df['Fecha'].max()
    
    # Selector de Rango de Fechas
    date_range = st.sidebar.date_input(
        "Rango de Fechas Analizado",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    # Filtro de volumen de tráfico
    min_vis = int(df['Visitantes'].min())
    max_vis = int(df['Visitantes'].max())
    
    traffic_range = st.sidebar.slider(
        "Filtro por volumen de visitantes",
        min_value=min_vis,
        max_value=max_vis,
        value=(min_vis, max_vis)
    )
    
    # Aplicar Filtros de forma segura
    # Controlar que date_input devuelva tupla completa de inicio y fin
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
        df_filtered = df[
            (df['Fecha'] >= start_date) & 
            (df['Fecha'] <= end_date) & 
            (df['Visitantes'] >= traffic_range[0]) & 
            (df['Visitantes'] <= traffic_range[1])
        ]
    else:
        df_filtered = df[
            (df['Visitantes'] >= traffic_range[0]) & 
            (df['Visitantes'] <= traffic_range[1])
        ]
else:
    df_filtered = df.copy()

# Botón de reinicio de filtros en el sidebar
if st.sidebar.button("🔄 Resetear Filtros"):
    st.rerun()

# -----------------------------------------------------------------------------
# 4. CABECERA, METADATOS Y RESUMEN EJECUTIVO
# -----------------------------------------------------------------------------
st.title("📈 Reporte de Tráfico Diario — Canal ST_B2C")

with st.expander("ℹ️ Resumen del Documento, Metadatos y Contexto", expanded=True):
    col_meta1, col_meta2 = st.columns([2, 1])
    with col_meta1:
        st.markdown("""
        **Sujeto de Análisis:** Canal de Ventas y Atención Directa al Consumidor (`ST_B2C`).  
        **Periodo del Reporte Original:** Desde el 24 de diciembre de 2025 hasta el 21 de enero de 2026.  
        **Descripción:** Análisis estratégico orientado a medir y evaluar las fluctuaciones, picos temporales y estabilidad del flujo diario de visitantes en nuestro portal web para soportar la toma de decisiones basada en datos de tráfico.
        """)
    with col_meta2:
        st.info(f"""
        **Metadatos Activos:**
        - **Registros filtrados:** {len(df_filtered)} de {len(df)} días.
        - **Fecha de Inicio:** {df_filtered['Fecha'].min() if not df_filtered.empty else 'N/A'}
        - **Fecha de Corte:** {df_filtered['Fecha'].max() if not df_filtered.empty else 'N/A'}
        """)

st.markdown("---")

# -----------------------------------------------------------------------------
# 5. TARJETAS DE MÉTRICAS (KPIs Dinámicos y Coherencia Semántica)
# -----------------------------------------------------------------------------
if not df_filtered.empty and 'Visitantes' in df_filtered.columns:
    total_visitantes = df_filtered['Visitantes'].sum()
    promedio_diario = df_filtered['Visitantes'].mean()
    max_visitantes = df_filtered['Visitantes'].max()
    min_visitantes = df_filtered['Visitantes'].min()
    
    # Encontrar las fechas específicas de los máximos y mínimos para anotaciones ricas
    fecha_max_series = df_filtered[df_filtered['Visitantes'] == max_visitantes]['Fecha']
    fecha_min_series = df_filtered[df_filtered['Visitantes'] == min_visitantes]['Fecha']
    
    fecha_max_str = str(fecha_max_series.iloc[0]) if not fecha_max_series.empty else "N/A"
    fecha_min_str = ", ".join([str(d) for d in fecha_min_series]) if not fecha_min_series.empty else "N/A"
else:
    total_visitantes = 0
    promedio_diario = 0.0
    max_visitantes = 0
    min_visitantes = 0
    fecha_max_str = "N/A"
    fecha_min_str = "N/A"

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Total de Visitantes", 
        value=f"{total_visitantes:,} visitas", 
        help="Suma acumulada del tráfico de visitantes dentro de los criterios y fechas filtradas actualmente."
    )

with col2:
    st.metric(
        label="Promedio Diario", 
        value=f"{promedio_diario:.1f} vis/día", 
        help="Media de tráfico calculado diariamente en base al periodo y condiciones seleccionadas."
    )

with col3:
    st.metric(
        label="Tráfico Máximo Diario", 
        value=f"{max_visitantes} visitas", 
        delta=f"Pico el: {fecha_max_str}",
        delta_color="normal",
        help="Volumen máximo de visitas diarias registrado en el rango de tiempo seleccionado."
    )

with col4:
    st.metric(
        label="Tráfico Mínimo Diario", 
        value=f"{min_visitantes} visitas", 
        delta=f"Valles el: {fecha_min_str}",
        delta_color="inverse",
        help="Volumen mínimo de visitas diarias registrado en el rango de tiempo seleccionado."
    )

st.markdown("---")

# -----------------------------------------------------------------------------
# 6. PESTAÑAS DE VISUALIZACIÓN Y NAVEGACIÓN (st.tabs)
# -----------------------------------------------------------------------------
tab1, tab2, tab3 = st.tabs([
    "📈 Tendencias y Comportamiento Temporal", 
    "📊 Distribución del Tráfico", 
    "🗂️ Exploración de Datos Crudos"
])

# Validar que existan las columnas clave antes de generar visualizaciones
if 'Fecha' in df_filtered.columns and 'Visitantes' in df_filtered.columns and not df_filtered.empty:
    
    # -------------------------------------------------------------------------
    # TAB 1: TENDENCIAS
    # -------------------------------------------------------------------------
    with tab1:
        st.subheader("Análisis de Tendencias Diarias y Flujos")
        
        # Creación de Gráfico de Líneas con Plotly Express
        fig_line = px.line(
            df_filtered, 
            x="Fecha", 
            y="Visitantes",
            title="Evolución de Tráfico Diario — Canal ST_B2C",
            labels={"Fecha": "Fecha de Análisis", "Visitantes": "Cantidad de Visitantes"},
            markers=True,
            template="plotly_white"
        )
        
        # Agregar línea horizontal indicando el promedio dinámico actual
        fig_line.add_hline(
            y=promedio_diario, 
            line_dash="dash", 
            line_color="#2ca02c", 
            annotation_text=f"Promedio Activo ({promedio_diario:.1f})", 
            annotation_position="bottom right"
        )
        
        # Personalización de trazados y marcadores
        fig_line.update_traces(
            line_color="#0068C9", 
            line_width=2.5,
            marker=dict(size=8, color="#FF4B4B")
        )
        
        fig_line.update_layout(
            hovermode="x unified",
            xaxis_title="Fecha de Registro",
            yaxis_title="Visitantes",
            margin=dict(l=20, r=20, t=50, b=20)
        )
        
        st.plotly_chart(fig_line, use_container_width=True)
        
        st.markdown("""
        **Observaciones de Tendencia:**  
        * El pico absoluto se identifica en el histórico el **2025-12-30** con un repunte a **35 visitantes**, seguido de un comportamiento oscilatorio que se estabiliza a mediados de enero. 
        * Los valles más pronunciados dentro del ciclo regular alcanzan el umbral de **8 visitantes**, representando periodos de baja interacción digital ideales para mantenimientos planificados.
        """)

    # -------------------------------------------------------------------------
    # TAB 2: DISTRIBUCIÓN
    # -------------------------------------------------------------------------
    with tab2:
        st.subheader("Análisis Estadístico de Distribución")
        col_graph1, col_graph2 = st.columns(2)
        
        with col_graph1:
            st.markdown("**Frecuencia del Tráfico Diario**")
            fig_hist = px.histogram(
                df_filtered, 
                x="Visitantes", 
                nbins=12,
                title="Distribución del Volumen de Visitas",
                labels={"Visitantes": "Intervalos de Visitantes (Bins)", "count": "Frecuencia (Días)"},
                color_discrete_sequence=["#29B5E8"],
                template="plotly_white"
            )
            fig_hist.update_layout(
                yaxis_title="Cantidad de Días",
                margin=dict(l=20, r=20, t=50, b=20)
            )
            st.plotly_chart(fig_hist, use_container_width=True)
            
        with col_graph2:
            st.markdown("**Análisis de Dispersión y Cuartiles**")
            fig_box = px.box(
                df_filtered, 
                y="Visitantes",
                title="Diagrama de Caja y Bigotes (Box Plot)",
                points="all",
                color_discrete_sequence=["#FF4B4B"],
                template="plotly_white"
            )
            fig_box.update_layout(
                yaxis_title="Rango de Visitantes",
                margin=dict(l=20, r=20, t=50, b=20)
            )
            st.plotly_chart(fig_box, use_container_width=True)

    # -------------------------------------------------------------------------
    # TAB 3: EXPLORADOR DE DATOS CRUDOS
    # -------------------------------------------------------------------------
    with tab3:
        st.subheader("Auditoría de Registros Diarios en el Portal B2C")
        st.markdown("La siguiente tabla interactiva visualiza los datos cargados / filtrados con barras de progreso integradas para comparar visualmente las magnitudes diarias.")
        
        # Renderizado interactivo y estilizado
        st.dataframe(
            df_filtered,
            column_config={
                "Fecha": st.column_config.DateColumn(
                    "Fecha de Registro",
                    format="YYYY-MM-DD",
                    help="Día específico del flujo de tráfico registrado"
                ),
                "Visitantes": st.column_config.ProgressColumn(
                    "Visitantes Únicos",
                    help="Flujo acumulado diario en el canal ST_B2C",
                    format="%d",
                    min_value=0,
                    max_value=35
                )
            },
            use_container_width=True,
            hide_index=True
        )
        
        # Descarga de Datos Filtrados
        st.markdown("---")
        csv_data = df_filtered.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Descargar Set de Datos Activo (CSV)",
            data=csv_data,
            file_name='trafico_filtrado_st_b2c.csv',
            mime='text/csv',
        )

else:
    st.warning("⚠️ No se han encontrado registros de datos válidos que coincidan con los filtros aplicados o las columnas del archivo cargado son incorrectas. Por favor, reajuste los controles de la barra lateral.")