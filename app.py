import streamlit as st
import pandas as pd
import plotly.express as px
import datetime

# -----------------------------------------------------------------------------
# 1. CONFIGURACIÓN DE LA PÁGINA
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Control de Compras y Diseño",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados para mejorar el diseño general
st.markdown("""
    <style>
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 15px;
        border-left: 5px solid #007bff;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .metric-title {
        font-size: 0.9rem;
        color: #6c757d;
        font-weight: bold;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: bold;
        color: #212529;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. GENERACIÓN DE DATOS (Muestra + Historial Dummy para visualización fluida)
# -----------------------------------------------------------------------------
@st.cache_data
def load_data():
    # Estructura base proporcionada
    base_data = [
        {
            "ID": 1, "Fecha captura": "2026-07-07", "Concepto": "OC cimentaciones",
            "Departamento": "Compras", "Contratista": None, "Responsable": None,
            "Estatus": "Cerrado", "Siguiente paso": "ya se tiene cotizacion con Rangel, se comparte el dia de hoy para revision"
        },
        {
            "ID": 2, "Fecha captura": "2026-07-07", "Concepto": "OC estructura",
            "Departamento": "Compras", "Contratista": None, "Responsable": "Judith Echeverria",
            "Estatus": "Critico", "Siguiente paso": "Se comparte OC el dia de hoy, anticipo se paga en 15 dias, en confirmacion de reunion el dia de hoy  (TECOIMSA)"
        },
        {
            "ID": 3, "Fecha captura": "2026-07-07", "Concepto": "Entrega diseño de estructura",
            "Departamento": "Diseño", "Contratista": None, "Responsable": "Carlos Mendez",
            "Estatus": "En proceso", "Siguiente paso": "En proceso de revision y vobo de NIDEC"
        },
        {
            "ID": 4, "Fecha captura": "2026-07-07", "Concepto": "OC de anclas y placas",
            "Departamento": "Compras", "Contratista": None, "Responsable": "Judith Echeverria",
            "Estatus": "En proceso", "Siguiente paso": "Ya se comenzo cotizacion de materiales para entrega a Luis Ramirez. (tiempo de fabricacion 4 dias)"
        },
        {
            "ID": 5, "Fecha captura": "2026-07-07", "Concepto": "Memoria calculo estructural (estructura metalica)",
            "Departamento": "Diseño", "Contratista": None, "Responsable": None,
            "Estatus": "Cerrado", "Siguiente paso": "Se espera entrega el proximo miercoles 15"
        }
    ]
    
    # Registros adicionales de simulación para dar riqueza visual a los históricos de gráficos
    extra_data = [
        {
            "ID": 6, "Fecha captura": "2026-07-01", "Concepto": "Estudios de Mecánica de Suelos",
            "Departamento": "Diseño", "Contratista": "Geotecnia SA", "Responsable": "Carlos Mendez",
            "Estatus": "Cerrado", "Siguiente paso": "Estudio entregado e integrado al diseño estructural."
        },
        {
            "ID": 7, "Fecha captura": "2026-07-03", "Concepto": "OC terracerías y excavación",
            "Departamento": "Compras", "Contratista": None, "Responsable": "Judith Echeverria",
            "Estatus": "Cerrado", "Siguiente paso": "Contrato firmado, inicio de operaciones el lunes."
        },
        {
            "ID": 8, "Fecha captura": "2026-07-05", "Concepto": "Diseño arquitectónico final",
            "Departamento": "Diseño", "Contratista": None, "Responsable": "Carlos Mendez",
            "Estatus": "En proceso", "Siguiente paso": "Modificaciones menores solicitadas por el cliente."
        },
        {
            "ID": 9, "Fecha captura": "2026-07-09", "Concepto": "OC Instalación Eléctrica Media Tensión",
            "Departamento": "Compras", "Contratista": None, "Responsable": "Judith Echeverria",
            "Estatus": "Critico", "Siguiente paso": "A espera de confirmación de presupuesto por alza en transformadores."
        },
        {
            "ID": 10, "Fecha captura": "2026-07-10", "Concepto": "Planos de Instalaciones Hidrosanitarias",
            "Departamento": "Diseño", "Contratista": None, "Responsable": None,
            "Estatus": "En proceso", "Siguiente paso": "Falta validación de acometidas municipales."
        },
        {
            "ID": 11, "Fecha captura": "2026-07-12", "Concepto": "OC de Herrería y Prefabricados",
            "Departamento": "Compras", "Contratista": None, "Responsable": "Judith Echeverria",
            "Estatus": "En proceso", "Siguiente paso": "Revisión de planos de taller de herrería."
        },
        {
            "ID": 12, "Fecha captura": "2026-07-12", "Concepto": "Diseño de fachadas y cancelería",
            "Departamento": "Diseño", "Contratista": None, "Responsable": "Carlos Mendez",
            "Estatus": "Critico", "Siguiente paso": "Ingeniería de detalle detenida por falta de definición de perfiles."
        }
    ]
    
    df = pd.DataFrame(base_data + extra_data)
    df["Fecha captura"] = pd.to_datetime(df["Fecha captura"]).dt.date
    # Mapear nulos en Responsable a "Sin Asignar" para filtros robustos
    df["Responsable"] = df["Responsable"].fillna("Sin Asignar")
    return df

df_original = load_data()

# -----------------------------------------------------------------------------
# 3. TÍTULO Y DESCRIPCIÓN DEL DASHBOARD
# -----------------------------------------------------------------------------
st.title("🏗️ Panel de Control y Tracking: Compras y Diseño")
st.markdown(
    """
    Este panel interactivo permite monitorear el avance de las órdenes de compra (OC), 
    entregables de diseño y tareas de construcción. Facilita la identificación de cuellos de botella, 
    asignación de responsables y la visualización de las acciones inmediatas para mitigar riesgos en la obra.
    """
)
st.markdown("---")

# -----------------------------------------------------------------------------
# 4. FILTROS EN LA BARRA LATERAL (st.sidebar)
# -----------------------------------------------------------------------------
st.sidebar.header("🔍 Filtros de Búsqueda")

# Rango de fechas
min_date = df_original["Fecha captura"].min()
max_date = df_original["Fecha captura"].max()

date_range = st.sidebar.date_input(
    "Rango de Fecha de Captura",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Filtro por Departamento
depts_available = df_original["Departamento"].unique().tolist()
selected_depts = st.sidebar.multiselect(
    "Filtrar por Departamento",
    options=depts_available,
    default=depts_available
)

# Filtro por Estatus
status_available = df_original["Estatus"].unique().tolist()
selected_status = st.sidebar.multiselect(
    "Estatus de la Tarea",
    options=status_available,
    default=status_available
)

# Filtro por Responsable
responsibles_available = df_original["Responsable"].unique().tolist()
selected_responsibles = st.sidebar.multiselect(
    "Responsable Asignado",
    options=responsibles_available,
    default=responsibles_available
)

# Aplicar filtros al DataFrame
df_filtered = df_original.copy()

# Manejo seguro de la selección de rango de fechas
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
    df_filtered = df_filtered[
        (df_filtered["Fecha captura"] >= start_date) & 
        (df_filtered["Fecha captura"] <= end_date)
    ]

if selected_depts:
    df_filtered = df_filtered[df_filtered["Departamento"].isin(selected_depts)]

if selected_status:
    df_filtered = df_filtered[df_filtered["Estatus"].isin(selected_status)]

if selected_responsibles:
    df_filtered = df_filtered[df_filtered["Responsable"].isin(selected_responsibles)]

# -----------------------------------------------------------------------------
# 5. TARJETAS DE MÉTRICAS CLAVE (st.metric)
# -----------------------------------------------------------------------------
total_tasks = len(df_filtered)
critical_tasks = len(df_filtered[df_filtered["Estatus"] == "Critico"])
in_progress_tasks = len(df_filtered[df_filtered["Estatus"] == "En proceso"])
closed_tasks = len(df_filtered[df_filtered["Estatus"] == "Cerrado"])

efficiency = (closed_tasks / total_tasks * 100) if total_tasks > 0 else 0.0

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="📊 Tareas Registradas", value=total_tasks)

with col2:
    st.metric(label="🚨 Tareas Críticas", value=critical_tasks, delta=f"{critical_tasks} críticas", delta_color="inverse")

with col3:
    st.metric(label="⚙️ En Proceso", value=in_progress_tasks)

with col4:
    st.metric(label="✅ Eficiencia de Cierre", value=f"{efficiency:.1f}%")

# Mensaje flotante de alerta si hay tareas críticas
if critical_tasks > 0:
    st.error(
        f"⚠️ **Atención Inmediata Requerida:** Hay **{critical_tasks}** tarea(s) en estatus **Crítico** "
        f"que requieren seguimiento o escalación técnica urgentemente."
    )

st.markdown("---")

# -----------------------------------------------------------------------------
# 6. GRÁFICOS INTERACTIVOS (Visualización de Datos)
# -----------------------------------------------------------------------------
char_col1, char_col2 = st.columns(2)

# Mapeo de colores estables para coherencia visual en todos los gráficos
color_map = {
    "Cerrado": "#28a745",     # Verde
    "En proceso": "#ffc107",  # Amarillo
    "Critico": "#dc3545"      # Rojo
}

with char_col1:
    st.subheader("📋 Carga de Trabajo por Departamento")
    if not df_filtered.empty:
        fig_dept = px.bar(
            df_filtered,
            x="Departamento",
            color="Estatus",
            title="Distribución de Tareas por Área",
            color_discrete_map=color_map,
            barmode="stack",
            height=350
        )
        fig_dept.update_layout(xaxis_title="Departamento", yaxis_title="Cantidad de Tareas")
        st.plotly_chart(fig_dept, use_container_width=True)
    else:
        st.info("Sin datos para generar gráfico de Departamentos debido a los filtros activos.")

with char_col2:
    st.subheader("👤 Productividad y Responsabilidades")
    if not df_filtered.empty:
        # Contar tareas por responsable y estatus
        fig_resp = px.bar(
            df_filtered,
            y="Responsable",
            color="Estatus",
            title="Tareas Activas por Colaborador",
            orientation="h",
            color_discrete_map=color_map,
            barmode="stack",
            height=350
        )
        fig_resp.update_layout(xaxis_title="Cantidad de Tareas", yaxis_title="Responsable")
        st.plotly_chart(fig_resp, use_container_width=True)
    else:
        st.info("Sin datos para generar gráfico de Responsables debido a los filtros activos.")

# Gráfico de tendencia a lo ancho completo
st.subheader("📈 Flujo de Requerimientos en el Tiempo")
if not df_filtered.empty:
    # Agrupar datos para ver el volumen diario de registros por departamento
    df_trend = df_filtered.groupby(["Fecha captura", "Departamento"]).size().reset_index(name="Tareas Registradas")
    df_trend = df_trend.sort_values(by="Fecha captura")
    
    fig_trend = px.line(
        df_trend,
        x="Fecha captura",
        y="Tareas Registradas",
        color="Departamento",
        markers=True,
        title="Tendencia de Registro de Tareas y OC",
        height=320,
        color_discrete_sequence=px.colors.qualitative.Safe
    )
    fig_trend.update_layout(
        xaxis_title="Fecha de Registro",
        yaxis_title="Cantidad",
        xaxis=dict(type='date')
    )
    st.plotly_chart(fig_trend, use_container_width=True)
else:
    st.info("Sin datos históricos disponibles en este rango seleccionado.")

st.markdown("---")

# -----------------------------------------------------------------------------
# 7. TABLA DE DETALLE OPERATIVO Y BITÁCORA (Sección Inferior)
# -----------------------------------------------------------------------------
st.subheader("📋 Bitácora de Acciones y Siguientes Pasos")

# Buscador de texto libre
search_query = st.text_input(
    "Buscar en la bitácora por palabras clave (ej: 'cotización', 'NIDEC', 'reunión'):",
    placeholder="Escribe aquí para buscar coincidencias..."
).strip()

# Filtrar tabla por término de búsqueda
df_table = df_filtered.copy()
if search_query:
    df_table = df_table[
        df_table["Concepto"].str.contains(search_query, case=False, na=False) |
        df_table["Siguiente paso"].str.contains(search_query, case=False, na=False)
    ]

# Omitir columna Contratista por no tener datos según lineamientos, reordenando columnas para lectura humana
display_columns = ["ID", "Estatus", "Departamento", "Concepto", "Responsable", "Siguiente paso", "Fecha captura"]
df_display = df_table[display_columns]

# Formateo visual y Emojis de Estatus en DataFrame para destacar rápidamente
def apply_status_emojis(val):
    if val == "Critico":
        return "🚨 Crítico"
    elif val == "En proceso":
        return "⚙️ En proceso"
    elif val == "Cerrado":
        return "✅ Cerrado"
    return val

df_display["Estatus"] = df_display["Estatus"].apply(apply_status_emojis)

# Estilo de Filas mediante Pandas Styler
def style_status_rows(row):
    color = ''
    if "🚨 Crítico" in str(row["Estatus"]):
        color = 'background-color: rgba(220, 53, 69, 0.12)'  # Rojo pálido suave
    elif "⚙️ En proceso" in str(row["Estatus"]):
        color = 'background-color: rgba(255, 193, 7, 0.12)'  # Amarillo pálido suave
    elif "✅ Cerrado" in str(row["Estatus"]):
        color = 'background-color: rgba(40, 167, 69, 0.08)'  # Verde pálido suave
    return [color] * len(row)

# Mostrar Tabla Interactiva
if not df_display.empty:
    styled_df = df_display.style.apply(style_status_rows, axis=1)
    st.dataframe(
        styled_df,
        use_container_width=True,
        hide_index=True
    )
    
    # Exportar datos a CSV
    csv_data = df_table.to_csv(index=False).encode('utf-8-sig')
    
    st.download_button(
        label="📥 Descargar Reporte Filtrado (CSV)",
        data=csv_data,
        file_name=f"reporte_obras_{datetime.date.today()}.csv",
        mime="text/csv"
    )
else:
    st.warning("No se encontraron registros que coincidan con la búsqueda de texto o filtros seleccionados.")