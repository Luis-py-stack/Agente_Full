import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------------------------------------------------
# 1. PAGE CONFIGURATION (MUST BE FIRST STREAMLIT CALL)
# ---------------------------------------------------------
st.set_page_config(
    page_title="Seguimiento de Órdenes de Compra y Entregables de Diseño",
    page_icon="🏗️",
    layout="wide"
)

# ---------------------------------------------------------
# 2. IN-MEMORY DATASET DEFINITION
# ---------------------------------------------------------
RAW_RECORDS = [
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

# ---------------------------------------------------------
# 3. SIDEBAR: FILE UPLOADER & FILTERS
# ---------------------------------------------------------
st.sidebar.title("⚙️ Configuración y Filtros")

uploaded_file = st.sidebar.file_uploader(
    "Cargar datos externos (XLSX o CSV)",
    type=["xlsx", "csv"],
    help="Si no subes ningún archivo, se utilizarán los datos predeterminados en memoria."
)

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith(".csv"):
            df_base = pd.read_csv(uploaded_file)
        else:
            df_base = pd.read_excel(uploaded_file)
        st.sidebar.success("✅ Archivo cargado correctamente.")
    except Exception as e:
        st.sidebar.warning(f"Error al procesar el archivo. Se utilizarán los datos internos. ({e})")
        df_base = pd.DataFrame(RAW_RECORDS)
else:
    df_base = pd.DataFrame(RAW_RECORDS)

# Defensive Data Cleaning
df = df_base.copy()

if "ID" in df.columns:
    df["ID"] = pd.to_numeric(df["ID"], errors="coerce").fillna(0).astype(int)

if "Fecha captura" in df.columns:
    df["Fecha captura"] = pd.to_datetime(df["Fecha captura"], errors="coerce").dt.strftime('%Y-%m-%d')

if "Responsable" in df.columns:
    df["Responsable"] = df["Responsable"].fillna("Sin Asignar")
else:
    df["Responsable"] = "Sin Asignar"

if "Departamento" not in df.columns:
    df["Departamento"] = "Sin Departamento"

if "Estatus" not in df.columns:
    df["Estatus"] = "Desconocido"

if "Concepto" not in df.columns:
    df["Concepto"] = ""

if "Siguiente paso" not in df.columns:
    df["Siguiente paso"] = ""

# Reactive Sidebar Filters
st.sidebar.subheader("🎯 Filtros Reactivos")

deptos_opt = sorted(list(df["Departamento"].unique()))
selected_deptos = st.sidebar.multiselect("Departamento:", options=deptos_opt, default=deptos_opt)

estatus_opt = sorted(list(df["Estatus"].unique()))
selected_estatus = st.sidebar.multiselect("Estatus:", options=estatus_opt, default=estatus_opt)

resp_opt = sorted(list(df["Responsable"].unique()))
selected_resp = st.sidebar.multiselect("Responsable:", options=resp_opt, default=resp_opt)

search_text = st.sidebar.text_input("🔍 Buscar en Concepto / Siguiente paso:", "")

# Filter Application
df_filtered = df[
    (df["Departamento"].isin(selected_deptos)) &
    (df["Estatus"].isin(selected_estatus)) &
    (df["Responsable"].isin(selected_resp))
]

if search_text:
    search_lower = search_text.lower()
    df_filtered = df_filtered[
        df_filtered["Concepto"].astype(str).str.lower().str.contains(search_lower, na=False) |
        df_filtered["Siguiente paso"].astype(str).str.lower().str.contains(search_lower, na=False)
    ]

# Guard clause for empty data
if df_filtered.empty:
    st.warning("⚠️ No se encontraron registros con los filtros seleccionados. Modifica las opciones en la barra lateral.")
    st.stop()

# ---------------------------------------------------------
# 4. HEADER & KPIS
# ---------------------------------------------------------
st.title("Seguimiento de Órdenes de Compra y Entregables de Diseño")
st.caption("Proyecto de Infraestructura y Estructura Metálica (NIDEC / TECOIMSA)")

st.info(
    "**Fecha de Captura General:** 2026-07-07  \n"
    "**Resumen Ejecutivo:** Bitácora de control para el seguimiento de órdenes de compra, "
    "revisiones de diseño estructural, asignación de responsables y estatus de ejecución de tareas claves del proyecto."
)

st.markdown("---")

# KPI Rows
kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
kpi_col4, kpi_col5, kpi_col6 = st.columns(3)

total_tasks = len(df_filtered)
closed_tasks = len(df_filtered[df_filtered["Estatus"] == "Cerrado"])
process_tasks = len(df_filtered[df_filtered["Estatus"] == "En proceso"])
critical_tasks = len(df_filtered[df_filtered["Estatus"].astype(str).str.lower().isin(["critico", "crítico"])])
compras_tasks = len(df_filtered[df_filtered["Departamento"] == "Compras"])
diseno_tasks = len(df_filtered[df_filtered["Departamento"] == "Diseño"])

closed_pct = round((closed_tasks / total_tasks * 100)) if total_tasks > 0 else 0

with kpi_col1:
    st.metric(
        label="Total Tareas Registradas",
        value=total_tasks,
        help="Total de filas registradas tras aplicar filtros"
    )

with kpi_col2:
    st.metric(
        label="Estatus Cerrado",
        value=closed_tasks,
        delta=f"{closed_pct}% Finalizado"
    )

with kpi_col3:
    st.metric(
        label="En Proceso",
        value=process_tasks,
        delta_color="off"
    )

with kpi_col4:
    st.metric(
        label="Estatus Crítico",
        value=critical_tasks,
        delta="-1 Atención Prioritaria" if critical_tasks > 0 else "0 Críticos",
        delta_color="inverse"
    )

with kpi_col5:
    st.metric(
        label="Dpto. Compras",
        value=f"{compras_tasks} tareas"
    )

with kpi_col6:
    st.metric(
        label="Dpto. Diseño",
        value=f"{diseno_tasks} tareas"
    )

st.markdown("---")

# ---------------------------------------------------------
# 5. TABS NAVIGATION
# ---------------------------------------------------------
tab1, tab2, tab3 = st.tabs([
    "📊 Panel General y Analítica",
    "📋 Bitácora: Seguimiento de Conceptos",
    "🔗 Trazabilidad y Relaciones Semánticas"
])

status_colors = {
    "Cerrado": "#2ecc71",
    "En proceso": "#f39c12",
    "Critico": "#e74c3c",
    "Crítico": "#e74c3c"
}

# ---------------------------------------------------------
# TAB 1: PANEL GENERAL Y ANALÍTICA
# ---------------------------------------------------------
with tab1:
    st.subheader("Análisis Gráfico de Estatus y Carga de Trabajo")
    
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        df_status = df_filtered["Estatus"].value_counts().reset_index()
        df_status.columns = ["Estatus", "Cantidad"]
        
        fig1 = px.pie(
            df_status,
            names="Estatus",
            values="Cantidad",
            hole=0.4,
            title="Distribución de Tareas por Estatus",
            color="Estatus",
            color_discrete_map=status_colors
        )
        fig1.update_traces(textinfo="value+percent")
        fig1.update_layout(
            legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5)
        )
        st.plotly_chart(fig1, use_container_width=True)

    with col_chart2:
        df_dept_status = df_filtered.groupby(["Departamento", "Estatus"]).size().reset_index(name="Cantidad")
        
        fig2 = px.bar(
            df_dept_status,
            x="Departamento",
            y="Cantidad",
            color="Estatus",
            title="Distribución de Tareas por Departamento y Estado",
            barmode="stack",
            color_discrete_map=status_colors,
            labels={"Cantidad": "Cantidad de Tareas"}
        )
        fig2.update_layout(
            legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5)
        )
        st.plotly_chart(fig2, use_container_width=True)

    df_resp = df_filtered.groupby(["Responsable", "Departamento"]).size().reset_index(name="Cantidad")
    
    fig3 = px.bar(
        df_resp,
        y="Responsable",
        x="Cantidad",
        color="Departamento",
        orientation="h",
        title="Tareas Asignadas por Responsable y Departamento",
        labels={"Cantidad": "Tareas Asignadas"}
    )
    fig3.update_layout(
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5)
    )
    st.plotly_chart(fig3, use_container_width=True)

# ---------------------------------------------------------
# TAB 2: BITÁCORA - TABLA DE DATOS CRUDOS
# ---------------------------------------------------------
with tab2:
    st.subheader("Bitácora Completa de Seguimiento")
    st.caption("Filtra, explora y exporta el detalle operativo de conceptos y órdenes de compra.")
    
    st.dataframe(
        df_filtered,
        use_container_width=True,
        column_config={
            "ID": st.column_config.NumberColumn("ID", format="%d"),
            "Fecha captura": st.column_config.TextColumn("Fecha Captura"),
            "Concepto": st.column_config.TextColumn("Concepto / Entregable", width="medium"),
            "Departamento": st.column_config.TextColumn("Departamento", width="small"),
            "Responsable": st.column_config.TextColumn("Responsable Asignado", width="medium"),
            "Estatus": st.column_config.TextColumn("Estatus", width="small"),
            "Siguiente paso": st.column_config.TextColumn("Siguiente Paso / Observaciones", width="large")
        },
        hide_index=True
    )
    
    csv_data = df_filtered.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Exportar Bitácora Filtrada (CSV)",
        data=csv_data,
        file_name="seguimiento_ordenes_compra.csv",
        mime="text/csv"
    )

# ---------------------------------------------------------
# TAB 3: TRAZABILIDAD Y RELACIONES SEMÁNTICAS
# ---------------------------------------------------------
with tab3:
    st.subheader("Matriz de Trazabilidad y Dependencias Críticas")
    
    # Module 1: Critical Alert Card
    with st.container(border=True):
        st.markdown("### 🚨 Módulo de Alerta Crítica: OC Estructura Metálica (ID 2)")
        st.markdown(
            "- **Área / Responsable:** Compras | Judith Echeverria  \n"
            "- **Proveedor / Entidad:** TECOIMSA  \n"
            "- **Diagnóstico de Riesgo:** Estatus **Crítico**. Se requiere compartir la Orden de Compra el día de hoy. "
            "El anticipo está programado para pago en 15 días, sujeto a confirmación de reunión de alineación con TECOIMSA."
        )
    
    # Module 2: Design Dependencies
    st.markdown("### 📐 Matriz de Dependencias en Diseño (IDs 3 y 5)")
    col_dis1, col_dis2 = st.columns(2)
    
    with col_dis1:
        with st.container(border=True):
            st.markdown("#### ⏳ ID 3: Entrega Diseño de Estructura")
            st.markdown(
                "- **Responsable:** Carlos Mendez  \n"
                "- **Estatus:** En proceso  \n"
                "- **Dependencia Clave:** Requiere revisión y VoBo técnico formal por parte del cliente **NIDEC**."
            )
        
    with col_dis2:
        with st.container(border=True):
            st.markdown("#### ✅ ID 5: Memoria de Cálculo Estructural")
            st.markdown(
                "- **Responsable:** Sin Asignar (Soporte Técnico)  \n"
                "- **Estatus:** Cerrado  \n"
                "- **Siguiente Hito:** Sirve como respaldo técnico del cálculo estructural para la aprobación del diseño (ID 3). Entrega de documento final el próximo miércoles 15."
            )
        
    # Module 3: Procurement Consolidation
    with st.container(border=True):
        st.markdown("### 📦 Consolidación de Responsabilidades en Compras")
        st.markdown(
            "**Judith Echeverria** concentra la gestión técnica de insumos críticos de infraestructura:  \n"
            "1. **ID 2 - OC Estructura:** Estado Crítico (Gestión urgente con TECOIMSA).  \n"
            "2. **ID 4 - OC Anclas y Placas:** Estado En Proceso (Cotización de materiales para entrega a Luis Ramirez, tiempo de fabricación: 4 días)."
        )