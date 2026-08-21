import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, date

# ----------------------------------------------------
# 1. CONFIGURACIÓN DE LA PÁGINA (Debe ser el primer comando)
# ----------------------------------------------------
st.set_page_config(
    page_title="Panel de Análisis de Tráfico de Visitantes",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------------------------------------
# 2. CARGA Y PREPROCESAMIENTO DE DATOS (Con Caché)
# ----------------------------------------------------
@st.cache_data
def cargar_datos():
    """
    Intenta cargar datos desde un archivo local. Si falla o no existe,
    genera un dataset realista basado en el esquema provisto.
    """
    try:
        # Intentar cargar desde un archivo JSON local si existe
        df = pd.read_json("data.json")
        # Asegurar tipos de columnas según esquema
        df["Fecha"] = pd.to_datetime(df["Fecha"]).dt.date
        df["Visitantes"] = df["Visitantes"].astype(int)
    except Exception:
        # Generación de Dummy Data realista en caso de fallo o inexistencia
        np.random.seed(42)
        rango_fechas = pd.date_range(start="2026-01-01", end="2026-03-31", freq="D")
        
        # Simular una tendencia con cierta estacionalidad y ruido
        visitantes_base = np.random.randint(15, 45, size=len(rango_fechas))
        # Añadir efecto de fin de semana (más visitas los viernes/sábados)
        fin_de_semana_efecto = [10 if d.weekday() in [4, 5] else 0 for d in rango_fechas]
        visitantes_finales = visitantes_base + fin_de_semana_efecto
        
        df = pd.DataFrame({
            "Fecha": rango_fechas.date,
            "Visitantes": visitantes_finales.astype(int)
        })
    
    return df

# Cargar los datos
try:
    df_original = cargar_datos()
except Exception as e:
    st.error(f"Error crítico al inicializar la base de datos: {e}")
    df_original = pd.DataFrame(columns=["Fecha", "Visitantes"])

# ----------------------------------------------------
# 3. INTERFAZ DE USUARIO - BARRA LATERAL (FILTROS)
# ----------------------------------------------------
st.sidebar.header("Filtros de Datos")

if not df_original.empty:
    min_fecha_val = min(df_original["Fecha"])
    max_fecha_val = max(df_original["Fecha"])
    
    st.sidebar.subheader("Rango Temporal")
    rango_seleccionado = st.sidebar.date_input(
        "Seleccione el período de análisis:",
        value=(min_fecha_val, max_fecha_val),
        min_value=min_fecha_val,
        max_value=max_fecha_val
    )
    
    # Procesar la selección del rango de fechas de forma segura
    if isinstance(rango_seleccionado, tuple) and len(rango_seleccionado) == 2:
        fecha_inicio, fecha_fin = rango_seleccionado
    elif isinstance(rango_seleccionado, tuple) and len(rango_seleccionado) == 1:
        fecha_inicio = rango_seleccionado[0]
        fecha_fin = max_fecha_val
    else:
        fecha_inicio, fecha_fin = min_fecha_val, max_fecha_val
        
    # Filtrado reactivo del dataframe
    df_filtrado = df_original[
        (df_original["Fecha"] >= fecha_inicio) & 
        (df_original["Fecha"] <= fecha_fin)
    ].copy()
else:
    df_filtrado = df_original.copy()

# ----------------------------------------------------
# 4. CUERPO PRINCIPAL: TÍTULO Y PROPÓSITO
# ----------------------------------------------------
st.title("📈 Panel de Análisis de Tráfico de Visitantes")
st.markdown(
    """
    Este cuadro de mando interactivo permite monitorear, segmentar y analizar la evolución temporal 
    de la afluencia de usuarios en la plataforma. Utilice la barra lateral para ajustar el rango de fechas.
    """
)
st.markdown("---")

# ----------------------------------------------------
# 5. CÁLCULO Y RENDERIZADO DE MÉTRICAS CLAVE (KPIs)
# ----------------------------------------------------
if not df_filtrado.empty:
    # 1. Total de Visitantes
    total_visitantes = int(df_filtrado["Visitantes"].sum())
    
    # 2. Promedio Diario de Visitantes
    promedio_diario = int(round(df_filtrado["Visitantes"].mean()))
    
    # 3. Pico Máximo de Visitantes y su Fecha
    id_max = df_filtrado["Visitantes"].idxmax()
    pico_maximo = int(df_filtrado.loc[id_max, "Visitantes"])
    fecha_pico = df_filtrado.loc[id_max, "Fecha"].strftime("%d/%m/%Y")
    
    # Visualización en 3 columnas
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Total de Visitantes",
            value=f"{total_visitantes:,}".replace(",", ".")
        )
        
    with col2:
        st.metric(
            label="Promedio Diario de Visitantes",
            value=f"{promedio_diario:,}".replace(",", ".")
        )
        
    with col3:
        st.metric(
            label="Pico Máximo de Visitantes",
            value=f"{pico_maximo:,}".replace(",", "."),
            delta=f"Fecha: {fecha_pico}",
            delta_color="off"
        )
else:
    st.warning("No hay datos disponibles para el rango de fechas seleccionado.")

st.markdown("---")

# ----------------------------------------------------
# 6. VISUALIZACIONES
# ----------------------------------------------------
if not df_filtrado.empty:
    # Gráfico de Línea Temporal (Plotly Express para interactividad y tooltips)
    st.subheader("Evolución Temporal del Tráfico")
    
    # Asegurar orden cronológico para el gráfico
    df_grafico = df_filtrado.sort_values(by="Fecha")
    
    fig = px.area(
        df_grafico,
        x="Fecha",
        y="Visitantes",
        labels={"Fecha": "Fecha de Registro", "Visitantes": "Cantidad de Visitantes"},
        template="plotly_white",
        color_discrete_sequence=["#1f77b4"]
    )
    
    # Personalización avanzada del gráfico para UX premium
    fig.update_layout(
        hovermode="x unified",
        xaxis=dict(showgrid=True, gridcolor='LightGrey'),
        yaxis=dict(showgrid=True, gridcolor='LightGrey'),
        margin=dict(l=40, r=40, t=20, b=40)
    )
    
    fig.update_traces(
        hovertemplate="<b>Fecha:</b> %{x}<br><b>Visitantes:</b> %{y}<extra></extra>",
        line=dict(width=2),
        fillcolor="rgba(31, 119, 180, 0.2)"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Tabla de Datos Detallada (Desplegable)
    with st.expander("Ver Datos Históricos Detallados"):
        st.markdown("A continuación se detallan los registros correspondientes al período seleccionado, ordenados de forma cronológica descendente.")
        
        # Ordenación cronológica descendente según instrucciones de UX
        df_tabla = df_filtrado.sort_values(by="Fecha", ascending=False)
        
        # Formatear la visualización de la tabla
        st.dataframe(
            df_tabla,
            column_config={
                "Fecha": st.column_config.DateColumn("Fecha", format="DD/MM/YYYY"),
                "Visitantes": st.column_config.NumberColumn("Visitantes", format="%d")
            },
            hide_index=True,
            use_container_width=True
        )

st.caption("DEPLOY_ID: DEPLOY_1787288618")
