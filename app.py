# app.py
import datetime
import pandas as pd
import plotly.express as px
import streamlit as st

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(
    page_title="Control de Proyectos: Compras y Diseño",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Estilo CSS personalizado para mejorar la tipografía y contenedores de métricas
st.markdown(
    """
    <style>
    div[data-testid="stMetricValue"] {
        font-size: 28px;
        font-weight: bold;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 14px;
        font-weight: 500;
    }
    .main-title {
        font-size: 38px;
        font-weight: 800;
        color: #1E293B;
        margin-bottom: 5px;
    }
    .subtitle {
        font-size: 16px;
        color: #64748B;
        margin-bottom: 25px;
    }
    </style>
""",
    unsafe_allow_html=True,
)


# 2. CARGA Y PREPARACIÓN DE DATOS (Mecanismo robusto de Mock Data)
@st.cache_data
def load_data():
    # Estructura e información basada estrictamente en la documentación JSON provista.
    raw_data = [
        {
            "ID": 1,
            "Fecha captura": "2026-07-07",
            "Concepto": "OC cimentaciones",
            "Departamento": "Compras",
            "Contratista": None,
            "Responsable": None,
            "Estatus": "Cerrado",
            "Siguiente paso": "ya se tiene cotizacion con Rangel, se comparte el dia de hoy para revision",
        },
        {
            "ID": 2,
            "Fecha captura": "2026-07-07",
            "Concepto": "OC estructura",
            "Departamento": "Compras",
            "Contratista": None,
            "Responsable": "Judith Echeverria",
            "Estatus": "Critico",
            "Siguiente paso": "Se comparte OC el dia de hoy, anticipo se paga en 15 dias, en confirmacion de reunion el dia de hoy  (TECOIMSA)",
        },
        {
            "ID": 3,
            "Fecha captura": "2026-07-07",
            "Concepto": "Entrega diseño de estructura",
            "Departamento": "Diseño",
            "Contratista": None,
            "Responsable": "Carlos Mendez",
            "Estatus": "En proceso",
            "Siguiente paso": "En proceso de revision y vobo de NIDEC",
        },
        {
            "ID": 4,
            "Fecha captura": "2026-07-07",
            "Concepto": "OC de anclas y placas",
            "Departamento": "Compras",
            "Contratista": None,
            "Responsable": "Judith Echeverria",
            "Estatus": "En proceso",
            "Siguiente paso": "Ya se comenzo cotizacion de materiales para entrega a Luis Ramirez. (tiempo de fabricacion 4 dias)",
        },
        {
            "ID": 5,
            "Fecha captura": "2026-07-07",
            "Concepto": "Memoria calculo estructural (estructura metalica)",
            "Departamento": "Diseño",
            "Contratista": None,
            "Responsable": None,
            "Estatus": "Cerrado",
            "Siguiente paso": "Se espera entrega el proximo miercoles 15",
        },
    ]

    df = pd.DataFrame(raw_data)

    # Conversión de tipos y homologación de nulos según requerimiento de UX
    df["Fecha captura"] = pd.to_datetime(df["Fecha captura"]).dt.date
    df["Contratista"] = df["Contratista"].fillna("Interno")
    df["Responsable"] = df["Responsable"].fillna("⚠️ Sin Asignar")

    return df


df_base = load_data()


# 3. BARRA LATERAL (Filtros de Búsqueda)
st.sidebar.markdown("## 🔍 Filtros de Búsqueda")

# Filtro 1: Rango de Fechas
min_date = df_base["Fecha captura"].min()
max_date = df_base["Fecha captura"].max()

# Margen de seguridad en caso de fechas vacías
if pd.isnull(min_date):
    min_date = datetime.date.today()
if pd.isnull(max_date):
    max_date = datetime.date.today()

date_range = st.sidebar.date_input(
    "Rango de Fecha de Captura",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

# Filtro 2: Departamento (Multiselect)
depts = sorted(df_base["Departamento"].unique())
selected_depts = st.sidebar.multiselect(
    "Filtrar por Departamento", options=depts, default=depts
)

# Filtro 3: Estatus (Multiselect)
statuses = sorted(df_base["Estatus"].unique())
selected_statuses = st.sidebar.multiselect(
    "Estado de la Actividad", options=statuses, default=statuses
)

# Filtro 4: Responsable (Multiselect con opción "Sin Asignar")
responsibles = sorted(df_base["Responsable"].unique())
selected_responsibles = st.sidebar.multiselect(
    "Responsable Asignado", options=responsibles, default=responsibles
)

# Filtro 5: Buscador de texto libre
search_term = st.sidebar.text_input("Buscar Concepto o Nota", value="")


# --- APLICACIÓN DE FILTROS ---
df_filtered = df_base.copy()

# Filtrar Fechas de forma segura
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
    df_filtered = df_filtered[
        (df_filtered["Fecha captura"] >= start_date)
        & (df_filtered["Fecha captura"] <= end_date)
    ]

# Filtrar por multiselecciones
if selected_depts:
    df_filtered = df_filtered[df_filtered["Departamento"].isin(selected_depts)]
else:
    df_filtered = df_filtered[
        df_filtered["Departamento"].isin([])
    ]  # Evita mostrar todo si deseleccionan todo

if selected_statuses:
    df_filtered = df_filtered[df_filtered["Estatus"].isin(selected_statuses)]
else:
    df_filtered = df_filtered[df_filtered["Estatus"].isin([])]

if selected_responsibles:
    df_filtered = df_filtered[
        df_filtered["Responsable"].isin(selected_responsibles)
    ]
else:
    df_filtered = df_filtered[df_filtered["Responsable"].isin([])]

# Filtrar por texto libre (Concepto o Siguiente paso)
if search_term:
    term = search_term.lower()
    df_filtered = df_filtered[
        df_filtered["Concepto"].str.lower().str.contains(term)
        | df_filtered["Siguiente paso"].str.lower().str.contains(term)
    ]


# 4. ENCABEZADO PRINCIPAL
st.markdown(
    '<div class="main-title">🚀 Panel de Control Operativo e Hitos</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="subtitle">Herramienta táctica para líderes de área. Identifica cuellos de botella en adquisiciones, distribución de carga de trabajo y seguimiento operativo inmediato.</div>',
    unsafe_allow_html=True,
)


# 5. TARJETAS DE MÉTRICAS CLAVE (KPIs)
total_records = len(df_filtered)
critical_count = len(df_filtered[df_filtered["Estatus"] == "Critico"])
in_progress_count = len(df_filtered[df_filtered["Estatus"] == "En proceso"])
closed_count = len(df_filtered[df_filtered["Estatus"] == "Cerrado"])

efficiency = (
    (closed_count / total_records * 100) if total_records > 0 else 0.0
)

kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)

with kpi_col1:
    st.metric(label="Tareas Registradas", value=total_records)

with kpi_col2:
    # Mostramos alerta delta de atención inmediata en base a tareas críticas.
    st.metric(
        label="🚨 Alertas Críticas",
        value=critical_count,
        delta=f"{critical_count} Críticas" if critical_count > 0 else None,
        delta_color="inverse",
    )

with kpi_col3:
    st.metric(label="⚙️ En Proceso", value=in_progress_count)

with kpi_col4:
    st.metric(label="✅ Tareas Completadas", value=f"{efficiency:.1f}%")

st.markdown("---")


# 6. GRÁFICOS INTERACTIVOS (Columnas duales)
chart_col1, chart_col2 = st.columns(2)

# Configuración del mapeo de colores semánticos solicitado
color_map = {"Cerrado": "#10B981", "En proceso": "#3B82F6", "Critico": "#EF4444"}

with chart_col1:
    st.subheader("⚖️ Balance de Carga por Departamento")

    if not df_filtered.empty:
        # Agrupación y conteo rápido para visualización
        df_grouped_dept = (
            df_filtered.groupby(["Departamento", "Estatus"])
            .size()
            .reset_index(name="Tareas")
        )

        fig_dept = px.bar(
            df_grouped_dept,
            y="Departamento",
            x="Tareas",
            color="Estatus",
            orientation="h",
            color_discrete_map=color_map,
            category_orders={"Estatus": ["Critico", "En proceso", "Cerrado"]},
            text="Tareas",
        )

        fig_dept.update_layout(
            legend_title_text="Estatus",
            xaxis_title="Número de Tareas",
            yaxis_title="Departamento",
            height=320,
            margin=dict(l=0, r=10, t=20, b=10),
            hovermode="y unified",
        )
        st.plotly_chart(fig_dept, use_container_width=True)
    else:
        st.info("No hay datos que coincidan con los filtros actuales.")

with chart_col2:
    st.subheader("👥 Productividad y Responsabilidad")

    if not df_filtered.empty:
        # Agrupación para visualizar la distribución por responsable
        df_grouped_resp = (
            df_filtered.groupby(["Responsable", "Estatus"])
            .size()
            .reset_index(name="Tareas")
        )

        fig_resp = px.bar(
            df_grouped_resp,
            x="Responsable",
            y="Tareas",
            color="Estatus",
            barmode="group",
            color_discrete_map=color_map,
            category_orders={"Estatus": ["Critico", "En proceso", "Cerrado"]},
            text="Tareas",
        )

        fig_resp.update_layout(
            legend_title_text="Estatus",
            xaxis_title="Responsable",
            yaxis_title="Número de Tareas",
            height=320,
            margin=dict(l=10, r=0, t=20, b=10),
        )
        st.plotly_chart(fig_resp, use_container_width=True)
    else:
        st.info("No hay datos que coincidan con los filtros actuales.")

st.markdown("---")


# 7. TABLA DE DETALLES Y ACCIONES INMEDIATAS
st.subheader("📋 Plan de Acción y Siguientes Pasos")

if not df_filtered.empty:
    # Clonamos para dar formato visual sin afectar datos internos
    df_table = df_filtered.copy()

    # Mapeo estético de estatus con emojis recomendados
    status_emoji_mapping = {
        "Cerrado": "🟢 Cerrado",
        "En proceso": "🟡 En proceso",
        "Critico": "🔴 Crítico",
    }
    df_table["Estatus"] = df_table["Estatus"].map(status_emoji_mapping)

    # Exclusión del ID para limpieza visual
    df_table_clean = df_table.drop(columns=["ID"])

    # Renderización optimizada con configuración de anchos específicos
    st.dataframe(
        df_table_clean,
        use_container_width=True,
        column_config={
            "Fecha captura": st.column_config.DateColumn(
                "Fecha de Captura", format="YYYY-MM-DD"
            ),
            "Concepto": st.column_config.TextColumn("Concepto", width="medium"),
            "Departamento": st.column_config.TextColumn("Área"),
            "Contratista": st.column_config.TextColumn("Contratista"),
            "Responsable": st.column_config.TextColumn("Responsable"),
            "Estatus": st.column_config.TextColumn("Estatus"),
            "Siguiente paso": st.column_config.TextColumn(
                "Siguiente Paso (Nota de Seguimiento)", width="large"
            ),
        },
        hide_index=True,
    )
else:
    st.warning(
        "⚠️ No existen registros para los criterios de filtrado seleccionados."
    )


# 8. FEATURE DE VALOR AGREGADO (Expander interactivo para juntas diarias)
st.markdown(" ")
with st.expander("🔍 Ver detalle de Tareas Críticas de hoy", expanded=True):
    critical_only = df_filtered[df_filtered["Estatus"] == "Critico"]

    if not critical_only.empty:
        st.write(
            "Los siguientes elementos requieren **atención y desbloqueo inmediato** hoy:"
        )
        for _, row in critical_only.iterrows():
            st.error(
                f"🚨 **[{row['Departamento']}]** {row['Concepto']}  \n"
                f"**Responsable:** {row['Responsable']} | **Contratista:** {row['Contratista']}  \n"
                f"👉 **Siguiente Paso Comprometido:** {row['Siguiente paso']}"
            )
    else:
        st.success(
            "🎉 ¡Felicidades! No se registran tareas críticas pendientes bajo los filtros activos."
        )