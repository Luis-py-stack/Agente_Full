import streamlit as st
import pandas as pd
import plotly.express as px
import io

# 1. CONFIGURACIÓN DE LA PÁGINA (Debe ser la primera instrucción de Streamlit)
st.set_page_config(
    page_title="Control de Adquisiciones y Estructuras",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. AUTONOMÍA DE DATOS (Datos por defecto basados en el JSON proporcionado)
DEFAULT_METADATA = {
    "document_title": "Control y Seguimiento de Adquisiciones y Diseños de Estructura",
    "entity_or_subject": "Proyecto de Construcción e Infraestructura (Menciones a NIDEC y TECOIMSA)",
    "date": "2026-07-07",
    "general_summary": "Monitoreo de tareas críticas, órdenes de compra (OC) y entregables de diseño estructural, detallando responsables, estatus de avance y siguientes acciones inmediatas."
}

@st.cache_data
def get_default_data():
    records = [
        {
            "ID": 1,
            "Fecha captura": "2026-07-07 00:00:00",
            "Concepto": "OC cimentaciones",
            "Departamento": "Compras",
            "Responsable": None,
            "Estatus": "Cerrado",
            "Siguiente paso": "ya se tiene cotizacion con Rangel, se comparte el dia de hoy para revision"
        },
        {
            "ID": 2,
            "Fecha captura": "2026-07-07 00:00:00",
            "Concepto": "OC estructura",
            "Departamento": "Compras",
            "Responsable": "Judith Echeverria",
            "Estatus": "Critico",
            "Siguiente paso": "Se comparte OC el dia de hoy, anticipo se paga en 15 dias, en confirmacion de reunion el dia de hoy  (TECOIMSA)"
        },
        {
            "ID": 3,
            "Fecha captura": "2026-07-07 00:00:00",
            "Concepto": "Entrega diseño de estructura",
            "Departamento": "Diseño",
            "Responsable": "Carlos Mendez",
            "Estatus": "En proceso",
            "Siguiente paso": "En proceso de revision y vobo de NIDEC"
        },
        {
            "ID": 4,
            "Fecha captura": "2026-07-07 00:00:00",
            "Concepto": "OC de anclas y placas",
            "Departamento": "Compras",
            "Responsable": "Judith Echeverria",
            "Estatus": "En proceso",
            "Siguiente paso": "Ya se comenzo cotizacion de materiales para entrega a Luis Ramirez. (tiempo de fabricacion 4 dias)"
        },
        {
            "ID": 5,
            "Fecha captura": "2026-07-07 00:00:00",
            "Concepto": "Memoria calculo estructural (estructura metalica)",
            "Departamento": "Diseño",
            "Responsable": None,
            "Estatus": "Cerrado",
            "Siguiente paso": "Se espera entrega el proximo miercoles 15"
        }
    ]
    df = pd.DataFrame(records)
    df["Fecha captura"] = pd.to_datetime(df["Fecha captura"])
    # Limpieza inicial de nulos en responsable para evitar fallos de visualización
    df["Responsable"] = df["Responsable"].fillna("No Asignado ⚠️")
    return df

# 3. FILE UPLOADER OPCIONAL EN SIDEBAR
st.sidebar.header("📂 Carga de Datos Externos")
uploaded_file = st.sidebar.file_uploader(
    "Cargue un archivo de control nuevo (Formatos aceptados: .xlsx, .csv)",
    type=["xlsx", "csv"]
)

# Determinación de fuente de datos activa
if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith(".csv"):
            df_active = pd.read_csv(uploaded_file)
        else:
            df_active = pd.read_excel(uploaded_file)
        
        # Validaciones de consistencia mínima
        if "Fecha captura" in df_active.columns:
            df_active["Fecha captura"] = pd.to_datetime(df_active["Fecha captura"], errors="coerce")
        if "Responsable" in df_active.columns:
            df_active["Responsable"] = df_active["Responsable"].fillna("No Asignado ⚠️")
        
        st.sidebar.success("¡Archivo cargado con éxito!")
    except Exception as e:
        st.sidebar.error(f"Error procesando archivo: {e}. Usando datos predeterminados.")
        df_active = get_default_data()
else:
    df_active = get_default_data()

# 4. BARRA LATERAL (FILTROS DINÁMICOS REACTIVOS)
st.sidebar.markdown("---")
st.sidebar.header("🎯 Filtros del Tablero")

# Validación y creación de filtros dinámicos basados en la disponibilidad de columnas
filtered_df = df_active.copy()

# Filtro por Departamento
if "Departamento" in df_active.columns:
    dept_options = df_active["Departamento"].dropna().unique().tolist()
    selected_depts = st.sidebar.multiselect("Filtrar por Departamento:", dept_options, default=dept_options)
    filtered_df = filtered_df[filtered_df["Departamento"].isin(selected_depts)]

# Filtro por Estatus
if "Estatus" in df_active.columns:
    estatus_options = df_active["Estatus"].dropna().unique().tolist()
    selected_estatus = st.sidebar.multiselect("Filtrar por Estatus de Tarea:", estatus_options, default=estatus_options)
    filtered_df = filtered_df[filtered_df["Estatus"].isin(selected_estatus)]

# Filtro por Responsable
if "Responsable" in df_active.columns:
    resp_options = df_active["Responsable"].unique().tolist()
    selected_resp = st.sidebar.multiselect("Filtrar por Responsable Asignado:", resp_options, default=resp_options)
    filtered_df = filtered_df[filtered_df["Responsable"].isin(selected_resp)]

# Filtro de escala temporal de manera informativa y adaptada
if "Fecha captura" in df_active.columns:
    min_date = df_active["Fecha captura"].min()
    max_date = df_active["Fecha captura"].max()
    if pd.notnull(min_date) and pd.notnull(max_date):
        st.sidebar.date_input(
            "Rango de Fechas (Solo Lectura / Contexto Histórico)",
            value=(min_date.date(), max_date.date()),
            min_value=min_date.date(),
            max_value=max_date.date(),
            disabled=True
        )

# 5. SECCIÓN SUPERIOR: ENCABEZADO Y METADATOS
st.title("🏗️ " + DEFAULT_METADATA["document_title"])
st.markdown(f"**Sujeto de Análisis:** {DEFAULT_METADATA['entity_or_subject']}")

with st.expander("ℹ️ Resumen Ejecutivo y Metadatos de Captura", expanded=True):
    col_meta1, col_meta2 = st.columns([1, 3])
    with col_meta1:
        st.metric("Fecha de Captura Global", DEFAULT_METADATA["date"])
    with col_meta2:
        st.markdown(f"**Propósito del Reporte:** {DEFAULT_METADATA['general_summary']}")

# 6. KPI METRICS DINÁMICAS (Calculadas sobre el DataFrame Filtrado)
st.markdown("---")
st.subheader("📈 Indicadores Operativos en Tiempo Real")

# Cálculos dinámicos basados en la estructura disponible
total_tasks = len(filtered_df)
critical_tasks = len(filtered_df[filtered_df["Estatus"] == "Critico"]) if "Estatus" in filtered_df.columns else 0
process_tasks = len(filtered_df[filtered_df["Estatus"] == "En proceso"]) if "Estatus" in filtered_df.columns else 0
closed_tasks = len(filtered_df[filtered_df["Estatus"] == "Cerrado"]) if "Estatus" in filtered_df.columns else 0

kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)

with kpi_col1:
    st.metric(label="Total de Tareas Registradas", value=total_tasks, help="Suma de todas las tareas activas y cerradas")
with kpi_col2:
    st.metric(
        label="🔴 Tareas en Estatus Crítico", 
        value=critical_tasks, 
        delta="Acción Prioritaria" if critical_tasks > 0 else None,
        delta_color="inverse"
    )
with kpi_col3:
    st.metric(label="🟡 Tareas en Proceso", value=process_tasks)
with kpi_col4:
    st.metric(label="🟢 Tareas Cerradas", value=closed_tasks)

st.markdown("---")

# 7. ORGANIZACIÓN EN PESTAÑAS (TABS)
tab_dashboard, tab_datos, tab_relaciones = st.tabs([
    "📊 Tablero de Control Visual", 
    "📋 Auditoría de Registros", 
    "🧠 Dependencias Técnicas y Alertas"
])

# 📌 PESTAÑA 1: TABLERO VISUAL (Gráficos Plotly)
with tab_dashboard:
    if filtered_df.empty:
        st.warning("⚠️ No existen registros para la combinación de filtros seleccionada en la barra lateral.")
    else:
        g_col1, g_col2 = st.columns(2)
        
        with g_col1:
            if "Estatus" in filtered_df.columns:
                fig_pie = px.pie(
                    filtered_df,
                    names="Estatus",
                    hole=0.4,
                    color="Estatus",
                    color_discrete_map={
                        "Critico": "#EF553B",    # Rojo
                        "En proceso": "#636EFA", # Azul
                        "Cerrado": "#00CC96"     # Verde
                    },
                    title="<b>Distribución de Tareas por Estatus de Urgencia</b>"
                )
                fig_pie.update_layout(margin=dict(l=20, r=20, t=50, b=20))
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("La columna 'Estatus' no se encuentra disponible para graficar.")
                
        with g_col2:
            if "Responsable" in filtered_df.columns and "Estatus" in filtered_df.columns:
                # Contabilizar ocurrencias para la barra
                df_counts = filtered_df.groupby(["Responsable", "Estatus"]).size().reset_index(name="Tareas")
                
                fig_bar = px.bar(
                    df_counts,
                    x="Responsable",
                    y="Tareas",
                    color="Estatus",
                    color_discrete_map={
                        "Critico": "#EF553B",
                        "En proceso": "#636EFA",
                        "Cerrado": "#00CC96"
                    },
                    title="<b>Distribución de Carga y Estatus por Responsable Asignado</b>",
                    labels={"Tareas": "Cantidad de Tareas", "Responsable": "Responsable Técnico"}
                )
                fig_bar.update_layout(yaxis_title="Cantidad de Actividades", margin=dict(l=20, r=20, t=50, b=20))
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.info("Las columnas necesarias ('Responsable', 'Estatus') no se encuentran disponibles.")

# 📌 PESTAÑA 2: AUDITORÍA DE REGISTROS (Datatable Interactiva y Descargas)
with tab_datos:
    st.subheader("Buscador y Visualizador del Repositorio de Datos")
    st.markdown("La siguiente tabla representa el conjunto consolidado con los filtros dinámicos activos.")
    
    # Configuración de columnas para un despliegue optimizado de UX
    column_configuration = {
        "ID": st.column_config.NumberColumn("ID Interno", format="%d"),
        "Fecha captura": st.column_config.DateColumn("Fecha Captura", format="YYYY-MM-DD"),
        "Concepto": st.column_config.TextColumn("Hito / Tarea de Adquisición"),
        "Departamento": st.column_config.TextColumn("Área Encargada"),
        "Responsable": st.column_config.TextColumn("Responsable Técnico"),
        "Estatus": st.column_config.TextColumn("Estatus Actual"),
        "Siguiente paso": st.column_config.TextColumn("Siguiente Acción Inmediata")
    }
    
    # Filtrar solo columnas presentes en la tabla activa para evitar excepciones de configuración
    active_cols_config = {k: v for k, v in column_configuration.items() if k in filtered_df.columns}
    
    st.dataframe(
        filtered_df,
        use_container_width=True,
        column_config=active_cols_config,
        hide_index=True
    )
    
    # Descarga interactiva de datos filtrados
    csv_buffer = io.StringIO()
    filtered_df.to_csv(csv_buffer, index=False)
    csv_data = csv_buffer.getvalue()
    
    st.download_button(
        label="📥 Exportar Reporte Filtrado como CSV",
        data=csv_data,
        file_name="Control_Adquisiciones_Filtrado.csv",
        mime="text/csv"
    )

# 📌 PESTAÑA 3: DEPENDENCIAS TÉCNICAS Y ALERTAS (Semántica e inteligencia de negocio)
with tab_relaciones:
    st.subheader("🧠 Matriz de Relaciones Semánticas y Cuellos de Botella Técnicos")
    
    # Caja informativa estructurada con Markdown
    st.info(
        "💡 **Agregación Lógica del Sistema:** El total consolidado de indicadores mostrados corresponde "
        "a la suma lineal de las dependencias logísticas y operativas del proyecto. El progreso de ingeniería de diseño "
        "condiciona de manera directa la colocación y validación de órdenes de compra (OC) de suministros."
    )
    
    col_rel_left, col_rel_right = st.columns(2)
    
    with col_rel_left:
        st.error(
            "### 🔴 Alerta de Ruta Crítica (Estructuras - TECOIMSA)\n\n"
            "La tarea **OC Estructura** (ID 2), bajo la responsabilidad directa de **Judith Echeverria**, "
            "representa el hito con mayor riesgo para el cronograma del proyecto.\n\n"
            "**Detalle Operativo:** Se requiere la liberación del anticipo en los próximos 15 días y la "
            "consolidación de la reunión técnica con el proveedor **TECOIMSA** de manera urgente."
        )
        
    with col_rel_right:
        st.warning(
            "### 🔄 Cuello de Botella Técnico (NIDEC ➡️ TECOIMSA)\n\n"
            "Existe una dependencia cruzada de alta prioridad entre la tarea de **Entrega diseño de estructura** (ID 3) "
            "y la **OC estructura** (ID 2).\n\n"
            "**Justificación:** No es viable iniciar el proceso formal de fabricación de acero estructural con "
            "TECOIMSA sin obtener previamente la aprobación técnica de ingeniería y el visto bueno final por parte de **NIDEC**."
        )