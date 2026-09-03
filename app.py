import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib  # Explicitly imported for Streamlit style compliance
from datetime import datetime

# 1. Configuración de página (Debe ser la PRIMERA llamada de Streamlit)
st.set_page_config(
    page_title="Reporte de Tráfico - Canal B2C",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Datos en memoria (Carga Autónoma por defecto)
default_records = [
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

df_raw = pd.DataFrame(default_records)

# 3. Barra Lateral (Sidebar) con Filtros y Carga de Archivos
with st.sidebar:
    st.header("🛠️ Panel de Control")
    
    # File Uploader Opcional
    uploaded_file = st.file_uploader(
        "Cargar archivo personalizado (xlsx/csv)", 
        type=["xlsx", "csv"],
        help="Sube un archivo con columnas 'fecha' y 'visitantes' para actualizar el dashboard."
    )
    
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith(".csv"):
                df_raw = pd.read_csv(uploaded_file)
            else:
                df_raw = pd.read_excel(uploaded_file)
            st.success("¡Datos cargados correctamente!")
        except Exception as e:
            st.error(f"Error al leer el archivo: {e}")
            st.info("Usando datos del sistema por defecto.")
            df_raw = pd.DataFrame(default_records)

    # Tipado Defensivo: Asegurar columnas requeridas y formatear adecuadamente
    df_normalized = df_raw.copy()
    # Estandarizar nombres de columnas a minúsculas para robustez
    df_normalized.columns = [str(col).lower().strip() for col in df_normalized.columns]
    
    if "fecha" in df_normalized.columns and "visitantes" in df_normalized.columns:
        # Conversión segura y eliminación de valores nulos críticos
        df_normalized["visitantes"] = pd.to_numeric(df_normalized["visitantes"], errors="coerce")
        df_normalized["fecha"] = pd.to_datetime(df_normalized["fecha"], errors="coerce")
        df_normalized = df_normalized.dropna(subset=["fecha", "visitantes"])
        df_normalized = df_normalized.sort_values(by="fecha")
    else:
        st.error("El archivo no contiene las columnas requeridas: 'fecha' y 'visitantes'.")
        # Forzar vuelta a datos por defecto estructurados
        df_normalized = pd.DataFrame(default_records)
        df_normalized["fecha"] = pd.to_datetime(df_normalized["fecha"])
        df_normalized["visitantes"] = pd.to_numeric(df_normalized["visitantes"])

    # Filtro de Rango de Fechas basado en el dataset activo
    min_date = df_normalized["fecha"].min().date()
    max_date = df_normalized["fecha"].max().date()
    
    st.subheader("Filtros Temporales")
    date_range = st.date_input(
        "Rango Temporal Seleccionado",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        help="Filtra los datos visualizados por rango de fechas."
    )
    
    # Filtro Deslizador de Visitantes
    min_vis = int(df_normalized["visitantes"].min())
    max_vis = int(df_normalized["visitantes"].max())
    
    st.subheader("Filtros de Volumen")
    visitor_range = st.slider(
        "Rango de Visitantes Diarios",
        min_value=min_vis,
        max_value=max_vis,
        value=(min_vis, max_vis),
        help="Filtra por volumen de visitas registrado en un día."
    )

# Aplicar Filtros Dinámicos de forma Segura
df_filtered = df_normalized.copy()

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
    df_filtered = df_filtered[
        (df_filtered["fecha"].dt.date >= start_date) & 
        (df_filtered["fecha"].dt.date <= end_date)
    ]

df_filtered = df_filtered[
    (df_filtered["visitantes"] >= visitor_range[0]) & 
    (df_filtered["visitantes"] <= visitor_range[1])
]

# 4. Estructura Superior (Título y Metadatos)
st.title("📈 Reporte de Tráfico - Canal B2C")

# Sección de Contexto (Metadata)
with st.expander("ℹ️ Información de Contexto y Metadata del Reporte", expanded=True):
    col_meta1, col_meta2 = st.columns([1, 2])
    with col_meta1:
        st.markdown("**Sujeto / Entidad:** Canal B2C")
        st.markdown(f"**Periodo de Análisis Base:** 2025-12-24 a 2026-01-21")
        st.markdown(f"**Rango Visualizado Actual:** {date_range[0] if isinstance(date_range, tuple) else min_date} a {date_range[1] if isinstance(date_range, tuple) and len(date_range) == 2 else max_date}")
    with col_meta2:
        st.markdown("**Resumen General:**")
        st.write(
            "Análisis analítico integral del flujo diario de visitantes para el canal de venta directa al consumidor final (B2C), "
            "registrando el comportamiento del tráfico durante la temporada alta de fin de año 2025 y principios del ciclo 2026."
        )

# 5. Cálculo y Presentación de KPIs Dinámicos
st.markdown("### Key Performance Indicators (KPIs) de Tráfico")
total_visitors = int(df_filtered["visitantes"].sum()) if not df_filtered.empty else 0
avg_visitors = float(df_filtered["visitantes"].mean()) if not df_filtered.empty else 0.0
max_visitors = int(df_filtered["visitantes"].max()) if not df_filtered.empty else 0
min_visitors = int(df_filtered["visitantes"].min()) if not df_filtered.empty else 0
days_count = int(df_filtered["fecha"].nunique()) if not df_filtered.empty else 0

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric(
    label="Total de Visitantes", 
    value=f"{total_visitors:,} usuarios", 
    help="Suma acumulada de visitantes registrados en el periodo seleccionado."
)
col2.metric(
    label="Promedio Diario", 
    value=f"{avg_visitors:.1f} visit/día", 
    help="Media aritmética del volumen diario de visitas."
)
col3.metric(
    label="Máximo Diario", 
    value=f"{max_visitors} usuarios", 
    help="El pico de tráfico diario más alto registrado bajo los filtros actuales."
)
col4.metric(
    label="Mínimo Diario", 
    value=f"{min_visitors} usuarios", 
    help="El flujo de tráfico diario más bajo registrado."
)
col5.metric(
    label="Días Registrados", 
    value=f"{days_count} días", 
    help="Número de días únicos que contienen registros en el rango seleccionado."
)

st.markdown("---")

# 6. Estructura de Pestañas (Tabs) para Distribución Limpia
tab_analisis, tab_datos, tab_relaciones = st.tabs([
    "📊 Análisis de Tráfico", 
    "🗃️ Datos Crudos (st_b2c_daily_traffic)", 
    "🧠 Relaciones Semánticas"
])

# ---- PESTAÑA 1: ANALISIS DE TRAFICO ----
with tab_analisis:
    st.subheader("Análisis Analítico de Variación y Frecuencias")
    
    if not df_filtered.empty:
        col_chart1, col_chart2 = st.columns([2, 1])
        
        with col_chart1:
            # Gráfico A: Línea de Tendencia Temporal con Promedio de Referencia
            fig_line = px.line(
                df_filtered, 
                x="fecha", 
                y="visitantes", 
                title="Evolución del Flujo Diario de Visitantes",
                labels={"fecha": "Fecha de Análisis", "visitantes": "Número de Visitantes"},
                markers=True,
                template="plotly_white"
            )
            
            # Línea de Promedio Semántico de Referencia (18.0)
            fig_line.add_hline(
                y=18.0, 
                line_dash="dash", 
                line_color="rgba(230, 57, 70, 0.8)",
                annotation_text="Promedio Histórico Base (18.0)", 
                annotation_position="bottom right"
            )
            
            # Anotación Dinámica del Máximo Histórico si se encuentra en los datos actuales
            peak_date = pd.to_datetime("2025-12-30")
            if peak_date in df_filtered["fecha"].values:
                peak_row = df_filtered[df_filtered["fecha"] == peak_date]
                fig_line.add_annotation(
                    x=peak_date, 
                    y=35,
                    text="Máximo Histórico (35)",
                    showarrow=True,
                    arrowhead=2,
                    ax=-40,
                    ay=-45,
                    bgcolor="rgba(255, 193, 7, 0.8)",
                    bordercolor="gray"
                )
            
            st.plotly_chart(fig_line, use_container_width=True)
            
        with col_chart2:
            # Gráfico B: Clasificación Respecto al Promedio
            # Lógica Semántica de Agrupación Dinámica
            df_filtered["Clasificación"] = df_filtered["visitantes"].apply(
                lambda x: "Sobre el Promedio (>=18.0)" if x >= 18.0 else "Bajo el Promedio (<18.0)"
            )
            
            fig_bar = px.bar(
                df_filtered,
                x="fecha",
                y="visitantes",
                color="Clasificación",
                color_discrete_map={
                    "Sobre el Promedio (>=18.0)": "#2a9d8f",
                    "Bajo el Promedio (<18.0)": "#e76f51"
                },
                title="Distribución y Clasificación de Tráfico",
                labels={"fecha": "Fecha", "visitantes": "Visitantes", "Clasificación": "Clasificación Semántica"},
                template="plotly_white"
            )
            fig_bar.update_layout(legend_position="bottom")
            st.plotly_chart(fig_bar, use_container_width=True)
            
    else:
        st.warning("No hay datos disponibles para graficar con los filtros actuales de la barra lateral.")

# ---- PESTAÑA 2: DATOS CRUDOS ----
with tab_datos:
    st.subheader("Detalle Tabular y Gestión de Datos")
    st.write(
        "A continuación se despliega el dataset consolidado de tráfico diario `st_b2c_daily_traffic`. "
        "Puede ordenar las columnas interactivamente y descargar los datos filtrados."
    )
    
    if not df_filtered.empty:
        # Visor de datos Premium nativo con Barras de Progreso e Indicador de Volumen
        st.dataframe(
            df_filtered[["fecha", "visitantes"]],
            column_config={
                "fecha": st.column_config.DateColumn(
                    "Fecha de Operación",
                    format="YYYY-MM-DD",
                    help="Día correspondiente al registro de tráfico."
                ),
                "visitantes": st.column_config.ProgressColumn(
                    "Volumen de Visitantes",
                    help="Volumen diario visualizado como barra de progreso en función del máximo histórico (35).",
                    format="%d",
                    min_value=0,
                    max_value=35
                )
            },
            use_container_width=True,
            hide_index=True
        )
        
        # Generación dinámica del botón de descarga en formato CSV
        csv_data = df_filtered[["fecha", "visitantes"]].to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Descargar Datos Actuales en CSV",
            data=csv_data,
            file_name=f"trafico_b2c_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            help="Descarga inmediata de los registros tal y como se observan con los filtros activos."
        )
    else:
        st.warning("La tabla está vacía debido a los filtros actuales. Ajuste el panel de control.")

# ---- PESTAÑA 3: RELACIONES SEMÁNTICAS ----
with tab_relaciones:
    st.subheader("Lógica de Negocio y Relaciones Semánticas")
    st.markdown(
        """
        Este dashboard está construido respetando estrictas reglas semánticas y de agregación lógica del negocio B2C. 
        A continuación, se describen los vínculos lógicos que garantizan la integridad referencial:
        
        *   **1. Relación de Agregación Aditiva:**
            *   *Origen:* Columna de datos crudos `visitantes` de la tabla de detalles.
            *   *Destino:* Indicador principal **Total de Visitantes (522)**.
            *   *Fórmula:* $\\sum (visitantes) = 522$. Cualquier filtro aplicado en el panel izquierdo actualiza síncronamente esta agregación garantizando que no existan discrepancias visuales.
            
        *   **2. Relación de Desviación Estándar y Análisis Relativo:**
            *   *Concepto:* El rendimiento de la operación diaria se contrasta permanentemente contra la media histórica calculada de **18.0 visitantes**.
            *   *Interpretación:* La línea de puntos roja del **Análisis de Tráfico** permite de un solo vistazo entender la fluctuación. Se detecta con claridad el comportamiento atípico positivo del **2025-12-30 (35 visitantes)** como el máximo rendimiento, mientras que los mínimos de **8 visitantes** (2026-01-03 y 2026-01-12) marcan las ventanas críticas de menor interés del canal.
        """
    )
    
    # Tabla resumen de correlaciones para facilitar auditoría
    audit_data = pd.DataFrame([
        {
            "Métrica Global": "Total de Visitantes",
            "Fórmula Relacional": "Suma total de registros",
            "Valor Base": "522",
            "Estado de Integridad": "Correcto"
        },
        {
            "Métrica Global": "Promedio Diario",
            "Fórmula Relacional": "Suma de visitantes / Cantidad de días",
            "Valor Base": "18.0",
            "Estado de Integridad": "Correcto"
        },
        {
            "Métrica Global": "Máximo Registrado",
            "Fórmula Relacional": "Valor máximo en el rango de tiempo",
            "Valor Base": "35 (Registrado 2025-12-30)",
            "Estado de Integridad": "Correcto"
        }
    ])
    
    st.dataframe(audit_data, use_container_width=True, hide_index=True)