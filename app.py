import pandas as pd
import plotly.express as px
import streamlit as st

# -----------------------------------------------------------------------------
# 1. CONFIGURACIÓN DE PÁGINA (PRIMERA LLAMADA OBLIGATORIA DE STREAMLIT)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Bitácora de Seguimiento de Tareas, OC y Diseño",
    page_icon="📊",
    layout="wide",
)

# -----------------------------------------------------------------------------
# 2. DATOS EN MEMORIA (AUTONOMÍA TOTAL DE DATOS)
# -----------------------------------------------------------------------------
DEFAULT_DATA = [
    {
        "id": 1,
        "fecha_captura": "2026-07-07 00:00:00",
        "concepto": "OC cimentaciones",
        "departamento": "Compras",
        "responsable": None,
        "estatus": "Cerrado",
        "siguiente_paso": (
            "ya se tiene cotizacion con Rangel, se comparte el dia de hoy para"
            " revision"
        ),
    },
    {
        "id": 2,
        "fecha_captura": "2026-07-07 00:00:00",
        "concepto": "OC estructura",
        "departamento": "Compras",
        "responsable": "Judith Echeverria",
        "estatus": "Critico",
        "siguiente_paso": (
            "Se comparte OC el dia de hoy, anticipo se paga en 15 dias, en"
            " confirmacion de reunion el dia de hoy  (TECOIMSA)"
        ),
    },
    {
        "id": 3,
        "fecha_captura": "2026-07-07 00:00:00",
        "concepto": "Entrega diseño de estructura",
        "departamento": "Diseño",
        "responsable": "Carlos Mendez",
        "estatus": "En proceso",
        "siguiente_paso": "En proceso de revision y vobo de NIDEC",
    },
    {
        "id": 4,
        "fecha_captura": "2026-07-07 00:00:00",
        "concepto": "OC de anclas y placas",
        "departamento": "Compras",
        "responsable": "Judith Echeverria",
        "estatus": "En proceso",
        "siguiente_paso": (
            "Ya se comenzo cotizacion de materiales para entrega a Luis"
            " Ramirez. (tiempo de fabricacion 4 dias)"
        ),
    },
    {
        "id": 5,
        "fecha_captura": "2026-07-07 00:00:00",
        "concepto": "Memoria calculo estructural (estructura metalica)",
        "departamento": "Diseño",
        "responsable": None,
        "estatus": "Cerrado",
        "siguiente_paso": "Se espera entrega el proximo miercoles 15",
    },
]

# -----------------------------------------------------------------------------
# 3. BARRA LATERAL (CARGA OPCIONAL Y FILTROS REACTIVOS)
# -----------------------------------------------------------------------------
st.sidebar.header("📁 Carga de Datos")
uploaded_file = st.sidebar.file_uploader(
    "Cargar archivo Excel o CSV", type=["xlsx", "csv"]
)

if uploaded_file is not None:
  try:
    if uploaded_file.name.endswith(".csv"):
      df_raw = pd.read_csv(uploaded_file)
    else:
      df_raw = pd.read_excel(uploaded_file)
    st.sidebar.success("✅ Archivo cargado correctamente")
  except Exception as e:
    st.sidebar.error(f"Error al cargar el archivo: {e}")
    df_raw = pd.DataFrame(DEFAULT_DATA)
else:
  df_raw = pd.DataFrame(DEFAULT_DATA)

# Copia defensiva y normalización de tipos
df = df_raw.copy()

if "responsable" in df.columns:
  df["responsable"] = (
      df["responsable"]
      .fillna("Sin Asignar")
      .replace({"": "Sin Asignar", None: "Sin Asignar"})
  )

if "fecha_captura" in df.columns:
  df["fecha_captura"] = pd.to_datetime(df["fecha_captura"], errors="coerce")

if "id" in df.columns:
  df["id"] = pd.to_numeric(df["id"], errors="coerce")

st.sidebar.divider()
st.sidebar.header("🔍 Filtros Dinámicos")

# Filtro por Departamento
if "departamento" in df.columns:
  depts = sorted([str(d) for d in df["departamento"].dropna().unique()])
  selected_depts = st.sidebar.multiselect(
      "Departamento", options=depts, default=depts
  )
else:
  selected_depts = []

# Filtro por Estatus Operativo
if "estatus" in df.columns:
  estatus_opts = sorted([str(e) for e in df["estatus"].dropna().unique()])
  selected_estatus = st.sidebar.multiselect(
      "Estatus Operativo", options=estatus_opts, default=estatus_opts
  )
else:
  selected_estatus = []

# Filtro por Responsable
if "responsable" in df.columns:
  resp_opts = sorted([str(r) for r in df["responsable"].dropna().unique()])
  selected_resp = st.sidebar.multiselect(
      "Responsable", options=resp_opts, default=resp_opts
  )
else:
  selected_resp = []

# Filtro por Rango de Fechas
date_range = None
if "fecha_captura" in df.columns and not df["fecha_captura"].dropna().empty:
  min_date = df["fecha_captura"].min().date()
  max_date = df["fecha_captura"].max().date()
  if min_date == max_date:
    date_range = (min_date, max_date)
    st.sidebar.info(f"📅 Fecha de captura: `{min_date}`")
  else:
    date_range = st.sidebar.date_input(
        "Rango de Fechas",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

# Buscador Libre
search_term = st.sidebar.text_input(
    "🔎 Búsqueda por palabra clave",
    value="",
    placeholder="Ej: cotización, TECOIMSA...",
)

# -----------------------------------------------------------------------------
# 4. APLICACIÓN DE FILTROS A DATOS
# -----------------------------------------------------------------------------
df_filtered = df.copy()

if "departamento" in df_filtered.columns and selected_depts:
  df_filtered = df_filtered[
      df_filtered["departamento"].astype(str).isin(selected_depts)
  ]

if "estatus" in df_filtered.columns and selected_estatus:
  df_filtered = df_filtered[
      df_filtered["estatus"].astype(str).isin(selected_estatus)
  ]

if "responsable" in df_filtered.columns and selected_resp:
  df_filtered = df_filtered[
      df_filtered["responsable"].astype(str).isin(selected_resp)
  ]

if (
    date_range
    and isinstance(date_range, tuple)
    and len(date_range) == 2
    and "fecha_captura" in df_filtered.columns
):
  start_d, end_d = date_range
  df_filtered = df_filtered[
      (df_filtered["fecha_captura"].dt.date >= start_d)
      & (df_filtered["fecha_captura"].dt.date <= end_d)
  ]

if search_term:
  mask = pd.Series(False, index=df_filtered.index)
  if "concepto" in df_filtered.columns:
    mask = mask | df_filtered["concepto"].astype(str).str.contains(
        search_term, case=False, na=False
    )
  if "siguiente_paso" in df_filtered.columns:
    mask = mask | df_filtered["siguiente_paso"].astype(str).str.contains(
        search_term, case=False, na=False
    )
  df_filtered = df_filtered[mask]

# -----------------------------------------------------------------------------
# 5. ENCABEZADO PRINCIPAL Y METADATOS
# -----------------------------------------------------------------------------
st.title("📊 Bitácora de Seguimiento de Tareas, Órdenes de Compra y Diseño")

with st.expander("ℹ️ Metadatos y Resumen Ejecutivo", expanded=False):
  st.markdown("""
    * **Entidad / Asunto:** Gestión de Proyectos, Compras y Diseño Estructural
    * **Fecha de Captura:** 2026-07-07
    * **Resumen Ejecutivo:** Documento de control y seguimiento de órdenes de compra (OC) y entregables de diseño estructural y cimentaciones, con detalle de responsables, departamento, estatus operativo y acciones a seguir.
    """)

# -----------------------------------------------------------------------------
# 6. MATRIZ DE KPIS GLOBALES
# -----------------------------------------------------------------------------
total_reg = len(df_filtered)
cerrados_cnt = (
    len(df_filtered[df_filtered["estatus"] == "Cerrado"])
    if "estatus" in df_filtered.columns
    else 0
)
proceso_cnt = (
    len(df_filtered[df_filtered["estatus"] == "En proceso"])
    if "estatus" in df_filtered.columns
    else 0
)
critico_cnt = (
    len(df_filtered[df_filtered["estatus"] == "Critico"])
    if "estatus" in df_filtered.columns
    else 0
)
compras_cnt = (
    len(df_filtered[df_filtered["departamento"] == "Compras"])
    if "departamento" in df_filtered.columns
    else 0
)
diseno_cnt = (
    len(df_filtered[df_filtered["departamento"] == "Diseño"])
    if "departamento" in df_filtered.columns
    else 0
)

kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5, kpi_col6 = st.columns(6)

with kpi_col1:
  st.metric(
      "Total Registros",
      f"{total_reg} unidades",
      help="Total de ítems registrados",
  )

with kpi_col2:
  pct_c = (cerrados_cnt / total_reg * 100) if total_reg > 0 else 0
  st.metric(
      "Estatus Cerrado",
      f"{cerrados_cnt} unidades",
      delta=f"{pct_c:.0f}% del total",
      delta_color="normal",
  )

with kpi_col3:
  pct_p = (proceso_cnt / total_reg * 100) if total_reg > 0 else 0
  st.metric(
      "Estatus En proceso",
      f"{proceso_cnt} unidades",
      delta=f"{pct_p:.0f}% del total",
      delta_color="off",
  )

with kpi_col4:
  pct_crit = (critico_cnt / total_reg * 100) if total_reg > 0 else 0
  st.metric(
      "Estatus Crítico",
      f"{critico_cnt} unidades",
      delta=f"{pct_crit:.0f}% Atención",
      delta_color="inverse",
  )

with kpi_col5:
  pct_comp = (compras_cnt / total_reg * 100) if total_reg > 0 else 0
  st.metric(
      "Carga Compras",
      f"{compras_cnt} tareas",
      help=f"{pct_comp:.0f}% de la carga de trabajo",
  )

with kpi_col6:
  pct_dis = (diseno_cnt / total_reg * 100) if total_reg > 0 else 0
  st.metric(
      "Carga Diseño",
      f"{diseno_cnt} tareas",
      help=f"{pct_dis:.0f}% de la carga de trabajo",
  )

st.divider()

# Validación defensiva ante conjunto de datos vacío por filtros
if df_filtered.empty:
  st.warning(
      "⚠️ No se encontraron registros que coincidan con los filtros"
      " seleccionados. Por favor modifique los criterios en el menú lateral."
  )
  st.stop()

# -----------------------------------------------------------------------------
# 7. ORGANIZACIÓN POR PESTAÑAS
# -----------------------------------------------------------------------------
tab_operativo, tab_relaciones = st.tabs([
    "📋 Seguimiento Operativo (Hoja 1)",
    "🔗 Alertas y Relaciones Semánticas",
])

COLOR_MAP = {"Cerrado": "#2ecc71", "En proceso": "#f39c12", "Critico": "#e74c3c"}

# -----------------------------------------------------------------------------
# PESTAÑA 1: SEGUIMIENTO OPERATIVO
# -----------------------------------------------------------------------------
with tab_operativo:
  st.subheader("📈 Análisis de Distribución y Carga Operativa")

  col_chart1, col_chart2 = st.columns(2)

  with col_chart1:
    fig_pie = px.pie(
        df_filtered,
        names="estatus",
        title="<b>Distribución por Estatus Operativo</b>",
        hole=0.45,
        color="estatus",
        color_discrete_map=COLOR_MAP,
    )
    fig_pie.update_traces(textinfo="percent+label")
    fig_pie.update_layout(
        legend=dict(
            orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5
        ),
        margin=dict(l=20, r=20, t=40, b=40),
    )
    st.plotly_chart(fig_pie, use_container_width=True)

  with col_chart2:
    dept_status = (
        df_filtered.groupby(["departamento", "estatus"])
        .size()
        .reset_index(name="conteo")
    )
    fig_bar_dept = px.bar(
        dept_status,
        x="departamento",
        y="conteo",
        color="estatus",
        title="<b>Carga de Trabajo por Departamento y Estatus</b>",
        barmode="stack",
        color_discrete_map=COLOR_MAP,
        labels={
            "departamento": "Departamento",
            "conteo": "Cantidad de Tareas",
            "estatus": "Estatus",
        },
    )
    fig_bar_dept.update_layout(
        legend=dict(
            orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5
        ),
        margin=dict(l=20, r=20, t=40, b=40),
        yaxis=dict(tick0=0, dtick=1),
    )
    st.plotly_chart(fig_bar_dept, use_container_width=True)

  st.subheader("👤 Carga de Trabajo por Responsable")
  resp_status = (
      df_filtered.groupby(["responsable", "estatus"])
      .size()
      .reset_index(name="conteo")
  )
  fig_bar_resp = px.bar(
      resp_status,
      y="responsable",
      x="conteo",
      color="estatus",
      orientation="h",
      title="<b>Desglose de Tareas por Responsable</b>",
      barmode="stack",
      color_discrete_map=COLOR_MAP,
      labels={
          "responsable": "Responsable",
          "conteo": "Cantidad de Tareas",
          "estatus": "Estatus",
      },
  )
  fig_bar_resp.update_layout(
      legend=dict(
          orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5
      ),
      margin=dict(l=20, r=20, t=40, b=40),
      xaxis=dict(tick0=0, dtick=1),
  )
  st.plotly_chart(fig_bar_resp, use_container_width=True)

  st.subheader("📄 Visor Detallado de Tareas")
  st.dataframe(
      df_filtered,
      use_container_width=True,
      hide_index=True,
      column_config={
          "id": st.column_config.NumberColumn("ID Task", format="%d"),
          "fecha_captura": st.column_config.DateColumn(
              "Fecha Captura", format="YYYY-MM-DD"
          ),
          "concepto": st.column_config.TextColumn(
              "Concepto / Entregable", width="medium"
          ),
          "departamento": st.column_config.TextColumn(
              "Departamento", width="small"
          ),
          "responsable": st.column_config.TextColumn(
              "Responsable", default="Sin Asignar"
          ),
          "estatus": st.column_config.SelectboxColumn(
              "Estatus", options=["Cerrado", "En proceso", "Critico"]
          ),
          "siguiente_paso": st.column_config.TextColumn(
              "Siguiente Paso / Observaciones", width="large"
          ),
      },
  )

  # Descarga CSV
  csv_bytes = df_filtered.to_csv(index=False).encode("utf-8")
  st.download_button(
      label="📥 Descargar Bitácora Filtrada (CSV)",
      data=csv_bytes,
      file_name="bitacora_seguimiento_filtrada.csv",
      mime="text/csv",
  )

# -----------------------------------------------------------------------------
# PESTAÑA 2: ALERTAS Y RELACIONES SEMÁNTICAS
# -----------------------------------------------------------------------------
with tab_relaciones:
  st.subheader("🚨 Alertas de Control y Mapeo Semántico")

  critical_items = df_filtered[df_filtered["estatus"] == "Critico"]
  if not critical_items.empty:
    st.warning(
        "🚨 **Atención Requerida:** Se ha identificado al menos una tarea en"
        " estado CRÍTICO."
    )
    for _, row in critical_items.iterrows():
      with st.container():
        st.markdown(f"""
                * **ID Tarea:** `{row['id']}`
                * **Concepto:** **{row['concepto']}**
                * **Departamento:** {row['departamento']} | **Responsable:** {row['responsable']}
                * **Acción Inmediata / Siguiente Paso:**  
                > {row['siguiente_paso']}
                """)
  else:
    st.info(
        "✅ No existen tareas en estatus Crítico dentro de los filtros"
        " seleccionados."
    )

  st.divider()
  st.subheader("📌 Desglose y Agregación por Departamento")

  col_rel_comp, col_rel_dis = st.columns(2)

  with col_rel_comp:
    st.markdown("#### 🛍️ Departamento: Compras")
    df_comp = df_filtered[df_filtered["departamento"] == "Compras"]
    if not df_comp.empty:
      for _, row in df_comp.iterrows():
        badge_color = (
            "🔴"
            if row["estatus"] == "Critico"
            else ("🟢" if row["estatus"] == "Cerrado" else "🟠")
        )
        st.write(
            f"{badge_color} **ID {row['id']} - {row['concepto']}**"
            f" ({row['estatus']})"
        )
        st.caption(
            f"Responsable: {row['responsable']} | Observación:"
            f" {row['siguiente_paso']}"
        )
    else:
      st.info("No hay tareas de Compras registradas en la selección actual.")

  with col_rel_dis:
    st.markdown("#### 📐 Departamento: Diseño")
    df_dis = df_filtered[df_filtered["departamento"] == "Diseño"]
    if not df_dis.empty:
      for _, row in df_dis.iterrows():
        badge_color = (
            "🔴"
            if row["estatus"] == "Critico"
            else ("🟢" if row["estatus"] == "Cerrado" else "🟠")
        )
        st.write(
            f"{badge_color} **ID {row['id']} - {row['concepto']}**"
            f" ({row['estatus']})"
        )
        st.caption(
            f"Responsable: {row['responsable']} | Observación:"
            f" {row['siguiente_paso']}"
        )
    else:
      st.info("No hay tareas de Diseño registradas en la selección actual.")