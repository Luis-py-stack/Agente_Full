import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# ==============================================================================
# CONFIGURACIÓN DE PÁGINA
# ==============================================================================
st.set_page_config(
    page_title="Centro de Mando Operativo",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados para pulir la interfaz
st.markdown("""
<style>
    .metric-card {
        background-color: #ffffff;
        border-radius: 8px;
        padding: 15px;
        border-left: 5px solid #1E88E5;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12);
    }
    .critical-card {
        background-color: #FFF5F5;
        border: 1px solid #FEB2B2;
        border-left: 6px solid #E53E3E;
        padding: 16px;
        border-radius: 8px;
        margin-bottom: 12px;
    }
    .critical-title {
        color: #C53030;
        font-weight: 700;
        font-size: 1.05rem;
    }
    .critical-step {
        color: #2D3748;
        font-size: 0.95rem;
        margin-top: 4px;
    }
</style>
""", unsafe_allow_html=True)

# Paleta semántica estandarizada
STATUS_COLORS = {
    "Critico": "#E53E3E",     # Rojo Alerta
    "En proceso": "#3182CE",  # Azul Operativo
    "Cerrado": "#38A169"      # Verde Éxito
}

# ==============================================================================
# CARGA Y PREPARACIÓN DE DATOS (DUMMY DATA ROBUSTA)
# ==============================================================================
@st.cache_data
def load_data():
    raw_data = [
        {"ID": 1, "Fecha captura": "2026-07-01", "Concepto": "OC cimentaciones", "Departamento": "Compras", "Contratista": "Grupo Constructor SA", "Responsable": None, "Estatus": "Cerrado", "Siguiente paso": "ya se tiene cotizacion con Rangel, se comparte el dia de hoy para revision"},
        {"ID": 2, "Fecha captura": "2026-07-02", "Concepto": "OC estructura", "Departamento": "Compras", "Contratista": "TECOIMSA", "Responsable": "Judith Echeverria", "Estatus": "Critico", "Siguiente paso": "Se comparte OC el dia de hoy, anticipo se paga en 15 dias, en confirmacion de reunion el dia de hoy (TECOIMSA)"},
        {"ID": 3, "Fecha captura": "2026-07-03", "Concepto": "Entrega diseño de estructura", "Departamento": "Diseño", "Contratista": None, "Responsable": "Carlos Mendez", "Estatus": "En proceso", "Siguiente paso": "En proceso de revision y vobo de NIDEC"},
        {"ID": 4, "Fecha captura": "2026-07-04", "Concepto": "OC de anclas y placas", "Departamento": "Compras", "Contratista": "Aceros Monterrey", "Responsable": "Judith Echeverria", "Estatus": "En proceso", "Siguiente paso": "Ya se comenzo cotizacion de materiales para entrega a Luis Ramirez. (tiempo de fabricacion 4 dias)"},
        {"ID": 5, "Fecha captura": "2026-07-05", "Concepto": "Memoria calculo estructural (estructura metalica)", "Departamento": "Diseño", "Contratista": None, "Responsable": None, "Estatus": "Cerrado", "Siguiente paso": "Se espera entrega el proximo miercoles 15"},
        {"ID": 6, "Fecha captura": "2026-07-06", "Concepto": "Revisión de planos hidrosanitarios", "Departamento": "Diseño", "Contratista": "HidroSistemas", "Responsable": "Carlos Mendez", "Estatus": "Critico", "Siguiente paso": "Resolver interferencias con estructura metálica antes del viernes"},
        {"ID": 7, "Fecha captura": "2026-07-07", "Concepto": "OC Luminarias LED", "Departamento": "Compras", "Contratista": "IluminaTech", "Responsable": "Judith Echeverria", "Estatus": "En proceso", "Siguiente paso": "Esperando aprobación de catálogo por parte del cliente"},
        {"ID": 8, "Fecha captura": "2026-07-08", "Concepto": "Modelado BIM Planta Baja", "Departamento": "Diseño", "Contratista": None, "Responsable": "Carlos Mendez", "Estatus": "En proceso", "Siguiente paso": "Subir modelo coordinado a la nube compartida"},
        {"ID": 9, "Fecha captura": "2026-07-09", "Concepto": "OC Concreto F'c 250", "Departamento": "Compras", "Contratista": "Cemex", "Responsable": None, "Estatus": "Critico", "Siguiente paso": "Autorizar crédito para garantizar colado de la siguiente semana"},
        {"ID": 10, "Fecha captura": "2026-07-10", "Concepto": "Catálogo de conceptos acabados", "Departamento": "Diseño", "Contratista": None, "Responsable": "Ana Karen Ortiz", "Estatus": "Cerrado", "Siguiente paso": "Entregado a compras para cotización general"}
    ]
    df = pd.DataFrame(raw_data)
    df["Fecha captura"] = pd.to_datetime(df["Fecha captura"]).dt.date
    return df

df_raw = load_data()

# ==============================================================================
# BARRA LATERAL: FILTROS
# ==============================================================================
st.sidebar.title("🎛️ Filtros de Control")

# Normalizar nulos para dropdowns
df_processed = df_raw.copy()
df_processed["Responsable_Display"] = df_processed["Responsable"].fillna("Sin Responsable Asignado")
df_processed["Contratista_Display"] = df_processed["Contratista"].fillna("Sin Contratista")

# 1. Rango Temporal
st.sidebar.subheader("📅 Rango Temporal")
min_date = df_processed["Fecha captura"].min()
max_date = df_processed["Fecha captura"].max()

date_range = st.sidebar.date_input(
    "Seleccionar periodo:",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# 2. Segmentación Organizacional
st.sidebar.subheader("🏢 Segmentación")
all_depts = sorted(df_processed["Departamento"].unique().tolist())
selected_depts = st.sidebar.multiselect(
    "Departamento:",
    options=all_depts,
    default=all_depts
)

# 3. Control de Riesgo y Avance
st.sidebar.subheader("🚦 Estatus")
all_status = ["Critico", "En proceso", "Cerrado"]
selected_status = st.sidebar.multiselect(
    "Estatus de la tarea:",
    options=all_status,
    default=all_status
)

# 4. Filtro de Asignación
st.sidebar.subheader("👥 Asignación")
all_responsibles = sorted(df_processed["Responsable_Display"].unique().tolist())
selected_responsibles = st.sidebar.multiselect(
    "Responsable:",
    options=all_responsibles,
    default=all_responsibles
)

all_contractors = sorted(df_processed["Contratista_Display"].unique().tolist())
selected_contractors = st.sidebar.multiselect(
    "Contratista:",
    options=all_contractors,
    default=all_contractors
)

# 5. Búsqueda Rápida
st.sidebar.subheader("🔍 Búsqueda Rápida")
search_query = st.sidebar.text_input("Buscar en Concepto o Siguiente paso:", placeholder="ej. cotización, estructura...")

# Botón de Restablecimiento (Streamlit Rerun Trigger)
if st.sidebar.button("🔄 Restablecer Filtros", use_container_width=True):
    st.rerun()

# ==============================================================================
# APLICACIÓN DE FILTROS
# ==============================================================================
filtered_df = df_processed.copy()

# Filtrar por fecha
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
    filtered_df = filtered_df[(filtered_df["Fecha captura"] >= start_date) & (filtered_df["Fecha captura"] <= end_date)]
elif isinstance(date_range, tuple) and len(date_range) == 1:
    filtered_df = filtered_df[filtered_df["Fecha captura"] == date_range[0]]

# Filtrar por listas de selección
filtered_df = filtered_df[
    (filtered_df["Departamento"].isin(selected_depts)) &
    (filtered_df["Estatus"].isin(selected_status)) &
    (filtered_df["Responsable_Display"].isin(selected_responsibles)) &
    (filtered_df["Contratista_Display"].isin(selected_contractors))
]

# Filtrar por texto libre
if search_query.strip():
    query = search_query.lower()
    filtered_df = filtered_df[
        filtered_df["Concepto"].str.lower().str.contains(query, na=False) |
        filtered_df["Siguiente paso"].str.lower().str.contains(query, na=False)
    ]

# ==============================================================================
# ENCABEZADO Y PROPÓSITO
# ==============================================================================
st.title("Centro de Mando Operativo: Control de Entregables y Adquisiciones")
st.caption("Monitoreo en tiempo real del estatus de tareas, mitigación de riesgos y seguimiento de acuerdos por departamento.")
st.markdown("---")

# ==============================================================================
# 3. FILA DE MÉTRICAS CLAVE
# ==============================================================================
total_tasks = len(filtered_df)
critical_tasks = len(filtered_df[filtered_df["Estatus"] == "Critico"])
in_process_tasks = len(filtered_df[filtered_df["Estatus"] == "En proceso"])
closed_tasks = len(filtered_df[filtered_df["Estatus"] == "Cerrado"])
unassigned_tasks = len(filtered_df[filtered_df["Responsable"].isna()])

closure_rate = (closed_tasks / total_tasks * 100) if total_tasks > 0 else 0.0

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric(label="Total de Tareas", value=total_tasks)
with col2:
    st.metric(
        label="Tareas Críticas",
        value=critical_tasks,
        delta=f"-{critical_tasks} urgentes" if critical_tasks > 0 else "0 alertas",
        delta_color="inverse"
    )
with col3:
    st.metric(label="En Proceso", value=in_process_tasks)
with col4:
    st.metric(label="Tasa de Cierre", value=f"{closure_rate:.1f}%")
with col5:
    st.metric(
        label="Sin Asignación",
        value=unassigned_tasks,
        delta=f"{unassigned_tasks} por asignar" if unassigned_tasks > 0 else "Todo asignado",
        delta_color="off"
    )

st.markdown("<br>", unsafe_allow_html=True)

# ==============================================================================
# 4. VISUALIZACIONES Y GRÁFICOS INTERACTIVOS
# ==============================================================================
if filtered_df.empty:
    st.warning("⚠️ No se encontraron registros con los filtros seleccionados.")
else:
    g_col1, g_col2 = st.columns(2)

    with g_col1:
        # Gráfico A: Barras Apiladas por Departamento
        st.subheader("📊 Distribución de Estatus por Departamento")
        dept_status_df = filtered_df.groupby(["Departamento", "Estatus"]).size().reset_index(name="Cantidad")
        fig_bar = px.bar(
            dept_status_df,
            x="Departamento",
            y="Cantidad",
            color="Estatus",
            color_discrete_map=STATUS_COLORS,
            barmode="stack",
            text_auto=True
        )
        fig_bar.update_layout(
            legend_title_text="Estatus",
            margin=dict(l=20, r=20, t=30, b=20),
            xaxis_title="Departamento",
            yaxis_title="Cantidad de Tareas"
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with g_col2:
        # Gráfico B: Carga de Trabajo por Responsable
        st.subheader("👤 Carga de Trabajo por Responsable")
        resp_df = filtered_df.groupby(["Responsable_Display", "Estatus"]).size().reset_index(name="Cantidad")
        fig_resp = px.bar(
            resp_df,
            y="Responsable_Display",
            x="Cantidad",
            color="Estatus",
            color_discrete_map=STATUS_COLORS,
            orientation="h",
            text_auto=True
        )
        fig_resp.update_layout(
            yaxis={'categoryorder': 'total ascending'},
            xaxis_title="Número de Tareas",
            yaxis_title="Responsable",
            legend_title_text="Estatus",
            margin=dict(l=20, r=20, t=30, b=20)
        )
        st.plotly_chart(fig_resp, use_container_width=True)

    g_col3, g_col4 = st.columns(2)

    with g_col3:
        # Gráfico C: Ritmo de Registro de Tareas
        st.subheader("📈 Ritmo de Registro de Tareas")
        timeline_df = filtered_df.groupby(["Fecha captura", "Departamento"]).size().reset_index(name="Cantidad")
        fig_time = px.line(
            timeline_df,
            x="Fecha captura",
            y="Cantidad",
            color="Departamento",
            markers=True,
            color_discrete_sequence=px.colors.qualitative.Safe
        )
        fig_time.update_layout(
            xaxis_title="Fecha de Captura",
            yaxis_title="Tareas Registradas",
            margin=dict(l=20, r=20, t=30, b=20)
        )
        st.plotly_chart(fig_time, use_container_width=True)

    with g_col4:
        # Gráfico D: Salud Global del Portafolio
        st.subheader("🍩 Salud Global del Portafolio")
        status_pie_df = filtered_df["Estatus"].value_counts().reset_index()
        status_pie_df.columns = ["Estatus", "Cantidad"]
        fig_donut = px.pie(
            status_pie_df,
            names="Estatus",
            values="Cantidad",
            hole=0.55,
            color="Estatus",
            color_discrete_map=STATUS_COLORS
        )
        fig_donut.update_traces(textinfo='percent+label', pull=[0.05, 0, 0])
        fig_donut.update_layout(
            showlegend=False,
            margin=dict(l=20, r=20, t=30, b=20)
        )
        st.plotly_chart(fig_donut, use_container_width=True)

# ==============================================================================
# 5. SECCIÓN INFERIOR: MÓDULO OPERATIVO Y TABLA DE ACCIÓN
# ==============================================================================
st.markdown("---")
st.header("⚡ Módulo de Acción y Seguimiento Detallado")

# 1. Panel de Alertas Rápidas (Tareas Críticas)
criticas_df = filtered_df[filtered_df["Estatus"] == "Critico"]

with st.expander(f"🚨 Tareas en Estado Crítico ({len(criticas_df)})", expanded=(len(criticas_df) > 0)):
    if criticas_df.empty:
        st.success("✅ No hay tareas críticas pendientes en este momento.")
    else:
        for _, row in criticas_df.iterrows():
            st.markdown(f"""
            <div class="critical-card">
                <div class="critical-title">ID #{row['ID']} - {row['Concepto']} <span style="font-size:0.85rem; font-weight:normal;">({row['Departamento']})</span></div>
                <div style="font-size:0.9rem; color:#4A5568; margin-top: 2px;">
                    <strong>Responsable:</strong> {row['Responsable_Display']} | <strong>Contratista:</strong> {row['Contratista_Display']} | <strong>Fecha:</strong> {row['Fecha captura']}
                </div>
                <div class="critical-step">
                    <strong>👉 Siguiente paso prioritario:</strong> {row['Siguiente paso']}
                </div>
            </div>
            """, unsafe_allow_html=True)

# 2. Tabla Maestra Interactiva
st.subheader("📋 Matriz Completa de Entregables")

display_columns = [
    "ID",
    "Fecha captura",
    "Departamento",
    "Concepto",
    "Responsable_Display",
    "Contratista_Display",
    "Estatus",
    "Siguiente paso"
]

export_df = filtered_df[display_columns].rename(columns={
    "Responsable_Display": "Responsable",
    "Contratista_Display": "Contratista"
})

st.dataframe(
    export_df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "ID": st.column_config.NumberColumn("ID", width="small"),
        "Fecha captura": st.column_config.DateColumn("Fecha Captura", format="YYYY-MM-DD"),
        "Estatus": st.column_config.TextColumn(
            "Estatus",
            help="Estado actual del requerimiento"
        ),
        "Concepto": st.column_config.TextColumn("Concepto", width="medium"),
        "Siguiente paso": st.column_config.TextColumn("Siguiente Paso / Compromiso", width="large"),
    }
)

# Descarga de datos
csv_data = export_df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Descargar datos filtrados (CSV)",
    data=csv_data,
    file_name=f"control_operativo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
    mime="text/csv"
)