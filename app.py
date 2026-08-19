import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import io

# -----------------------------------------------------------------------------
# 1. CONFIGURACIÓN DE PÁGINA Y ESTILOS
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Panel de Control Operativo",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos personalizados para tarjetas de métricas, badges y espaciado
st.markdown("""
<style>
    /* Estilización de tarjetas métricas */
    div[data-testid="stMetricValue"] {
        font-size: 1.85rem !important;
        font-weight: 700 !important;
    }
    div[data-testid="stMetricDelta"] {
        font-size: 0.85rem !important;
        font-weight: 600 !important;
    }
    /* Estructura limpia de contenedores */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1.5rem;
    }
    .stTabs [data-baseweb="tab"] {
        height: 3rem;
        white-space: pre-wrap;
        font-weight: 600;
        font-size: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Paleta de colores semántica
COLOR_MAP = {
    "Critico": "#EF4444",     # Rojo alerta
    "En proceso": "#3B82F6",   # Azul activo
    "Cerrado": "#10B981"       # Verde completado
}

# -----------------------------------------------------------------------------
# 2. CARGA Y GENERACIÓN DE DATOS
# -----------------------------------------------------------------------------
@st.cache_data
def load_data():
    raw_data = [
        {
            "ID": 1,
            "Fecha captura": "2026-07-01",
            "Concepto": "OC cimentaciones",
            "Departamento": "Compras",
            "Contratista": None,
            "Responsable": None,
            "Estatus": "Cerrado",
            "Siguiente paso": "ya se tiene cotizacion con Rangel, se comparte el dia de hoy para revision"
        },
        {
            "ID": 2,
            "Fecha captura": "2026-07-03",
            "Concepto": "OC estructura principal",
            "Departamento": "Compras",
            "Contratista": None,
            "Responsable": "Judith Echeverria",
            "Estatus": "Critico",
            "Siguiente paso": "Se comparte OC el dia de hoy, anticipo se paga en 15 dias, en confirmacion de reunion (TECOIMSA)"
        },
        {
            "ID": 3,
            "Fecha captura": "2026-07-05",
            "Concepto": "Entrega diseño de estructura",
            "Departamento": "Diseño",
            "Contratista": None,
            "Responsable": "Carlos Mendez",
            "Estatus": "En proceso",
            "Siguiente paso": "En proceso de revision y vobo de NIDEC"
        },
        {
            "ID": 4,
            "Fecha captura": "2026-07-06",
            "Concepto": "OC Instalaciones Hidrosanitarias",
            "Departamento": "Compras",
            "Contratista": None,
            "Responsable": "Judith Echeverria",
            "Estatus": "En proceso",
            "Siguiente paso": "Esperando cuadro comparativo final de proveedores"
        },
        {
            "ID": 5,
            "Fecha captura": "2026-07-07",
            "Concepto": "Revisión memorias de cálculo pluvial",
            "Departamento": "Diseño",
            "Contratista": None,
            "Responsable": None,
            "Estatus": "Critico",
            "Siguiente paso": "Asignar ingeniero calculista para firma de planos oficiales"
        },
        {
            "ID": 6,
            "Fecha captura": "2026-07-08",
            "Concepto": "OC Transformador Eléctrico 500kVA",
            "Departamento": "Compras",
            "Contratista": None,
            "Responsable": "Judith Echeverria",
            "Estatus": "Critico",
            "Siguiente paso": "Definir tiempo de entrega crítico con fabricante Siemens"
        },
        {
            "ID": 7,
            "Fecha captura": "2026-07-09",
            "Concepto": "Planos arquitectónicos definitivos",
            "Departamento": "Diseño",
            "Contratista": None,
            "Responsable": "Carlos Mendez",
            "Estatus": "Cerrado",
            "Siguiente paso": "Expediente entregado y firmado por perito responsable"
        },
        {
            "ID": 8,
            "Fecha captura": "2026-07-10",
            "Concepto": "OC Concreto premezclado f'c=250",
            "Departamento": "Compras",
            "Contratista": None,
            "Responsable": "Judith Echeverria",
            "Estatus": "Cerrado",
            "Siguiente paso": "Programación de colado para la siguiente semana con Cemex"
        },
        {
            "ID": 9,
            "Fecha captura": "2026-07-12",
            "Concepto": "Diseño de fachadas y cancelería",
            "Departamento": "Diseño",
            "Contratista": None,
            "Responsable": "Carlos Mendez",
            "Estatus": "En proceso",
            "Siguiente paso": "Presentación de renders a comité directivo el jueves"
        },
        {
            "ID": 10,
            "Fecha captura": "2026-07-14",
            "Concepto": "OC Sistema contra incendios",
            "Departamento": "Compras",
            "Contratista": None,
            "Responsable": None,
            "Estatus": "En proceso",
            "Siguiente paso": "Solicitud de 3 cotizaciones base bajo norma NFPA"
        }
    ]
    df = pd.DataFrame(raw_data)
    df["Fecha captura"] = pd.to_datetime(df["Fecha captura"]).dt.date
    # Asignar etiqueta 'Sin Asignar' explícita para manejo en filtros
    df["Responsable_Display"] = df["Responsable"].fillna("Sin Asignar")
    return df

df_raw = load_data()

# -----------------------------------------------------------------------------
# 3. BARRA LATERAL: FILTROS INTERACTIVOS
# -----------------------------------------------------------------------------
st.sidebar.title("🎛️ Filtros de Control")
st.sidebar.markdown("Personalice la vista del panel operativo.")

# 1. Rango de Fechas
min_date = df_raw["Fecha captura"].min()
max_date = df_raw["Fecha captura"].max()

date_range = st.sidebar.date_input(
    "📅 Rango de Fechas (Captura):",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# 2. Filtro Departamento
dept_options = sorted(df_raw["Departamento"].unique().tolist())
selected_depts = st.sidebar.multiselect(
    "🏢 Departamento:",
    options=dept_options,
    default=dept_options
)

# 3. Filtro Estatus con Toggle "Solo Críticos"
solo_criticos = st.sidebar.toggle("🚨 Ver únicamente Críticos", value=False)

status_options = ["Critico", "En proceso", "Cerrado"]
if solo_criticos:
    selected_status = ["Critico"]
    st.sidebar.info("Modo de urgencia: Filtrando solo estatus **Crítico**.")
else:
    selected_status = st.sidebar.multiselect(
        "📊 Estatus:",
        options=status_options,
        default=status_options
    )

# 4. Filtro Responsable
resp_options = sorted(df_raw["Responsable_Display"].unique().tolist())
selected_resp = st.sidebar.multiselect(
    "👤 Responsable:",
    options=resp_options,
    default=resp_options
)

# 5. Buscador de Texto Libre
search_query = st.sidebar.text_input(
    "🔍 Buscar en Concepto / Siguiente Paso:",
    placeholder="Ej. TECOIMSA, Cimentación..."
).strip()

st.sidebar.markdown("---")
st.sidebar.caption("Centro de Control Operativo v1.2 • Actualizado en tiempo real")

# -----------------------------------------------------------------------------
# 4. APLICACIÓN DE FILTROS AL DATAFRAME
# -----------------------------------------------------------------------------
df_filtered = df_raw.copy()

# Filtrar por Fechas
if isinstance(date_range, (tuple, list)):
    if len(date_range) == 2:
        start_date, end_date = date_range
        df_filtered = df_filtered[
            (df_filtered["Fecha captura"] >= start_date) & 
            (df_filtered["Fecha captura"] <= end_date)
        ]
    elif len(date_range) == 1:
        df_filtered = df_filtered[df_filtered["Fecha captura"] >= date_range[0]]

# Filtrar por Departamento
if selected_depts:
    df_filtered = df_filtered[df_filtered["Departamento"].isin(selected_depts)]
else:
    df_filtered = df_filtered.iloc[0:0]

# Filtrar por Estatus
if selected_status:
    df_filtered = df_filtered[df_filtered["Estatus"].isin(selected_status)]
else:
    df_filtered = df_filtered.iloc[0:0]

# Filtrar por Responsable
if selected_resp:
    df_filtered = df_filtered[df_filtered["Responsable_Display"].isin(selected_resp)]
else:
    df_filtered = df_filtered.iloc[0:0]

# Filtrar por Búsqueda de Texto
if search_query:
    query_lower = search_query.lower()
    df_filtered = df_filtered[
        df_filtered["Concepto"].str.lower().str.contains(query_lower, na=False) |
        df_filtered["Siguiente paso"].str.lower().str.contains(query_lower, na=False)
    ]

# -----------------------------------------------------------------------------
# 5. CABECERA Y TARJETAS DE MÉTRICAS (KPIs)
# -----------------------------------------------------------------------------
st.title("Panel de Control y Seguimiento Operativo de Proyectos")
st.markdown(
    "**Monitoreo de estatus, asignación de responsables y gestión de bloqueos por departamento.**"
)
st.markdown("---")

total_tasks = len(df_filtered)
critical_tasks = len(df_filtered[df_filtered["Estatus"] == "Critico"])
in_progress_tasks = len(df_filtered[df_filtered["Estatus"] == "En proceso"])
closed_tasks = len(df_filtered[df_filtered["Estatus"] == "Cerrado"])
unassigned_tasks = len(df_filtered[df_filtered["Responsable_Display"] == "Sin Asignar"])

completion_rate = (closed_tasks / total_tasks * 100) if total_tasks > 0 else 0.0

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="📋 Total de Tareas",
        value=total_tasks,
        help="Conteo total de órdenes de compra y entregables registrados según los filtros activos."
    )

with col2:
    delta_crit = f"{critical_tasks} con bloqueo" if critical_tasks > 0 else "Sin alertas"
    st.metric(
        label="🚨 Ítems Críticos",
        value=critical_tasks,
        delta=delta_crit,
        delta_color="inverse",
        help="Tareas que requieren atención prioritaria o desescalamiento urgente."
    )

with col3:
    st.metric(
        label="⚡ En Proceso / Cierre",
        value=f"{in_progress_tasks} Activas",
        delta=f"{completion_rate:.1f}% Completadas",
        delta_color="normal",
        help="Distribución de tareas en ejecución y tasa de finalización efectiva."
    )

with col4:
    delta_unassigned = f"{unassigned_tasks} sin dueño" if unassigned_tasks > 0 else "100% Asignado"
    st.metric(
        label="⚠️ Sin Asignar / En Riesgo",
        value=unassigned_tasks,
        delta=delta_unassigned,
        delta_color="inverse" if unassigned_tasks > 0 else "normal",
        help="Requerimientos sin un responsable asignado para seguimiento."
    )

st.markdown("<br>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 6. PESTAÑAS: VISTA ANALÍTICA Y VISTA OPERATIVA
# -----------------------------------------------------------------------------
tab_analytics, tab_operations = st.tabs([
    "📈 Vista Analítica (Gráficos)",
    "📑 Vista Operativa y Tabla de Acción"
])

# -----------------------------------------------------------------------------
# PESTAÑA A: VISTA ANALÍTICA
# -----------------------------------------------------------------------------
with tab_analytics:
    if df_filtered.empty:
        st.warning("⚠️ No hay datos para mostrar con los filtros seleccionados.")
    else:
        col_g1, col_g2 = st.columns(2)

        with col_g1:
            st.subheader("Distribución de Estatus por Departamento")
            # Agrupar para gráfico de barras apiladas
            dept_status_df = (
                df_filtered.groupby(["Departamento", "Estatus"])
                .size()
                .reset_index(name="Cantidad")
            )
            
            fig_dept = px.bar(
                dept_status_df,
                x="Departamento",
                y="Cantidad",
                color="Estatus",
                color_discrete_map=COLOR_MAP,
                barmode="stack",
                text="Cantidad"
            )
            fig_dept.update_layout(
                margin=dict(l=20, r=20, t=30, b=20),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                xaxis_title="Departamento",
                yaxis_title="Cantidad de Tareas",
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                hovermode="x unified"
            )
            fig_dept.update_traces(textposition='inside', textfont=dict(color='white', size=12))
            st.plotly_chart(fig_dept, use_container_width=True)

        with col_g2:
            st.subheader("Carga de Trabajo por Responsable")
            # Gráfico de barras horizontales
            resp_status_df = (
                df_filtered.groupby(["Responsable_Display", "Estatus"])
                .size()
                .reset_index(name="Cantidad")
            )
            
            fig_resp = px.bar(
                resp_status_df,
                y="Responsable_Display",
                x="Cantidad",
                color="Estatus",
                color_discrete_map=COLOR_MAP,
                orientation="h",
                barmode="stack",
                text="Cantidad"
            )
            fig_resp.update_layout(
                margin=dict(l=20, r=20, t=30, b=20),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                xaxis_title="Número de Conceptos Asignados",
                yaxis_title="Responsable",
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)"
            )
            fig_resp.update_traces(textposition='inside', textfont=dict(color='white', size=12))
            st.plotly_chart(fig_resp, use_container_width=True)

        st.subheader("Ritmo de Captura y Evolución Temporal")
        # Gráfico temporal
        time_df = (
            df_filtered.groupby(["Fecha captura", "Estatus"])
            .size()
            .reset_index(name="Conteo")
            .sort_values("Fecha captura")
        )
        
        fig_time = px.line(
            time_df,
            x="Fecha captura",
            y="Conteo",
            color="Estatus",
            markers=True,
            color_discrete_map=COLOR_MAP
        )
        fig_time.update_layout(
            margin=dict(l=20, r=20, t=30, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            xaxis_title="Fecha de Captura",
            yaxis_title="Volumen Diario de Tareas",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig_time, use_container_width=True)

# -----------------------------------------------------------------------------
# PESTAÑA B: VISTA OPERATIVA Y TABLA DE ACCIÓN
# -----------------------------------------------------------------------------
with tab_operations:
    st.subheader("Tabla Maestra de Seguimiento y Acciones")
    
    if df_filtered.empty:
        st.warning("⚠️ No se encontraron registros con los criterios de búsqueda actuales.")
    else:
        # Preparación de DataFrame para visualización limpia
        display_df = df_filtered[[
            "ID", 
            "Fecha captura",
            "Estatus", 
            "Concepto", 
            "Departamento", 
            "Responsable_Display", 
            "Siguiente paso"
        ]].rename(columns={"Responsable_Display": "Responsable"})
        
        # Renderizado con configuración avanzada de columnas
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "ID": st.column_config.NumberColumn("ID", width="small"),
                "Fecha captura": st.column_config.DateColumn("Fecha Captura", format="YYYY-MM-DD", width="small"),
                "Estatus": st.column_config.SelectboxColumn(
                    "Estatus",
                    help="Estatus operativo",
                    width="small",
                    options=["Critico", "En proceso", "Cerrado"],
                    required=True
                ),
                "Concepto": st.column_config.TextColumn("Concepto / Requerimiento", width="medium"),
                "Departamento": st.column_config.TextColumn("Departamento", width="small"),
                "Responsable": st.column_config.TextColumn("Responsable Asignado", width="medium"),
                "Siguiente paso": st.column_config.TextColumn("Siguiente Paso / Plan de Acción", width="large")
            }
        )

        st.markdown("<br>", unsafe_allow_html=True)
        col_down1, col_down2, _ = st.columns([1.5, 1.5, 5])
        
        # 1. Descarga CSV
        csv_data = display_df.to_csv(index=False).encode('utf-8-sig')
        with col_down1:
            st.download_button(
                label="📥 Descargar CSV",
                data=csv_data,
                file_name=f"seguimiento_operativo_{date.today().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )

        # 2. Descarga Excel
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            display_df.to_excel(writer, index=False, sheet_name='Seguimiento')
        excel_data = excel_buffer.getvalue()

        with col_down2:
            st.download_button(
                label="📊 Descargar Excel",
                data=excel_data,
                file_name=f"seguimiento_operativo_{date.today().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )