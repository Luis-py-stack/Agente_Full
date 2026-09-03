import streamlit as st
import pandas as pd
import plotly.express as px
import json

# 1. Configuración de página - PRIMERA llamada de Streamlit
st.set_page_config(
    page_title="Seguimiento NIDEC - Panel de Control",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Autonomía de datos: Construcción del dataset JSON en memoria
DATA_JSON = {
  "metadata": {
    "document_title": "Seguimiento de Órdenes de Compra y Diseño Estructural",
    "entity_or_subject": "NIDEC (Proyecto de Infraestructura / TECOIMSA / Rangel)",
    "dates": [
      {
        "context": "Fecha de captura de estatus",
        "value": "2026-07-07"
      },
      {
        "context": "Fecha estimada de entrega de memoria de cálculo",
        "value": "2026-07-15"
      }
    ],
    "general_summary": "Monitoreo de tareas críticas, órdenes de compra (OC) y entregables de diseño técnico para el proyecto de cimentación y estructura metalica de la planta NIDEC."
  },
  "global_kpis_and_totals": [
    {
      "metric": "Total de Tareas Registradas",
      "value": "5",
      "unit": "unidades",
      "context": "Volumen de actividades en el tablero de control"
    },
    {
      "metric": "Tareas Cerradas",
      "value": "2",
      "unit": "unidades",
      "context": "Tareas con estatus Cerrado (Cimentaciones y Memoria de cálculo)"
    },
    {
      "metric": "Tareas en Proceso",
      "value": "2",
      "unit": "unidades",
      "context": "Tareas activas de diseño y cotización de herrajes"
    },
    {
      "metric": "Tareas Críticas",
      "value": "1",
      "unit": "unidades",
      "context": "Órdenes de compra pendientes urgentes (Estructura con TECOIMSA)"
    },
    {
      "metric": "Tiempo de Fabricación de Anclas y Placas",
      "value": "4",
      "unit": "días",
      "context": "Tiempo estimado para la entrega de materiales a Luis Ramírez"
    }
  ],
  "tables": [
    {
      "table_id": "control_actividades_hoja1",
      "description": "Lista detallada del estatus de adquisiciones y aprobaciones técnicas del proyecto de obra civil.",
      "columns": [
        "ID",
        "Fecha captura",
        "Concepto",
        "Departamento",
        "Responsable",
        "Estatus",
        "Siguiente paso"
      ],
      "records": [
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
    }
  ],
  "semantic_relationships": [
    {
      "source": "global_kpis_and_totals.Tareas Críticas",
      "relation_type": "desglose",
      "target": "tables[0].records[ID=2]",
      "explanation": "La única tarea en estatus crítico corresponde a la OC Estructura asignada a Judith Echeverria relacionada con TECOIMSA."
    },
    {
      "source": "tables[0].records[ID=3]",
      "relation_type": "dependencia",
      "target": "metadata.entity_or_subject",
      "explanation": "El diseño de la estructura (Carlos Mendez) se encuentra actualmente en revisión y visto bueno directo por el cliente final NIDEC."
    },
    {
      "source": "tables[0].records[ID=4]",
      "relation_type": "especificacion",
      "target": "global_kpis_and_totals.Tiempo de Fabricación de Anclas y Placas",
      "explanation": "El proceso de cotización y suministro de anclas y placas cuenta con un tiempo estimado de manufactura interna de 4 días antes de su entrega."
    }
  ]
}

# Carga por defecto de los datos del JSON
default_records = DATA_JSON["tables"][0]["records"]
df_default = pd.DataFrame(default_records)
df_default["Fecha captura"] = pd.to_datetime(df_default["Fecha captura"])
df_default["Responsable"] = df_default["Responsable"].fillna("Sin asignar")

# 3. File Uploader opcional en Sidebar
st.sidebar.markdown("## ⚙️ Panel de Configuración")
uploaded_file = st.sidebar.file_uploader(
    "Cargar un archivo nuevo (Opcional)", 
    type=["csv", "xlsx"],
    help="Suba un archivo con columnas idénticas para actualizar el reporte dinámicamente."
)

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        st.sidebar.success("¡Archivo cargado con éxito!")
    except Exception as e:
        st.sidebar.error(f"Error al leer el archivo cargado. Usando base predeterminada. Detalles: {e}")
        df = df_default.copy()
else:
    df = df_default.copy()

# Tratamiento de nulos para consistencia de filtros
if "Responsable" in df.columns:
    df["Responsable"] = df["Responsable"].fillna("Sin asignar")

# Filtros Interactivos Multivariables
st.sidebar.markdown("---")
st.sidebar.markdown("### 🔍 Filtros de Visualización")

# Filtro Departamento
selected_depts = []
if "Departamento" in df.columns:
    depts = sorted(df["Departamento"].dropna().unique().tolist())
    selected_depts = st.sidebar.multiselect("Filtrar por Departamento", options=depts, default=depts)

# Filtro Estatus
selected_status = []
if "Estatus" in df.columns:
    status_opts = sorted(df["Estatus"].dropna().unique().tolist())
    selected_status = st.sidebar.multiselect("Filtrar por Estatus", options=status_opts, default=status_opts)

# Filtro Responsable
selected_resp = []
if "Responsable" in df.columns:
    resp_opts = sorted(df["Responsable"].unique().tolist())
    selected_resp = st.sidebar.multiselect("Filtrar por Responsable", options=resp_opts, default=resp_opts)

# Buscador de texto libre
search_query = st.sidebar.text_input("Buscar por concepto o palabra clave:")

# Aplicar Filtros
filtered_df = df.copy()
if "Departamento" in filtered_df.columns and selected_depts:
    filtered_df = filtered_df[filtered_df["Departamento"].isin(selected_depts)]
if "Estatus" in filtered_df.columns and selected_status:
    filtered_df = filtered_df[filtered_df["Estatus"].isin(selected_status)]
if "Responsable" in filtered_df.columns and selected_resp:
    filtered_df = filtered_df[filtered_df["Responsable"].isin(selected_resp)]
if search_query:
    search_cols = [c for c in ["Concepto", "Siguiente paso", "Departamento", "Responsable"] if c in filtered_df.columns]
    if search_cols:
        mask = filtered_df[search_cols].apply(lambda row: row.astype(str).str.contains(search_query, case=False).any(), axis=1)
        filtered_df = filtered_df[mask]

# 4. Visualización Completa: Cabecera y Metadatos
st.title("🏗️ Seguimiento de Órdenes de Compra y Diseño Estructural")
st.markdown(f"#### **Sujeto/Entidad:** {DATA_JSON['metadata']['entity_or_subject']}")

# Tarjeta de Información de Metadatos
col_meta1, col_meta2 = st.columns([1, 2])
with col_meta1:
    st.info(
        f"📅 **Captura de Estatus:** `{DATA_JSON['metadata']['dates'][0]['value']}`\n\n"
        f"🎯 **Hito Clave (Memoria de Cálculo):** **`{DATA_JSON['metadata']['dates'][1]['value']}`**"
    )
with col_meta2:
    st.markdown(
        f"**Resumen General del Proyecto:**\n"
        f"*{DATA_JSON['metadata']['general_summary']}*"
    )

st.markdown("---")

# Renderizar KPI's Globales (st.metric) en un grid de 5 columnas
st.subheader("📈 Indicadores Clave de Rendimiento (KPIs)")
kpi_cols = st.columns(5)
kpis_data = DATA_JSON["global_kpis_and_totals"]

with kpi_cols[0]:
    st.metric(
        label="📋 " + kpis_data[0]["metric"], 
        value=kpis_data[0]["value"], 
        help=kpis_data[0]["context"]
    )
with kpi_cols[1]:
    st.metric(
        label="✅ " + kpis_data[1]["metric"], 
        value=kpis_data[1]["value"], 
        help=kpis_data[1]["context"]
    )
with kpi_cols[2]:
    st.metric(
        label="🔄 " + kpis_data[2]["metric"], 
        value=kpis_data[2]["value"], 
        help=kpis_data[2]["context"]
    )
with kpi_cols[3]:
    st.metric(
        label="⚠️ " + kpis_data[3]["metric"], 
        value=kpis_data[3]["value"], 
        help=kpis_data[3]["context"]
    )
with kpi_cols[4]:
    st.metric(
        label="⏱️ " + kpis_data[4]["metric"], 
        value=f"{kpis_data[4]['value']} {kpis_data[4]['unit']}", 
        help=kpis_data[4]["context"]
    )

st.markdown("---")

# 5. Pestañas de Navegación Operativa
tab1, tab2, tab3 = st.tabs([
    "📊 Control de Actividades y KPI's", 
    "🔗 Trazabilidad y Relaciones Semánticas", 
    "📋 Datos Crudos y Exportación"
])

# MAPA DE COLORES CONSISTENTE PARA GRÁFICOS
color_map = {
    "Cerrado": "#2ca02c", 
    "En proceso": "#ff7f0e", 
    "Critico": "#d62728"
}

# PESTAÑA 1: CONTROL DE ACTIVIDADES Y GRAFICOS
with tab1:
    st.subheader("Análisis Visual del Tablero de Trabajo")
    
    if filtered_df.empty:
        st.warning("No hay registros que coincidan con los filtros aplicados en el sidebar.")
    else:
        # Fila de gráficos principales
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            if "Estatus" in filtered_df.columns:
                fig_pie = px.pie(
                    filtered_df, 
                    names="Estatus", 
                    color="Estatus",
                    color_discrete_map=color_map,
                    hole=0.4,
                    title="Distribución Total de Actividades por Estatus"
                )
                fig_pie.update_layout(legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5))
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("Columna 'Estatus' no disponible para graficar.")

        with chart_col2:
            if "Departamento" in filtered_df.columns and "Estatus" in filtered_df.columns:
                df_grouped = filtered_df.groupby(["Departamento", "Estatus"]).size().reset_index(name="Cantidad")
                fig_bar = px.bar(
                    df_grouped,
                    x="Departamento",
                    y="Cantidad",
                    color="Estatus",
                    color_discrete_map=color_map,
                    title="Carga de Trabajo por Departamento",
                    barmode="stack"
                )
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.info("Columnas 'Departamento' o 'Estatus' no disponibles para el gráfico de barras.")

        st.markdown("---")
        
        # Gráfico de matriz de responsabilidad
        if "Responsable" in filtered_df.columns and "Estatus" in filtered_df.columns:
            df_resp = filtered_df.groupby(["Responsable", "Estatus"]).size().reset_index(name="Cantidad")
            fig_resp = px.bar(
                df_resp,
                x="Responsable",
                y="Cantidad",
                color="Estatus",
                color_discrete_map=color_map,
                barmode="group",
                title="Matriz de Responsabilidad Técnica y Estatus"
            )
            st.plotly_chart(fig_resp, use_container_width=True)


# PESTAÑA 2: TRAZABILIDAD Y RELACIONES SEMÁNTICAS
with tab2:
    st.subheader("🕸️ Red de Trazabilidad y Relaciones del Negocio")
    st.markdown(
        "Las siguientes tarjetas exponen las conexiones lógicas, dependencias y justificaciones "
        "comerciales de los hitos documentados:"
    )

    # Relación Semántica 1
    st.error(
        f"### 🔴 Alerta de Criticidad Operativa\n"
        f"**Origen:** `{DATA_JSON['semantic_relationships'][0]['source']}`  \n"
        f"**Tipo de Relación:** `{DATA_JSON['semantic_relationships'][0]['relation_type']}`  \n"
        f"**Destino:** `{DATA_JSON['semantic_relationships'][0]['target']}`  \n\n"
        f"**Detalle del Enlace:** {DATA_JSON['semantic_relationships'][0]['explanation']}"
    )

    # Relación Semántica 2
    st.info(
        f"### 🔵 Dependencia de Aprobación Externa\n"
        f"**Origen:** `{DATA_JSON['semantic_relationships'][1]['source']}`  \n"
        f"**Tipo de Relación:** `{DATA_JSON['semantic_relationships'][1]['relation_type']}`  \n"
        f"**Destino:** `{DATA_JSON['semantic_relationships'][1]['target']}`  \n\n"
        f"**Detalle del Enlace:** {DATA_JSON['semantic_relationships'][1]['explanation']}"
    )

    # Relación Semántica 3
    st.success(
        f"### 🟢 Especificación y Planificación de Suministro\n"
        f"**Origen:** `{DATA_JSON['semantic_relationships'][2]['source']}`  \n"
        f"**Tipo de Relación:** `{DATA_JSON['semantic_relationships'][2]['relation_type']}`  \n"
        f"**Destino:** `{DATA_JSON['semantic_relationships'][2]['target']}`  \n\n"
        f"**Detalle del Enlace:** {DATA_JSON['semantic_relationships'][2]['explanation']}"
    )


# PESTAÑA 3: DATOS CRUDOS Y EXPORTACIÓN
with tab3:
    st.subheader("📋 Datos Estructurados del Proyecto")
    st.markdown("A continuación se muestra el subconjunto de datos resultante con formato interactivo:")

    # Formateo de fecha para mejor visualización
    df_export = filtered_df.copy()
    if "Fecha captura" in df_export.columns:
        df_export["Fecha captura"] = pd.to_datetime(df_export["Fecha captura"]).dt.date

    # Estilizado Condicional
    def color_estatus(val):
        if val == "Critico":
            return 'background-color: #ffcccc; color: #cc0000; font-weight: bold;'
        elif val == "En proceso":
            return 'background-color: #ffe5cc; color: #b35900;'
        elif val == "Cerrado":
            return 'background-color: #e2f0d9; color: #385723;'
        return ''

    # Aplicación segura de estilos según versión de pandas
    if "Estatus" in df_export.columns:
        try:
            styled_df = df_export.style.map(color_estatus, subset=['Estatus'])
        except AttributeError:
            # Soporte para versiones anteriores de pandas
            styled_df = df_export.style.applymap(color_estatus, subset=['Estatus'])
    else:
        styled_df = df_export

    # Mostrar dataframe con ancho completo
    st.dataframe(styled_df, use_container_width=True, hide_index=True)

    st.markdown("---")

    # Contenedores de Exportación y Auditoría
    col_dl1, col_dl2 = st.columns(2)
    with col_dl1:
        # Descarga de datos interactiva
        csv_data = df_export.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Descargar Reporte Filtrado (CSV)",
            data=csv_data,
            file_name="Reporte_Control_NIDEC.csv",
            mime="text/csv"
        )
    with col_dl2:
        with st.expander("🛠️ Ver Estructura Original del JSON (Auditoría Técnica)"):
            st.json(DATA_JSON)