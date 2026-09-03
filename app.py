import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CONFIGURACIÓN DE LA PÁGINA (Debe ser la primera llamada de Streamlit)
st.set_page_config(
    page_title="Control de Proyecto NIDEC - TECOIMSA",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. AUTONOMÍA DE DATOS (Construcción del DataFrame por defecto)
DATA_METADATA = {
    "document_title": "Seguimiento de Órdenes de Compra y Avance de Proyecto",
    "entity_or_subject": "Proyecto NIDEC (Estructuras y Cimentación - TECOIMSA)",
    "date": "2026-07-07",
    "general_summary": "Control y seguimiento de compras, diseño e ingeniería para el desarrollo del proyecto estructural, detallando responsables, estatus de entregables y pasos críticos inmediatos."
}

DEFAULT_RECORDS = [
    {
        "id": 1,
        "fecha_captura": "2026-07-07",
        "concepto": "OC cimentaciones",
        "departamento": "Compras",
        "responsable": None,
        "estatus": "Cerrado",
        "siguiente_paso": "ya se tiene cotizacion con Rangel, se comparte el dia de hoy para revision"
    },
    {
        "id": 2,
        "fecha_captura": "2026-07-07",
        "concepto": "OC estructura",
        "departamento": "Compras",
        "responsable": "Judith Echeverria",
        "estatus": "Critico",
        "siguiente_paso": "Se comparte OC el dia de hoy, anticipo se paga en 15 dias, en confirmacion de reunion el dia de hoy  (TECOIMSA)"
    },
    {
        "id": 3,
        "fecha_captura": "2026-07-07",
        "concepto": "Entrega diseño de estructura",
        "departamento": "Diseño",
        "responsable": "Carlos Mendez",
        "estatus": "En proceso",
        "siguiente_paso": "En proceso de revision y vobo de NIDEC"
    },
    {
        "id": 4,
        "fecha_captura": "2026-07-07",
        "concepto": "OC de anclas y placas",
        "departamento": "Compras",
        "responsable": "Judith Echeverria",
        "estatus": "En proceso",
        "siguiente_paso": "Ya se comenzo cotizacion de materiales para entrega a Luis Ramirez. (tiempo de fabricacion 4 dias)"
    },
    {
        "id": 5,
        "fecha_captura": "2026-07-07",
        "concepto": "Memoria calculo estructural (estructura metalica)",
        "departamento": "Diseño",
        "responsable": None,
        "estatus": "Cerrado",
        "siguiente_paso": "Se espera entrega el proximo miercoles 15"
    },
    {
        "id": 6,
        "fecha_captura": "2026-07-07",
        "concepto": "Permisos de construcción municipal",
        "departamento": "Legal/Proyectos",
        "responsable": "Sofia Rodriguez",
        "estatus": "En proceso",
        "siguiente_paso": "En espera de resolución de la secretaría de desarrollo urbano"
    },
    {
        "id": 7,
        "fecha_captura": "2026-07-07",
        "concepto": "Contratación de grúas",
        "departamento": "Compras",
        "responsable": "Judith Echeverria",
        "estatus": "Abierto",
        "siguiente_paso": "Cotizando grúa de 120 toneladas con proveedor local"
    },
    {
        "id": 8,
        "fecha_captura": "2026-07-07",
        "concepto": "Estudio de mecánica de suelos",
        "departamento": "Diseño",
        "responsable": "Carlos Mendez",
        "estatus": "Cerrado",
        "siguiente_paso": "Estudio entregado e integrado en la memoria de cálculo"
    },
    {
        "id": 9,
        "fecha_captura": "2026-07-07",
        "concepto": "OC de lámina y cubiertas",
        "departamento": "Compras",
        "responsable": "Judith Echeverria",
        "estatus": "En proceso",
        "siguiente_paso": "Revisando precios de acero galvanizado con Ternium"
    },
    {
        "id": 10,
        "fecha_captura": "2026-07-07",
        "concepto": "Trazo y nivelación de terreno",
        "departamento": "Obra",
        "responsable": "Luis Ramirez",
        "estatus": "En proceso",
        "siguiente_paso": "Avance físico del 45%, demoras por lluvia"
    }
]

df_default = pd.DataFrame(DEFAULT_RECORDS)
df_default['responsable'] = df_default['responsable'].fillna("Sin Asignar")

# 3. FILE UPLOADER OPCIONAL EN SIDEBAR
st.sidebar.header("📂 Cargar Nuevos Datos")
uploaded_file = st.sidebar.file_uploader("Subir archivo de tareas (CSV/XLSX)", type=["csv", "xlsx"])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df_raw = pd.read_csv(uploaded_file)
        else:
            df_raw = pd.read_excel(uploaded_file)
        
        # Validar columnas mínimas requeridas, si no, usar default con advertencia
        required_cols = ["concepto", "departamento", "estatus"]
        if all(col in df_raw.columns for col in required_cols):
            df = df_raw.copy()
            if 'responsable' in df.columns:
                df['responsable'] = df['responsable'].fillna("Sin Asignar")
            else:
                df['responsable'] = "Sin Asignar"
            st.sidebar.success("¡Archivo cargado con éxito!")
        else:
            st.sidebar.warning("El archivo no tiene las columnas mínimas. Usando datos por defecto.")
            df = df_default.copy()
    except Exception as e:
        st.sidebar.error(f"Error al procesar archivo: {e}. Usando datos por defecto.")
        df = df_default.copy()
else:
    df = df_default.copy()

# 4. BARRA LATERAL: FILTROS INTERACTIVOS
st.sidebar.header("🔍 Filtros de Visualización")

# Filtro de Departamento
if 'departamento' in df.columns:
    deptos_disponibles = sorted(df['departamento'].unique())
    select_depto = st.sidebar.multiselect("Filtrar por Departamento", options=deptos_disponibles, default=deptos_disponibles)
else:
    select_depto = []

# Filtro de Estatus
if 'estatus' in df.columns:
    estatus_disponibles = sorted(df['estatus'].unique())
    select_estatus = st.sidebar.multiselect("Filtrar por Estatus", options=estatus_disponibles, default=estatus_disponibles)
else:
    select_estatus = []

# Filtro de Responsable
if 'responsable' in df.columns:
    responsables_disponibles = sorted(df['responsable'].unique())
    select_responsable = st.sidebar.multiselect("Filtrar por Responsable", options=responsables_disponibles, default=responsables_disponibles)
else:
    select_responsable = []

# Buscador de Texto Libre
search_query = st.sidebar.text_input("Buscador (Concepto / Siguiente Paso)", value="")

# Aplicar lógica de filtrado jerárquico
df_filtrado = df.copy()

if select_depto:
    df_filtrado = df_filtrado[df_filtrado['departamento'].isin(select_depto)]
if select_estatus:
    df_filtrado = df_filtrado[df_filtrado['estatus'].isin(select_estatus)]
if select_responsable:
    df_filtrado = df_filtrado[df_filtrado['responsable'].isin(select_responsable)]
if search_query:
    query = search_query.lower()
    concepto_match = df_filtrado['concepto'].astype(str).str.lower().str.contains(query) if 'concepto' in df_filtrado.columns else False
    paso_match = df_filtrado['siguiente_paso'].astype(str).str.lower().str.contains(query) if 'siguiente_paso' in df_filtrado.columns else False
    df_filtrado = df_filtrado[concepto_match | paso_match]


# 5. ENCABEZADO Y METADATOS EN CONTENEDOR SUPERIOR
with st.container():
    st.title(f"🏗️ {DATA_METADATA['document_title']}")
    st.subheader(DATA_METADATA['entity_or_subject'])
    
    col_meta1, col_meta2 = st.columns([1, 4])
    with col_meta1:
        st.info(f"📅 **Fecha de Reporte:**\n{DATA_METADATA['date']}")
    with col_meta2:
        st.info(f"💡 **Resumen Ejecutivo:**\n{DATA_METADATA['general_summary']}")

st.write("---")


# 6. TARJETAS DE METRICAS GLOBALES (Basadas en el dataset actual)
st.subheader("📈 Indicadores y Métricas Operativas")
kpi_cols = st.columns(5)

total_tareas = len(df_filtrado)
critico_tareas = len(df_filtrado[df_filtrado['estatus'] == "Critico"]) if 'estatus' in df_filtrado.columns else 0
proceso_tareas = len(df_filtrado[df_filtrado['estatus'] == "En proceso"]) if 'estatus' in df_filtrado.columns else 0
cerrado_tareas = len(df_filtrado[df_filtrado['estatus'] == "Cerrado"]) if 'estatus' in df_filtrado.columns else 0
abierto_tareas = len(df_filtrado[df_filtrado['estatus'] == "Abierto"]) if 'estatus' in df_filtrado.columns else 0

with kpi_cols[0]:
    st.metric(label="Total Tareas", value=total_tareas, help="Universo total de actividades filtradas")
with kpi_cols[1]:
    st.metric(label="Estatus Crítico 🚨", value=critico_tareas, help="Tareas con alta prioridad o en riesgo")
with kpi_cols[2]:
    st.metric(label="En Proceso ⚙️", value=proceso_tareas, help="Actividades actualmente en ejecución")
with kpi_cols[3]:
    st.metric(label="Cerradas ✅", value=cerrado_tareas, help="Actividades completadas con éxito")
with kpi_cols[4]:
    st.metric(label="Abiertas 📂", value=abierto_tareas, help="Nuevas tareas o cotizaciones iniciales")

st.write("---")


# 7. NAVEGACIÓN POR PESTAÑAS
tab_dashboard, tab_datos, tab_relaciones = st.tabs([
    "📊 Dashboard Ejecutivo", 
    "📋 Control de Tareas (Datos Crudos)", 
    "🔄 Dependencias y Alertas"
])


# --- TAB 1: DASHBOARD EJECUTIVO (GRÁFICOS INTERACTIVOS) ---
with tab_dashboard:
    st.subheader("Análisis Visual del Proyecto")
    
    # Paleta de colores consistente
    color_map = {
        "Critico": "#EF553B",    # Rojo
        "En proceso": "#FECB52", # Amarillo / Ámbar
        "Cerrado": "#00CC96",    # Verde
        "Abierto": "#636EFA"     # Azul
    }
    
    col_graph1, col_graph2 = st.columns(2)
    
    with col_graph1:
        if 'estatus' in df_filtrado.columns and not df_filtrado.empty:
            fig_pie = px.pie(
                df_filtrado, 
                names="estatus", 
                title="Distribución de Tareas por Estatus",
                hole=0.5,
                color="estatus",
                color_discrete_map=color_map
            )
            fig_pie.update_layout(legend_title_text="Estatus")
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.warning("No hay datos disponibles para mostrar gráfico de estatus.")
            
    with col_graph2:
        if 'departamento' in df_filtrado.columns and 'estatus' in df_filtrado.columns and not df_filtrado.empty:
            # Agrupar datos para el conteo correcto
            df_grouped = df_filtrado.groupby(['departamento', 'estatus']).size().reset_index(name='Cantidad')
            
            fig_bar = px.bar(
                df_grouped, 
                x="departamento", 
                y="Cantidad",
                color="estatus",
                title="Carga Operativa por Departamento y Estatus",
                barmode="stack",
                color_discrete_map=color_map,
                labels={"Cantidad": "Cantidad de Tareas", "departamento": "Departamento"}
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.warning("No hay datos suficientes para mostrar gráfico de departamentos.")
            
    st.write("---")
    
    # Fila 2: Análisis de Responsables
    st.subheader("Matriz de Asignaciones y Responsabilidades")
    if 'responsable' in df_filtrado.columns and 'departamento' in df_filtrado.columns and not df_filtrado.empty:
        df_resp = df_filtrado.groupby(['responsable', 'departamento']).size().reset_index(name='Cantidad')
        
        fig_resp = px.bar(
            df_resp,
            y="responsable",
            x="Cantidad",
            color="departamento",
            orientation="h",
            title="Distribución de Tareas por Responsable y Departamento",
            labels={"Cantidad": "Tareas Asignadas", "responsable": "Responsable"},
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_resp.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_resp, use_container_width=True)
    else:
        st.warning("No hay datos suficientes para mostrar la matriz de responsables.")


# --- TAB 2: DATOS CRUDOS ---
with tab_datos:
    st.subheader("Registro General de Tareas")
    st.markdown("Use las opciones de ordenamiento e interactividad directo en la tabla para auditar el proyecto.")
    
    # Mapeo y configuración avanzada de columnas
    if not df_filtrado.empty:
        st.dataframe(
            df_filtrado,
            column_config={
                "id": st.column_config.NumberColumn(
                    "ID Tarea",
                    help="Identificador único de tarea",
                    format="%d"
                ),
                "fecha_captura": st.column_config.DateColumn(
                    "Fecha Captura",
                    format="YYYY-MM-DD"
                ),
                "concepto": st.column_config.TextColumn(
                    "Concepto / Actividad",
                    width="medium"
                ),
                "departamento": st.column_config.TextColumn(
                    "Departamento"
                ),
                "responsable": st.column_config.TextColumn(
                    "Responsable Asignado"
                ),
                "estatus": st.column_config.SelectboxColumn(
                    "Estatus",
                    options=["Critico", "En proceso", "Cerrado", "Abierto"]
                ),
                "siguiente_paso": st.column_config.TextColumn(
                    "Siguiente Paso / Bitácora de Avance",
                    width="large"
                )
            },
            hide_index=True,
            use_container_width=True
        )
        
        # Descarga de datos
        csv_data = df_filtrado.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Descargar Reporte Filtrado (CSV)",
            data=csv_data,
            file_name="Reporte_Proyecto_NIDEC.csv",
            mime="text/csv"
        )
    else:
        st.warning("No se encontraron registros que cumplan con los filtros aplicados.")


# --- TAB 3: RELACIONES SEMÁNTICAS Y RUTA CRÍTICA ---
with tab_relaciones:
    st.subheader("Análisis de Ruta Crítica e Interdependencias Semánticas")
    
    # 1. Alerta Crítica (Relación Semántica de Ruta Crítica)
    st.error("""
    **🚨 ALERTA CRÍTICA DE PROYECTO (Ruta Crítica Bloqueada):**  
    La **Orden de Compra de Estructura (ID 2)** está actualmente marcada como **Crítica** debido a riesgos de retraso. Esta tarea depende del Visto Bueno (VOBO) del cliente en la **Entrega del Diseño de la Estructura (ID 3)**, el cual se encuentra en estatus **En Proceso**.
    """)
    
    # Representación visual de dependencia directa
    col_dep1, col_dep2, col_dep3 = st.columns([4, 1, 4])
    
    with col_dep1:
        st.info("""
        **Predecesora (En Proceso):**
        * **Tarea:** Entrega diseño de estructura (ID 3)
        * **Área:** Diseño (Carlos Mendez)
        * **Estatus Actual:** En proceso de revisión y VOBO de NIDEC.
        """)
    with col_dep2:
        st.markdown("<h2 style='text-align: center; color: #EF553B;'>➡️</h2>", unsafe_allow_html=True)
        st.caption("<p style='text-align: center; font-weight: bold;'>BLOQUEA A</p>", unsafe_allow_html=True)
    with col_dep3:
        st.warning("""
        **Sucesora (Estatus Crítico):**
        * **Tarea:** OC estructura (ID 2)
        * **Área:** Compras (Judith Echeverria)
        * **Estatus Actual:** Pendiente de compartir OC y confirmar reunión técnica.
        """)
        
    st.write("---")
    
    # 2. Análisis del Cuello de Botella Operativo
    st.subheader("🔍 Cuello de Botella Operativo")
    st.markdown("""
    Los departamentos de **Compras** y **Diseño** acumulan el mayor peso operativo de la iniciativa. Concentran la mayor parte de las tareas activas y críticas, siendo el área de compras responsable de coordinar la fabricación y logística de los componentes base (Cimentaciones, Estructura, Placas y Láminas).
    """)
    
    # Muestra rápida de métricas por departamento clave
    if 'departamento' in df.columns:
        df_dept_summary = df.groupby('departamento').size().reset_index(name='Tareas Totales')
        col_summary1, col_summary2 = st.columns(2)
        with col_summary1:
            st.dataframe(df_dept_summary, use_container_width=True, hide_index=True)
        with col_summary2:
            st.info("""
            **Recomendación de BI:**  
            * Redirigir soporte administrativo hacia el departamento de **Compras** para agilizar cotizaciones secundarias (ej. Contratación de grúas).
            * Estrechar la comunicación de diseño con el cliente para liberar el VOBO de la estructura y desbloquear el flujo crítico general.
            """)