import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import io

# 1. CONFIGURACIÓN DE LA PÁGINA (Debe ser la primera llamada a Streamlit)
st.set_page_config(
    page_title="Reporte de Tráfico Web - Canal ST_B2C",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. DATOS DE RESPALDO EN MEMORIA (AUTONOMÍA DE DATOS)
DATA_JSON = {
  "metadata": {
    "document_title": "Reporte de Tráfico Web - Canal ST_B2C",
    "entity_or_subject": "ST_B2C (Canal de Comercio Electrónico B2C)",
    "dates": "2025-12-24 a 2026-01-21",
    "general_summary": "Monitoreo y registro del volumen diario de visitantes para el canal de negocio B2C, abarcando la temporada de fin de año 2025 y el inicio del año 2026."
  },
  "global_kpis_and_totals": {
    "total_visitantes": 522,
    "promedio_diario": 18.0,
    "pico_maximo": 35,
    "pico_fecha": "2025-12-30",
    "minimo_registrado": 8
  },
  "records": [
    { "Fecha": "2026-01-21 00:00:00", "Visitantes": 31 },
    { "Fecha": "2026-01-20 00:00:00", "Visitantes": 28 },
    { "Fecha": "2026-01-19 00:00:00", "Visitantes": 26 },
    { "Fecha": "2026-01-18 00:00:00", "Visitantes": 25 },
    { "Fecha": "2026-01-17 00:00:00", "Visitantes": 27 },
    { "Fecha": "2026-01-16 00:00:00", "Visitantes": 18 },
    { "Fecha": "2026-01-15 00:00:00", "Visitantes": 22 },
    { "Fecha": "2026-01-14 00:00:00", "Visitantes": 15 },
    { "Fecha": "2026-01-13 00:00:00", "Visitantes": 15 },
    { "Fecha": "2026-01-12 00:00:00", "Visitantes": 8 },
    { "Fecha": "2026-01-11 00:00:00", "Visitantes": 9 },
    { "Fecha": "2026-01-10 00:00:00", "Visitantes": 15 },
    { "Fecha": "2026-01-09 00:00:00", "Visitantes": 16 },
    { "Fecha": "2026-01-08 00:00:00", "Visitantes": 12 },
    { "Fecha": "2026-01-07 00:00:00", "Visitantes": 16 },
    { "Fecha": "2026-01-06 00:00:00", "Visitantes": 14 },
    { "Fecha": "2026-01-05 00:00:00", "Visitantes": 24 },
    { "Fecha": "2026-01-04 00:00:00", "Visitantes": 15 },
    { "Fecha": "2026-01-03 00:00:00", "Visitantes": 8 },
    { "Fecha": "2026-01-02 00:00:00", "Visitantes": 15 },
    { "Fecha": "2026-01-01 00:00:00", "Visitantes": 14 },
    { "Fecha": "2025-12-31 00:00:00", "Visitantes": 10 },
    { "Fecha": "2025-12-30 00:00:00", "Visitantes": 35 },
    { "Fecha": "2025-12-29 00:00:00", "Visitantes": 13 },
    { "Fecha": "2025-12-28 00:00:00", "Visitantes": 13 },
    { "Fecha": "2025-12-27 00:00:00", "Visitantes": 26 },
    { "Fecha": "2025-12-26 00:00:00", "Visitantes": 26 },
    { "Fecha": "2025-12-25 00:00:00", "Visitantes": 12 },
    { "Fecha": "2025-12-24 00:00:00", "Visitantes": 14 }
  ]
}

# Inicializar cargando los datos base
@st.cache_data
def get_default_data():
    df = pd.DataFrame(DATA_JSON["records"])
    df["Fecha"] = pd.to_datetime(df["Fecha"])
    df["Visitantes"] = pd.to_numeric(df["Visitantes"])
    return df

df_base = get_default_data()

# Días de la semana en español para análisis y Feature Engineering
DIAS_MAP = {
    'Monday': 'Lunes', 'Tuesday': 'Martes', 'Wednesday': 'Miércoles',
    'Thursday': 'Jueves', 'Friday': 'Viernes', 'Saturday': 'Sábado', 'Sunday': 'Domingo'
}

# 3. BARRA LATERAL (FILTROS INTERACTIVOS Y CARGA DE ARCHIVO)
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3121/3121768.png", width=70)
st.sidebar.title("Configuración y Filtros")

# File Uploader opcional
uploaded_file = st.sidebar.file_uploader("Subir archivo de tráfico nuevo (Opcional)", type=["xlsx", "csv"])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith(".csv"):
            df_input = pd.read_csv(uploaded_file)
        else:
            df_input = pd.read_excel(uploaded_file)
        
        # Validar estructura básica necesaria
        if "Fecha" in df_input.columns and "Visitantes" in df_input.columns:
            df_input["Fecha"] = pd.to_datetime(df_input["Fecha"])
            df_input["Visitantes"] = pd.to_numeric(df_input["Visitantes"])
            df_working = df_input.copy()
            st.sidebar.success("¡Archivo cargado correctamente!")
        else:
            st.sidebar.error("El archivo debe contener las columnas 'Fecha' y 'Visitantes'. Usando datos por defecto.")
            df_working = df_base.copy()
    except Exception as e:
        st.sidebar.error(f"Error al procesar el archivo: {e}. Usando datos por defecto.")
        df_working = df_base.copy()
else:
    df_working = df_base.copy()

# Feature Engineering
if "Fecha" in df_working.columns:
    df_working["Día_Semana"] = df_working["Fecha"].dt.day_name().map(DIAS_MAP)

# --- Controles de Filtrado ---
st.sidebar.subheader("Filtros del Dashboard")

# Rango de fechas
if "Fecha" in df_working.columns:
    min_date = df_working["Fecha"].min().date()
    max_date = df_working["Fecha"].max().date()
    
    date_range = st.sidebar.date_input(
        "Rango Temporal",
        value=[min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )
else:
    date_range = None

# Umbral de volumen de visitantes
if "Visitantes" in df_working.columns:
    min_vis = int(df_working["Visitantes"].min())
    max_vis = int(df_working["Visitantes"].max())
    
    visitor_threshold = st.sidebar.slider(
        "Umbral de Visitantes Diarios",
        min_value=min_vis,
        max_value=max_vis,
        value=(min_vis, max_vis)
    )
else:
    visitor_threshold = None

# Filtro por Día de la semana
if "Día_Semana" in df_working.columns:
    days_list = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    selected_days = st.sidebar.multiselect(
        "Días de la semana",
        options=days_list,
        default=days_list
    )
else:
    selected_days = []

# --- Aplicar Filtros Reactivos ---
df_filtered = df_working.copy()

if "Fecha" in df_filtered.columns and date_range and len(date_range) == 2:
    df_filtered = df_filtered[
        (df_filtered["Fecha"].dt.date >= date_range[0]) & 
        (df_filtered["Fecha"].dt.date <= date_range[1])
    ]

if "Visitantes" in df_filtered.columns and visitor_threshold:
    df_filtered = df_filtered[
        (df_filtered["Visitantes"] >= visitor_threshold[0]) & 
        (df_filtered["Visitantes"] <= visitor_threshold[1])
    ]

if "Día_Semana" in df_filtered.columns and selected_days:
    df_filtered = df_filtered[df_filtered["Día_Semana"].isin(selected_days)]

# 4. DISEÑO DE INTERFAZ PRINCIPAL
# Encabezado de Metadatos
st.title("📊 Reporte de Tráfico Web - Canal ST_B2C")

with st.container():
    col_meta1, col_meta2 = st.columns([3, 1])
    with col_meta1:
        st.markdown(f"**Sujeto bajo análisis:** `{DATA_JSON['metadata']['entity_or_subject']}`")
        st.markdown(f"*{DATA_JSON['metadata']['general_summary']}*")
    with col_meta2:
        st.info(f"📅 **Periodo Base:** {DATA_JSON['metadata']['dates']}")

st.markdown("---")

# 5. TARJETAS DE KPIS GLOBALES (DINÁMICOS VS LÍNEA BASE)
if "Visitantes" in df_filtered.columns and not df_filtered.empty:
    current_total = int(df_filtered["Visitantes"].sum())
    current_mean = round(df_filtered["Visitantes"].mean(), 1)
    current_max = int(df_filtered["Visitantes"].max())
    current_min = int(df_filtered["Visitantes"].min())
    
    # Calcular delta relativo al baseline histórico para valor añadido
    delta_total = current_total - DATA_JSON["global_kpis_and_totals"]["total_visitantes"]
    delta_mean = round(current_mean - DATA_JSON["global_kpis_and_totals"]["promedio_diario"], 1)
else:
    current_total, current_mean, current_max, current_min = 0, 0, 0, 0
    delta_total, delta_mean = 0, 0

col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)

with col_kpi1:
    st.metric(
        label="Total de Visitantes",
        value=f"{current_total} visitantes",
        delta=f"{delta_total:+} vs base" if uploaded_file is None else None,
        help="Suma acumulada de visitas dentro del rango y filtros aplicados."
    )

with col_kpi2:
    st.metric(
        label="Promedio Diario",
        value=f"{current_mean} visitas/día",
        delta=f"{delta_mean:+} vs base" if uploaded_file is None else None,
        help="Media de tráfico diario registrado en el sitio bajo el filtro actual."
    )

with col_kpi3:
    st.metric(
        label="Pico Máximo de Tráfico",
        value=f"{current_max} visitantes",
        help="Mayor volumen de tráfico diario registrado según filtros actuales."
    )

with col_kpi4:
    st.metric(
        label="Tráfico Mínimo Registrado",
        value=f"{current_min} visitantes",
        help="Menor volumen de tráfico diario registrado según filtros actuales."
    )

st.markdown("---")

# 6. ORGANIZACIÓN POR PESTAÑAS (TABS)
tab_visualizacion, tab_datos_origen = st.tabs([
    "📈 Análisis de Tráfico y Tendencias", 
    "🗃️ Tabla de Datos: st_b2c_daily_visitors"
])

# --- PESTAÑA 1: VISUALIZACIONES ---
with tab_visualizacion:
    if df_filtered.empty:
        st.warning("No hay datos disponibles para los filtros seleccionados. Intente ajustar el rango en la barra lateral.")
    else:
        st.subheader("Análisis Visual del Comportamiento Temporal")
        
        # Fila para Gráfico A (Evolución) y Gráfico B (Distribución)
        col_chart1, col_chart2 = st.columns([2, 1])
        
        with col_chart1:
            if "Fecha" in df_filtered.columns and "Visitantes" in df_filtered.columns:
                # Asegurar orden cronológico para gráfico lineal
                df_chart_a = df_filtered.sort_values(by="Fecha")
                
                fig_line = px.area(
                    df_chart_a, 
                    x="Fecha", 
                    y="Visitantes",
                    title="Evolución Diaria del Tráfico de Visitantes (Canal B2C)",
                    labels={"Fecha": "Fecha de Análisis", "Visitantes": "Cantidad de Visitantes"},
                    template="plotly_white",
                    color_discrete_sequence=["#1f77b4"]
                )
                
                # Línea de referencia del Promedio Global Histórico (18.0)
                fig_line.add_hline(
                    y=18.0, 
                    line_dash="dash", 
                    line_color="red", 
                    annotation_text="Media Histórica (18.0)",
                    annotation_position="bottom left"
                )
                
                # Anotación del Pico Máximo Histórico si está dentro de los filtros
                if not df_chart_a[df_chart_a["Fecha"] == "2025-12-30"].empty:
                    fig_line.add_annotation(
                        x="2025-12-30",
                        y=35,
                        text="Pico Histórico (35)",
                        showarrow=True,
                        arrowhead=2,
                        ax=40,
                        ay=-40,
                        bgcolor="rgba(255, 255, 255, 0.8)",
                        bordercolor="#1f77b4"
                    )
                
                fig_line.update_layout(
                    hovermode="x unified",
                    xaxis_title="",
                    yaxis_title="Visitantes",
                    margin=dict(l=40, r=40, t=50, b=40)
                )
                
                st.plotly_chart(fig_line, use_container_width=True)
        
        with col_chart2:
            if "Visitantes" in df_filtered.columns:
                fig_box = px.box(
                    df_filtered,
                    y="Visitantes",
                    points="all",
                    title="Distribución y Rango del Tráfico",
                    labels={"Visitantes": "Tráfico (Visitantes)"},
                    template="plotly_white",
                    color_discrete_sequence=["#2ca02c"]
                )
                fig_box.update_layout(
                    margin=dict(l=40, r=40, t=50, b=40)
                )
                st.plotly_chart(fig_box, use_container_width=True)

        # Fila adicional para desglose de estacionalidad
        st.subheader("Análisis de Estacionalidad Semanal")
        if "Día_Semana" in df_filtered.columns and "Visitantes" in df_filtered.columns:
            # Calcular promedio por día de la semana para detectar patrones de consumo
            order_days = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
            df_day_agg = df_filtered.groupby("Día_Semana")["Visitantes"].mean().reindex(order_days).reset_index()
            df_day_agg = df_day_agg.dropna()
            
            fig_bar = px.bar(
                df_day_agg,
                x="Día_Semana",
                y="Visitantes",
                title="Tráfico Promedio por Día de la Semana",
                labels={"Día_Semana": "Día de la Semana", "Visitantes": "Visitas Promedio"},
                template="plotly_white",
                color="Visitantes",
                color_continuous_scale="Viridis"
            )
            fig_bar.update_layout(
                xaxis_title="",
                yaxis_title="Promedio de Visitantes"
            )
            st.plotly_chart(fig_bar, use_container_width=True)

# --- PESTAÑA 2: TABLA DE DATOS ---
with tab_datos_origen:
    st.subheader("Auditoría y Exportación de Registros")
    st.markdown("A continuación se muestra la tabla interactiva basada en los filtros activos en la barra lateral.")
    
    if df_filtered.empty:
        st.warning("No hay registros para mostrar.")
    else:
        # Preparación de la visualización
        df_display = df_filtered.copy()
        if "Fecha" in df_display.columns:
            # Limpiar la estampa de tiempo
            df_display["Fecha_Formateada"] = df_display["Fecha"].dt.strftime("%Y-%m-%d")
        
        # Botón para descargar los datos filtrados en CSV
        @st.cache_data
        def convert_df_to_csv(df):
            return df.to_csv(index=False).encode('utf-8')
        
        csv_data = convert_df_to_csv(df_display)
        
        col_actions1, col_actions2 = st.columns([6, 1])
        with col_actions2:
            st.download_button(
                label="📥 Descargar CSV",
                data=csv_data,
                file_name="trafico_b2c_filtrado.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        # Renderizado del dataframe con estilo y formato condicional
        # Eliminamos temporalmente la columna original datetime para mejorar legibilidad
        cols_to_show = ["Fecha_Formateada", "Visitantes", "Día_Semana"]
        cols_to_show = [c for c in cols_to_show if c in df_display.columns]
        
        df_show = df_display[cols_to_show].rename(columns={"Fecha_Formateada": "Fecha de Registro"})
        
        if "Visitantes" in df_show.columns:
            st.dataframe(
                df_show.style.background_gradient(subset=["Visitantes"], cmap="YlGnBu"),
                use_container_width=True,
                column_config={
                    "Fecha de Registro": st.column_config.DateColumn("Fecha de Registro"),
                    "Visitantes": st.column_config.NumberColumn("Total de Visitantes", format="%d"),
                    "Día_Semana": st.column_config.TextColumn("Día de la Semana")
                }
            )
        else:
            st.dataframe(df_show, use_container_width=True)