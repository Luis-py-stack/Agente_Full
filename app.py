import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import datetime

# REGLA CRÍTICA: set_page_config debe ser el PRIMER comando de Streamlit.
st.set_page_config(
    page_title="Dashboard de Análisis de Tráfico de Visitantes",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CARGA Y PROCESAMIENTO DE DATOS ---
@st.cache_data
def load_data():
    """
    Carga de datos de tráfico. Intenta leer 'data.json' o 'data.csv'.
    Genera datos realistas basados en el esquema de la especificación si no se encuentran.
    """
    try:
        import os
        import json
        if os.path.exists("data.json"):
            with open("data.json", "r") as f:
                data = json.load(f)
            df = pd.DataFrame(data)
        elif os.path.exists("data.csv"):
            df = pd.read_csv("data.csv")
        else:
            raise FileNotFoundError
    except Exception:
        # Datos 'dummy' realistas basados en el esquema
        np.random.seed(42)
        base_date = pd.to_datetime("2026-01-01")
        dates = [base_date + pd.Timedelta(days=i) for i in range(60)]
        # Generar un flujo con estacionalidad semanal y ruido aleatorio
        visitantes = []
        for i, d in enumerate(dates):
            day_of_week = d.dayofweek
            is_weekend = 1 if day_of_week >= 5 else 0
            base_traffic = 30 + (is_weekend * 15) + int(10 * np.sin(i / 3))
            noise = np.random.randint(-8, 8)
            visitantes.append(max(5, base_traffic + noise))
            
        df = pd.DataFrame({
            "Fecha": [d.strftime("%Y-%m-%d") for d in dates],
            "Visitantes": visitantes
        })
    
    # Procesamiento robusto
    df["Fecha"] = pd.to_datetime(df["Fecha"])
    df["Visitantes"] = df["Visitantes"].astype(int)
    df = df.sort_values("Fecha").reset_index(drop=True)
    return df

# Cargar el set inicial de datos
df_base = load_data()

# --- ESTADOS POR DEFECTO PARA LOS FILTROS ---
min_date_val = df_base["Fecha"].min().to_pydatetime().date()
max_date_val = df_base["Fecha"].max().to_pydatetime().date()
min_vis_val = int(df_base["Visitantes"].min())
max_vis_val = int(df_base["Visitantes"].max())

if "filter_date" not in st.session_state:
    st.session_state.filter_date = (min_date_val, max_date_val)
if "filter_visitors" not in st.session_state:
    st.session_state.filter_visitors = (min_vis_val, max_vis_val)

# Función callback para restablecer filtros
def reset_filters():
    st.session_state.filter_date = (min_date_val, max_date_val)
    st.session_state.filter_visitors = (min_vis_val, max_vis_val)

# --- FILTROS (BARRA LATERAL) ---
st.sidebar.title("Configuración de Filtros")
st.sidebar.markdown("---")

# Filtro de Rango de Fechas
date_range = st.sidebar.date_input(
    "Selecciona Rango de Fechas:",
    value=st.session_state.filter_date,
    min_value=min_date_val,
    max_value=max_date_val,
    key="filter_date"
)

# Filtro de Umbral de Visitantes
visitor_range = st.sidebar.slider(
    "Umbral de Visitantes (Mín - Máx):",
    min_value=min_vis_val,
    max_value=max_vis_val,
    value=st.session_state.filter_visitors,
    key="filter_visitors"
)

st.sidebar.markdown("---")
# Botón de restablecer
st.sidebar.button("Restablecer Filtros", on_click=reset_filters, use_container_width=True)

# --- APLICAR FILTROS EN MEMORIA ---
filtered_df = df_base.copy()

# Filtrar fechas de forma segura dependiente del input
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    filtered_df = filtered_df[(filtered_df["Fecha"] >= start_date) & (filtered_df["Fecha"] <= end_date)]
elif isinstance(date_range, tuple) and len(date_range) == 1:
    start_date = pd.to_datetime(date_range[0])
    filtered_df = filtered_df[filtered_df["Fecha"] >= start_date]

# Filtrar por umbral de visitantes
filtered_df = filtered_df[
    (filtered_df["Visitantes"] >= visitor_range[0]) & 
    (filtered_df["Visitantes"] <= visitor_range[1])
]

# --- VISTA PRINCIPAL ---
st.title("📊 Dashboard de Análisis de Tráfico de Visitantes")
st.markdown("Visualización interactiva y análisis detallado de la evolución temporal del flujo de visitantes.")
st.markdown("---")

# --- MÉTRICAS CLAVE (KPIs) ---
if not filtered_df.empty:
    total_visitors = filtered_df["Visitantes"].sum()
    avg_visitors = filtered_df["Visitantes"].mean()
    
    # Obtener pico de tráfico de manera segura
    peak_idx = filtered_df["Visitantes"].idxmax()
    peak_row = filtered_df.loc[peak_idx]
    peak_val = peak_row["Visitantes"]
    peak_date = peak_row["Fecha"].strftime("%Y-%m-%d")
    
    # Calcular variación de tendencia comparado al período anterior de igual duración
    trend_val = None
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_dt, end_dt = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
        duration = end_dt - start_dt + pd.Timedelta(days=1)
        prev_start = start_dt - duration
        prev_end = start_dt - pd.Timedelta(days=1)
        
        prev_df = df_base[
            (df_base["Fecha"] >= prev_start) & 
            (df_base["Fecha"] <= prev_end) &
            (df_base["Visitantes"] >= visitor_range[0]) &
            (df_base["Visitantes"] <= visitor_range[1])
        ]
        
        if not prev_df.empty:
            prev_total = prev_df["Visitantes"].sum()
            if prev_total > 0:
                trend_val = ((total_visitors - prev_total) / prev_total) * 100
                
    # Mostrar KPIs en columnas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total de Visitantes",
            value=f"{total_visitors:,}"
        )
    with col2:
        st.metric(
            label="Promedio Diario",
            value=f"{avg_visitors:.1f}"
        )
    with col3:
        st.metric(
            label="Pico de Tráfico",
            value=f"{peak_val:,}",
            delta=f"Fecha: {peak_date}",
            delta_color="off"
        )
    with col4:
        if trend_val is not None:
            st.metric(
                label="Variación de Tendencia",
                value=f"{trend_val:+.1f}%",
                delta="vs. período anterior de igual duración"
            )
        else:
            st.metric(
                label="Variación de Tendencia",
                value="N/A",
                delta="Falta histórico para comparar",
                delta_color="off"
            )
else:
    st.warning("No hay registros que coincidan con los filtros seleccionados actualmente.")

st.markdown("---")

# --- VISUALIZACIONES ---
if not filtered_df.empty:
    # 1. Gráfico de Tendencia Temporal (Principal)
    st.subheader("📈 Evolución Temporal del Tráfico")
    fig_line = px.line(
        filtered_df,
        x="Fecha",
        y="Visitantes",
        labels={"Fecha": "Fecha de Registro", "Visitantes": "Cantidad de Visitantes"},
        title="Tendencia Diaria de Visitantes"
    )
    fig_line.update_traces(
        line_color="#0068C9",
        hoverinfo="all",
        hovertemplate="<b>Fecha:</b> %{x|%Y-%m-%d}<br><b>Visitantes:</b> %{y}<extra></extra>"
    )
    fig_line.update_layout(
        hovermode="x unified",
        margin=dict(l=20, r=20, t=50, b=20),
        height=400
    )
    st.plotly_chart(fig_line, use_container_width=True)

    # 2. Gráfico de Distribución o Frecuencia
    st.subheader("📊 Distribución Diaria Detallada")
    fig_bar = px.bar(
        filtered_df,
        x="Fecha",
        y="Visitantes",
        labels={"Fecha": "Fecha", "Visitantes": "Cantidad de Visitantes"},
        title="Comparación Diaria de Visitantes"
    )
    fig_bar.update_traces(
        marker_color="#2ca02c",
        hovertemplate="<b>Fecha:</b> %{x|%Y-%m-%d}<br><b>Visitantes:</b> %{y}<extra></extra>"
    )
    fig_bar.update_layout(
        margin=dict(l=20, r=20, t=50, b=20),
        height=350
    )
    st.plotly_chart(fig_bar, use_container_width=True)
else:
    st.info("Ajuste los filtros para ver las visualizaciones.")

st.markdown("---")

# --- TABLA DE DATOS DETALLADA ---
with st.expander("🔍 Ver datos origen", expanded=False):
    if not filtered_df.empty:
        # Formatear visualización de fecha para que sea legible en la tabla
        display_df = filtered_df.copy()
        display_df["Fecha"] = display_df["Fecha"].dt.strftime("%Y-%m-%d")
        st.dataframe(
            display_df.sort_values(by="Fecha", ascending=False),
            column_config={
                "Fecha": "Fecha de Registro",
                "Visitantes": "Número de Visitantes"
            },
            use_container_width=True,
            hide_index=True
        )
    else:
        st.write("No hay registros para mostrar.")

st.caption("DEPLOY_ID: DEPLOY_1787290326")
