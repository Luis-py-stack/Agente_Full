import streamlit as pd
import pandas as pd
import numpy as np
import plotly.express as px
import datetime

# Configuración de la página
pd.set_page_config(
    page_title="Dashboard de Análisis de Visitantes Diario",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CARGA Y PREPARACIÓN DE DATOS ---
@pd.cache_data
def load_data():
    """
    Carga los datos del archivo CSV local si existe, de lo contrario
    genera un dataset sintético realista basado en el esquema especificado.
    """
    try:
        # Intento de cargar archivo de datos de producción
        df = pd.read_csv('visitantes.csv')
        df['Fecha'] = pd.to_datetime(df['Fecha'])
    except Exception:
        # Generación de datos sintéticos (Dummy Data) realistas
        np.random.seed(42)
        base_date = datetime.date(2026, 1, 21)
        num_days = 120
        dates = [base_date - datetime.timedelta(days=x) for x in range(num_days)]
        dates.reverse()  # Orden cronológico
        
        # Generación de volumen de visitantes con tendencia y estacionalidad semanal
        visitors = []
        for i, date in enumerate(dates):
            weekday_factor = 1.5 if date.weekday() >= 5 else 1.0  # Más visitas fines de semana
            trend = i * 0.1  # Ligero crecimiento temporal
            noise = np.random.randint(-10, 10)
            val = max(5, int(25 + trend + (weekday_factor * 10) + noise))
            visitors.append(val)
            
        df = pd.DataFrame({
            'Fecha': pd.to_datetime(dates),
            'Visitantes': visitors
        })
    return df

df_raw = load_data()

# --- PANEL DE CONTROL LATERAL (SIDEBAR) ---
pd.sidebar.header("Panel de Control")
pd.sidebar.markdown("---")

# Rango de fechas dinámico basado en el dataset
min_date_val = df_raw['Fecha'].min().date()
max_date_val = df_raw['Fecha'].max().date()

pd.sidebar.subheader("Filtrar por Rango Temporal")
date_range = pd.sidebar.date_input(
    "Selecciona las fechas (Desde - Hasta):",
    value=(min_date_val, max_date_val),
    min_value=min_date_val,
    max_value=max_date_val
)

# Control de granularidad temporal
pd.sidebar.subheader("Granularidad de Visualización")
granularity = pd.sidebar.selectbox(
    "Agrupar datos por:",
    options=["Día", "Semana"],
    index=0,
    help="Permite suavizar las tendencias agrupando las visitas en periodos semanales."
)

# Validación de selección de rango completo de fechas
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date_val, max_date_val

# Filtrado de datos en memoria para optimización de rendimiento
df_filtered = df_raw[
    (df_raw['Fecha'].dt.date >= start_date) & 
    (df_raw['Fecha'].dt.date <= end_date)
].copy()

# --- TÍTULO Y PROPÓSITO ---
pd.title("📈 Dashboard de Análisis de Visitantes Diario")
pd.markdown(
    """
    Este dashboard interactivo proporciona una herramienta avanzada para monitorear, 
    analizar y comprender el comportamiento del flujo de usuarios a lo largo del tiempo. 
    Permite visualizar la evolución temporal de la variable **Visitantes** según el registro de **Fecha**, 
    facilitando la toma de decisiones estratégicas basadas en el histórico acumulado.
    """
)
pd.markdown("---")

# --- CÁLCULO DE MÉTRICAS CLAVE (KPIs) ---
if not df_filtered.empty:
    # 1. Total Visitantes y cálculo de Periodo Anterior
    total_visitantes = df_filtered['Visitantes'].sum()
    
    # Calcular duración del periodo seleccionado para el cálculo de delta
    duration = pd.to_datetime(end_date) - pd.to_datetime(start_date)
    prev_end_date = pd.to_datetime(start_date) - pd.Timedelta(days=1)
    prev_start_date = prev_end_date - duration
    
    df_prev = df_raw[
        (df_raw['Fecha'] >= prev_start_date) & 
        (df_raw['Fecha'] <= prev_end_date)
    ]
    total_visitantes_prev = df_prev['Visitantes'].sum()
    
    if total_visitantes_prev > 0:
        pct_change = ((total_visitantes - total_visitantes_prev) / total_visitantes_prev) * 100
        delta_total = f"{pct_change:+.1f}% vs anterior"
    else:
        delta_total = "Sin datos previos"

    # 2. Promedio Diario
    promedio_diario = df_filtered['Visitantes'].mean()

    # 3. Pico Máximo de Tráfico
    pico_idx = df_filtered['Visitantes'].idxmax()
    pico_maximo = df_filtered.loc[pico_idx, 'Visitantes']
    pico_fecha = df_filtered.loc[pico_idx, 'Fecha'].strftime('%Y-%m-%d')
    delta_pico = f"Registrado el {pico_fecha}"
else:
    total_visitantes = 0
    delta_total = "N/A"
    promedio_diario = 0
    pico_maximo = 0
    delta_pico = "N/A"

# Render de Métricas en Columnas
kpi_col1, kpi_col2, kpi_col3 = pd.columns(3)

with kpi_col1:
    pd.metric(
        label="Total de Visitantes",
        value=f"{total_visitantes:,}",
        delta=delta_total
    )

with kpi_col2:
    pd.metric(
        label="Promedio Diario de Visitantes",
        value=f"{promedio_diario:.1f}"
    )

with kpi_col3:
    pd.metric(
        label="Pico Máximo de Visitantes",
        value=f"{pico_maximo:,}",
        delta=delta_pico,
        delta_color="off"
    )

pd.markdown("---")

# --- PROCESAMIENTO SEGÚN GRANULARIDAD ---
if granularity == "Semana" and not df_filtered.empty:
    # Agrupación por semana (atribuyendo al lunes de cada semana)
    df_chart = df_filtered.resample('W-MON', on='Fecha').agg({
        'Visitantes': 'sum'
    }).reset_index()
    x_axis_title = "Semana (Inicio de Lunes)"
    hover_fmt = "%Y-%m-%d"
else:
    df_chart = df_filtered.copy()
    x_axis_title = "Fecha"
    hover_fmt = "%Y-%m-%d"

# --- VISUALIZACIÓN DE TENDENCIAS ---
pd.subheader("Evolución Temporal del Flujo de Visitantes")

if not df_chart.empty:
    # Generar gráfico interactivo con Plotly Express
    fig = px.line(
        df_chart,
        x='Fecha',
        y='Visitantes',
        markers=True,
        template="plotly_white",
        color_discrete_sequence=["#1f77b4"]
    )
    
    # Configuración de diseño UX/UI suave (spline) y tooltips customizados
    fig.update_traces(
        line_shape='spline', 
        line=dict(width=3),
        hovertemplate="<b>Fecha:</b> %{x|<br><b>Visitantes:</b> %{y}<extra></extra>"
    )
    
    fig.update_layout(
        hovermode="x unified",
        xaxis_title=x_axis_title,
        yaxis_title="Cantidad de Visitantes",
        margin=dict(l=40, r=40, t=20, b=40),
        height=450,
        xaxis=dict(showgrid=True, gridcolor='rgba(200, 200, 200, 0.2)'),
        yaxis=dict(showgrid=True, gridcolor='rgba(200, 200, 200, 0.2)')
    )
    
    pd.plotly_chart(fig, use_container_width=True)
else:
    pd.warning("No hay datos disponibles para el rango de fechas seleccionado.")

# --- TABLA DE DATOS HISTÓRICOS (EXPANDER) ---
with pd.expander("Ver Datos Históricos Detallados"):
    if not df_filtered.empty:
        # Formatear la fecha para una visualización más amigable
        df_display = df_filtered.copy()
        df_display['Fecha'] = df_display['Fecha'].dt.strftime('%Y-%m-%d')
        pd.dataframe(
            df_display.sort_values(by="Fecha", ascending=False),
            use_container_width=True,
            column_config={
                "Fecha": pd.column_config.DateColumn("Fecha de Registro"),
                "Visitantes": pd.column_config.NumberColumn("Total de Visitantes", format="%d")
            },
            hide_index=True
        )
    else:
        pd.info("No hay registros en el rango seleccionado.")