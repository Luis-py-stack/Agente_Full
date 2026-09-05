import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib

# RULE 1: Page Configuration must be the FIRST Streamlit call
st.set_page_config(page_title="Seguimiento de Proyecto NIDEC", layout='wide')

# RULE 2: Autonomous Data - Built-in DataFrame representing the JSON data
raw_data = [
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
    }
]
df_default = pd.DataFrame(raw_data)

# Header & Context Layout
st.title("🏗️ Seguimiento de Tareas y Órdenes de Compra")
st.subheader("Proyecto de Infraestructura (NIDEC) — Hoja 1")

# Metadata Expandable Panel
with st.expander("ℹ️ Información del Documento y Metadatos", expanded=True):
    col_meta1, col_meta2 = st.columns([1, 3])
    with col_meta1:
        st.markdown("**Fecha de Captura:** `2026-07-07`" )
    with col_meta2:
        st.markdown("**Resumen General:** Monitoreo del estatus de órdenes de compra y entregables de diseño técnico para la cimentación y estructura metálica del proyecto, identificando responsables, cuellos de botella y fechas de entrega de hitos.")

st.markdown("---")

# RULE 3: Optional File Uploader in the sidebar
st.sidebar.header("📂 Carga de Datos Adicionales")
uploaded_file = st.sidebar.file_uploader("Subir archivo Excel o CSV", type=['xlsx', 'csv'])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df_active = pd.read_csv(uploaded_file)
        else:
            df_active = pd.read_excel(uploaded_file)
        st.sidebar.success("¡Datos externos cargados correctamente!")
    except Exception as e:
        st.sidebar.error(f"Error al procesar archivo: {e}")
        df_active = df_default.copy()
else:
    df_active = df_default.copy()

# RULE 6: Defensive typing and column verification
if 'responsable' in df_active.columns:
    df_active['responsable'] = df_active['responsable'].fillna("Sin Asignar")
else:
    df_active['responsable'] = "Sin Asignar"

if 'estatus' in df_active.columns:
    df_active['estatus'] = df_active['estatus'].fillna("Sin Estatus")
else:
    df_active['estatus'] = "Sin Estatus"

if 'departamento' in df_active.columns:
    df_active['departamento'] = df_active['departamento'].fillna("Sin Departamento")
else:
    df_active['departamento'] = "Sin Departamento"

if 'id' in df_active.columns:
    df_active['id'] = pd.to_numeric(df_active['id'], errors='coerce')

# Interactive Filters in Sidebar
st.sidebar.header("🎯 Filtros de Control")

# Departamento Filter
if 'departamento' in df_active.columns:
    depts_available = sorted(df_active['departamento'].unique())
    selected_depts = st.sidebar.multiselect("Filtrar por Departamento:", options=depts_available, default=depts_available)
else:
    selected_depts = []

# Estatus Filter
if 'estatus' in df_active.columns:
    estatus_available = sorted(df_active['estatus'].unique())
    selected_estatus = st.sidebar.multiselect("Filtrar por Estatus:", options=estatus_available, default=estatus_available)
else:
    selected_estatus = []

# Responsable Filter
if 'responsable' in df_active.columns:
    resp_available = sorted(df_active['responsable'].unique())
    selected_resp = st.sidebar.multiselect("Filtrar por Responsable:", options=resp_available, default=resp_available)
else:
    selected_resp = []

# Reset filters button
if st.sidebar.button("🔄 Resetear Filtros"):
    st.rerun()

# Apply Filters Reactively
df_filtrado = df_active[
    (df_active['departamento'].isin(selected_depts)) &
    (df_active['estatus'].isin(selected_estatus)) &
    (df_active['responsable'].isin(selected_resp))
]

# RULE 6: Validate Empty DataFrames and Stop Operative Process if Empty
if df_filtrado.empty:
    st.warning("⚠️ No se encontraron registros que coincidan con los filtros seleccionados. Ajuste los parámetros de la barra lateral.")
    st.stop()

# Dynamic KPI calculations based on current (filtered) dataset
total_tareas = len(df_filtrado)
cerradas = len(df_filtrado[df_filtrado['estatus'] == 'Cerrado']) if 'estatus' in df_filtrado.columns else 0
en_proceso = len(df_filtrado[df_filtrado['estatus'] == 'En proceso']) if 'estatus' in df_filtrado.columns else 0
critico = len(df_filtrado[df_filtrado['estatus'] == 'Critico']) if 'estatus' in df_filtrado.columns else 0
compras_count = len(df_filtrado[df_filtrado['departamento'] == 'Compras']) if 'departamento' in df_filtrado.columns else 0
diseno_count = len(df_filtrado[df_filtrado['departamento'] == 'Diseño']) if 'departamento' in df_filtrado.columns else 0

# KPIs Grid (6 Columns)
cols_kpi = st.columns(6)
cols_kpi[0].metric(label="Total Tareas", value=str(total_tareas), help="Volumen total de actividades visibles.")
cols_kpi[1].metric(label="Tareas Cerradas", value=str(cerradas), help="Actividades completadas con estatus Cerrado.")
cols_kpi[2].metric(label="En Proceso", value=str(en_proceso), help="Actividades en desarrollo activo.")
cols_kpi[3].metric(label="Estatus Crítico", value=str(critico), delta_color="inverse", help="Atención prioritaria por alto impacto.")
cols_kpi[4].metric(label="Carga: Compras", value=str(compras_count), help="Tareas asignadas al departamento de Compras.")
cols_kpi[5].metric(label="Carga: Diseño", value=str(diseno_count), help="Tareas de ingeniería y diseño técnico.")

st.markdown("---")

# Navigation Tabs
tab_dashboard, tab_datos, tab_relaciones = st.tabs([
    "📈 Dashboard de Control", 
    "🗂️ Registro de Datos Crudos", 
    "🕸️ Dependencias y Relaciones Semánticas"
])

# Color Scheme configuration for plotting consistency
color_map = {
    "Cerrado": "#2ca02c",      # Green
    "En proceso": "#ff7f0e",    # Orange
    "Critico": "#d62728",       # Red
    "Sin Estatus": "#7f7f7f"
}

# TAB 1: VISUAL DASHBOARD
with tab_dashboard:
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.markdown("### 📊 Distribución de Tareas por Estado")
        if 'estatus' in df_filtrado.columns:
            fig_pie = px.pie(
                df_filtrado, 
                names="estatus", 
                hole=0.45,
                color="estatus",
                color_discrete_map=color_map,
                title="Proporción del Estatus de Gestión de Actividades"
            )
            fig_pie.update_traces(textinfo='percent+label')
            
            # RULE 5: Plotly Legend alignment standard dictionary
            fig_pie.update_layout(
                legend=dict(orientation='h', yanchor='bottom', y=-0.25, xanchor='center', x=0.5),
                margin=dict(b=80)
            )
            st.plotly_chart(fig_pie, width='stretch')
        else:
            st.info("Columna 'estatus' no disponible para graficar.")
            
    with col_chart2:
        st.markdown("### 🏢 Carga de Trabajo por Departamento")
        if 'departamento' in df_filtrado.columns and 'estatus' in df_filtrado.columns:
            fig_bar = px.bar(
                df_filtrado,
                x="departamento",
                color="estatus",
                title="Estatus de Entregables por Departamento",
                barmode="stack",
                color_discrete_map=color_map,
                category_orders={"departamento": ["Compras", "Diseño"]}
            )
            
            # RULE 5: Plotly Legend alignment standard dictionary
            fig_bar.update_layout(
                legend=dict(orientation='h', yanchor='bottom', y=-0.25, xanchor='center', x=0.5),
                margin=dict(b=80),
                xaxis_title="Departamento",
                yaxis_title="Cantidad de Tareas"
            )
            st.plotly_chart(fig_bar, width='stretch')
        else:
            st.info("Columnas de departamento/estatus no disponibles para graficar.")

# TAB 2: DATA TABLE VIEW
with tab_datos:
    st.markdown("### 📋 Tabla de Seguimiento de Proyecto (Hoja 1)")
    st.write("Visualice, filtre, ordene y descargue los registros individuales del plan de infraestructura:")
    
    # RULE 4: Standardize dataframe layout and sizing without dependency issues
    st.dataframe(
        df_filtrado,
        width='stretch',
        column_config={
            "id": st.column_config.NumberColumn("ID Tarea", format="%d"),
            "fecha_captura": st.column_config.DateColumn("Fecha Captura"),
            "concepto": st.column_config.TextColumn("Concepto/Entregable"),
            "departamento": st.column_config.TextColumn("Departamento"),
            "responsable": st.column_config.TextColumn("Responsable"),
            "estatus": st.column_config.TextColumn("Estatus de Gestión"),
            "siguiente_paso": st.column_config.TextColumn("Siguiente Acción Clave")
        },
        hide_index=True
    )
    
    # Dynamic CSV Download Option
    csv_data = df_filtrado.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Descargar datos actuales como CSV",
        data=csv_data,
        file_name="seguimiento_proyecto_nidec.csv",
        mime="text/csv"
    )

# TAB 3: SEMANTIC RELATIONSHIPS & STRATEGIC INSIGHTS
# Using clean custom styled HTML containers to present insights professionally and avoid AST test engine errors
with tab_relaciones:
    st.markdown("### 🕸️ Dependencias, Cuellos de Botella e Insights de Operación")
    st.write("Análisis cruzado de los datos y dependencias organizacionales latentes:")

    # Relationship 1: Concentration of Responsibility
    st.markdown("""
    <div style="padding:15px; border-radius:8px; border-left: 5px solid #d62728; background-color: rgba(214, 39, 40, 0.08); margin-bottom: 20px;">
        <h4 style="margin-top:0; color: #d62728;">👤 1. Concentración de Responsabilidad y Carga Crítica</h4>
        <strong>Origen:</strong> ID 2 y ID 4 (Judith Echeverria)<br>
        <strong>Tipo de Relación:</strong> Agregación / Carga de Trabajo<br><br>
        <strong>Insight de Negocio:</strong><br>
        La colaboradora <strong>Judith Echeverria</strong> concentra actualmente la gestión completa de las compras críticas y en proceso de la estructura (<code>OC estructura</code> y <code>OC de anclas y placas</code>). Cualquier retraso en su flujo operativo detendrá el inicio de la instalación física de materiales metálicos en obra.
    </div>
    """, unsafe_allow_html=True)
    
    # Relationship 2: Dependency Design -> Purchases
    st.markdown("""
    <div style="padding:15px; border-radius:8px; border-left: 5px solid #ff7f0e; background-color: rgba(255, 127, 14, 0.08); margin-bottom: 20px;">
        <h4 style="margin-top:0; color: #ff7f0e;">⚙️ 2. Dependencias Técnicas Cruzadas</h4>
        <strong>Origen:</strong> ID 3 (Diseño - Carlos Mendez) ➡️ ID 2 (Compras - Judith Echeverria)<br>
        <strong>Tipo de Relación:</strong> Dependencia Técnica de Alcance<br><br>
        <strong>Insight de Negocio:</strong><br>
        La liberación de la <strong>OC de Estructura (ID 2)</strong> por parte de Compras se encuentra condicionada por la validación técnica y el visto bueno de <strong>NIDEC</strong> sobre el diseño físico estructurado a cargo de <strong>Carlos Mendez (ID 3)</strong>. El departamento de Compras no puede formalizar contratos definitivos sin esta definición técnica de ingeniería previa.
    </div>
    """, unsafe_allow_html=True)

    # Relationship 3: Status vs Reality
    st.markdown("""
    <div style="padding:15px; border-radius:8px; border-left: 5px solid #1f77b4; background-color: rgba(31, 119, 180, 0.08); margin-bottom: 20px;">
        <h4 style="margin-top:0; color: #1f77b4;">📅 3. Advertencia de Entrega Pendiente (Estatus vs Realidad)</h4>
        <strong>Origen:</strong> ID 5 (Memoria de cálculo estructural)<br>
        <strong>Tipo de Relación:</strong> Desfase Temporal Comparativo<br><br>
        <strong>Insight de Negocio:</strong><br>
        Aunque la <strong>Memoria de Cálculo Estructural (ID 5)</strong> figura administrativamente bajo un estatus <strong>'Cerrado'</strong> en el sistema, la descripción del siguiente paso indica un entregable físico clave programado para el <em>próximo miércoles 15</em>. Se sugiere realizar seguimiento proactivo para validar la recepción de la memoria física y evitar desajustes en las auditorías de diseño.
    </div>
    """, unsafe_allow_html=True)