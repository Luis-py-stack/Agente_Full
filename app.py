import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime

# 1. CONFIGURACIÓN DE LA PÁGINA (Debe ser el primer comando de Streamlit)
st.set_page_config(
    page_title="Panel de Control de Tráfico de Visitantes",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. CARGA DE DATOS Y GENERACIÓN DE DATOS DUMMY
@st.cache_data
def load_data():
    """
    Carga los datos del esquema. Si no existe un origen de datos físico,
    genera datos 'dummy' realistas basados en el esquema JSON provisto.
    """
    try:
        # Intento de cargar datos desde un archivo si existiera (ej: data.csv)
        df = pd.read_csv("data.csv")
    except Exception:
        # Generación de datos dummy según el esquema solicitado para el año 2026
        np.random.seed(42)
        rango_fechas = pd.date_range(start="2026-01-01", end="2026-03-31", freq="D")
        
        # Simulación de tráfico con comportamiento semanal (fines de semana con variación)
        visitantes = []
        for fecha in rango_fechas:
            base = 30
            semanal = 15 if fecha.dayofweek in [4, 5, 6] else 0  # Más tráfico fines de semana
            ruido = np.random.randint(-10, 15)
            visitantes.append(max(5, base + semanal + ruido))

        df = pd.DataFrame({
            "Fecha": rango_fechas,
            "Visitantes": visitantes
        })
    
    # Optimización de Tipos de Datos (Requisito UX)
    df["Fecha"] = pd.to_datetime(df["Fecha"])
    df["Visitantes"] = df["Visitantes"].astype(int)
    return df

# Inicialización de datos
df_raw = load_data()

# Límites absolutos de los datos para los filtros
min_date = df_raw["Fecha"].min().date()
max_date = df_raw["Fecha"].max().date()
min_vis = int(df_raw["Visitantes"].min())
max_vis = int(df_raw["Visitantes"].max())

# 3. BARRA LATERAL (Filtros y Estado de la Aplicación)
st.sidebar.header("Filtros de Análisis")

# Inicialización del estado de sesión para permitir el botón de restablecimiento
if "start_date" not in st.session_state:
    st.session_state.start_date = min_date
if "end_date" not in st.session_state:
    st.session_state.end_date = max_date
if "vis_range" not in st.session_state:
    st.session_state.vis_range = (min_vis, max_vis)

# Botón de Restablecimiento
if st.sidebar.button("Restablecer Filtros", use_container_width=True):
    st.session_state.start_date = min_date
    st.session_state.end_date = max_date
    st.session_state.vis_range = (min_vis, max_vis)
    st.rerun()

# Control de Rango de Fechas
date_input_range = st.sidebar.date_input(
    "Rango de Fechas",
    value=(st.session_state.start_date, st.session_state.end_date),
    min_value=min_date,
    max_value=max_date,
    help="Seleccione el rango temporal para el análisis."
)

# Control de Umbral de Visitantes
vis_range = st.sidebar.slider(
    "Umbral de Visitantes (Rango)",
    min_value=min_vis,
    max_value=max_vis,
    value=st.session_state.vis_range,
    help="Filtra los días que registran visitas dentro de este intervalo."
)

# Actualizar el estado con los valores seleccionados para mantener persistencia correcta
if isinstance(date_input_range, tuple) and len(date_input_range) == 2:
    st.session_state.start_date, st.session_state.end_date = date_input_range
elif isinstance(date_input_range, tuple) and len(date_input_range) == 1:
    st.session_state.start_date = date_input_range[0]
    st.session_state.end_date = date_input_range[0]

st.session_state.vis_range = vis_range

# 4. PROCESAMIENTO Y FILTRADO DE DATOS
df_filtered = df_raw.copy()
df_filtered["Fecha_date"] = df_filtered["Fecha"].dt.date

# Aplicar filtros
df_filtered = df_filtered[
    (df_filtered["Fecha_date"] >= st.session_state.start_date) &
    (df_filtered["Fecha_date"] <= st.session_state.end_date) &
    (df_filtered["Visitantes"] >= vis_range[0]) &
    (df_filtered["Visitantes"] <= vis_range[1])
]

# 5. DISEÑO DE LA INTERFAZ PRINCIPAL
st.title("📊 Panel de Control de Tráfico de Visitantes")
st.markdown(
    """
    Bienvenido al panel interactivo de análisis temporal de tráfico. 
    Utilice este espacio para identificar picos de tráfico, calcular promedios y observar la tendencia 
    del flujo de personas que interactúan con el servicio a lo largo de la dimensión temporal.
    """
)
st.markdown("---")

# Renderizado Condicional en caso de datos vacíos (Requisito UX)
if df_filtered.empty:
    st.warning("⚠️ No se encontraron registros para la combinación de filtros seleccionados. Intente ampliar el rango de fechas o relajar el umbral de visitantes en la barra lateral.")
else:
    # 6. SECCIÓN DE MÉTRICAS CLAVE (KPIs)
    # Cálculos Dinámicos
    total_visitors = int(df_filtered["Visitantes"].sum())
    avg_visitors = float(df_filtered["Visitantes"].mean())
    
    # Promedio histórico del dataset completo
    hist_mean = float(df_raw["Visitantes"].mean())
    
    # Diferencia porcentual respecto al histórico (Delta)
    if hist_mean > 0:
        pct_diff = ((avg_visitors - hist_mean) / hist_mean) * 100
        delta_str = f"{pct_diff:+.1f}% vs. Promedio Histórico"
    else:
        delta_str = "N/A"

    # Pico máximo y su fecha correspondiente
    max_idx = df_filtered["Visitantes"].idxmax()
    peak_val = int(df_filtered.loc[max_idx, "Visitantes"])
    peak_date = df_filtered.loc[max_idx, "Fecha"].strftime("%Y-%m-%d")

    # Mostrar Métricas en Columnas
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Total de Visitantes",
            value=f"{total_visitors:,}"
        )
    
    with col2:
        st.metric(
            label="Promedio Diario de Visitantes",
            value=f"{avg_visitors:.1f}",
            delta=delta_str
        )
        
    with col3:
        st.metric(
            label="Pico Máximo de Visitantes",
            value=f"{peak_val:,}"
        )
        st.caption(f"📅 Registrado el: **{peak_date}**")

    st.markdown("---")

    # 7. VISUALIZACIONES
    tab1, tab2 = st.tabs(["📈 Tendencia Temporal", "📊 Distribución por Volumen"])

    with tab1:
        st.subheader("Evolución Temporal de Visitas")
        # Gráfico de Línea Temporal (Tendencia Principal)
        fig_line = px.line(
            df_filtered,
            x="Fecha",
            y="Visitantes",
            labels={"Fecha": "Dimensión Temporal (Fecha)", "Visitantes": "Cantidad de Visitantes"},
            markers=True,
            template="plotly_white"
        )
        fig_line.update_traces(line_color="#1f77b4", marker=dict(size=6, hovertimestamp="all"))
        fig_line.update_layout(
            hovermode="x unified",
            xaxis_title="Fecha",
            yaxis_title="Visitantes",
            margin=dict(l=40, r=40, t=20, b=40)
        )
        st.plotly_chart(fig_line, use_container_width=True)

    with tab2:
        st.subheader("Distribución Diaria de Visitas")
        # Gráfico de Barras con Gradiente de Intensidad
        fig_bar = px.bar(
            df_filtered,
            x="Fecha",
            y="Visitantes",
            color="Visitantes",
            color_continuous_scale="Blues",
            labels={"Fecha": "Fecha", "Visitantes": "Cantidad de Visitantes"},
            template="plotly_white"
        )
        fig_bar.update_layout(
            coloraxis_showscale=True,
            xaxis_title="Fecha",
            yaxis_title="Visitantes",
            margin=dict(l=40, r=40, t=20, b=40)
        )
        st.plotly_chart(fig_bar, use_container_width=True)

st.caption("DEPLOY_ID: DEPLOY_1787289701")
