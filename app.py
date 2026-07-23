import streamlit as st
import pandas as pd
import numpy as np
import datetime

# Configuración de página
st.set_page_config(page_title="Dashboard de Visitantes", layout="wide")

# 1. Preparación de Data Simulada
def get_data():
    data = [
        {"Fecha": "2026-01-21", "Visitantes": 31}, {"Fecha": "2026-01-20", "Visitantes": 28},
        {"Fecha": "2026-01-19", "Visitantes": 26}, {"Fecha": "2026-01-18", "Visitantes": 22},
        {"Fecha": "2026-01-17", "Visitantes": 35}, {"Fecha": "2026-01-16", "Visitantes": 19},
        {"Fecha": "2026-01-15", "Visitantes": 25}, {"Fecha": "2026-01-14", "Visitantes": 30},
        {"Fecha": "2026-01-13", "Visitantes": 28}, {"Fecha": "2026-01-12", "Visitantes": 24},
        {"Fecha": "2026-01-11", "Visitantes": 21}, {"Fecha": "2026-01-10", "Visitantes": 18},
        {"Fecha": "2026-01-09", "Visitantes": 27}, {"Fecha": "2026-01-08", "Visitantes": 29},
        {"Fecha": "2026-01-07", "Visitantes": 32}, {"Fecha": "2026-01-06", "Visitantes": 26},
        {"Fecha": "2026-01-05", "Visitantes": 20}, {"Fecha": "2026-01-04", "Visitantes": 15},
        {"Fecha": "2026-01-03", "Visitantes": 19}, {"Fecha": "2026-01-02", "Visitantes": 24},
        {"Fecha": "2026-01-01", "Visitantes": 22}, {"Fecha": "2025-12-31", "Visitantes": 18},
        {"Fecha": "2025-12-30", "Visitantes": 25}, {"Fecha": "2025-12-29", "Visitantes": 27},
        {"Fecha": "2025-12-28", "Visitantes": 21}, {"Fecha": "2025-12-27", "Visitantes": 19},
        {"Fecha": "2025-12-26", "Visitantes": 23}, {"Fecha": "2025-12-25", "Visitantes": 12},
        {"Fecha": "2025-12-24", "Visitantes": 15}
    ]
    df = pd.DataFrame(data)
    df['Fecha'] = pd.to_datetime(df['Fecha'])
    return df.sort_values('Fecha')

df = get_data()

# 2. Sidebar
st.sidebar.header("Filtros de Análisis")
start_date = datetime.date(2025, 12, 24)
end_date = datetime.date(2026, 1, 21)

date_range = st.sidebar.date_input(
    "Rango de Fechas",
    value=(start_date, end_date),
    min_value=df['Fecha'].min().date(),
    max_value=df['Fecha'].max().date()
)

grouping = st.sidebar.selectbox("Granularidad", ["Diario", "Semanal", "Promedio Móvil de 7 días"])

# Filtrado
if isinstance(date_range, tuple) and len(date_range) == 2:
    mask = (df['Fecha'].dt.date >= date_range[0]) & (df['Fecha'].dt.date <= date_range[1])
    filtered_df = df.loc[mask]
else:
    filtered_df = df

st.sidebar.divider()
csv = filtered_df.to_csv(index=False).encode('utf-8')
st.sidebar.download_button("Exportar Datos (CSV)", csv, "datos_visitantes.csv", "text/csv")

# 3. Contenido Principal
st.title("Panel de Control: Análisis de Tráfico de Visitantes")

if filtered_df.empty:
    st.warning("No hay datos disponibles para el rango seleccionado.")
else:
    # Métricas
    col1, col2, col3 = st.columns(3)
    total_visitantes = filtered_df['Visitantes'].sum()
    promedio = filtered_df['Visitantes'].mean()
    pico = filtered_df['Visitantes'].max()
    
    col1.metric("Total de Visitantes", total_visitantes)
    col2.metric("Promedio Diario", f"{promedio:.1f}")
    col3.metric("Pico de Visitas", pico)
    
    st.divider()

    # Visualización
    tab1, tab2 = st.tabs(["Tendencia (Área)", "Distribución (Barras)"])
    
    with tab1:
        st.subheader("Tendencia Temporal")
        st.area_chart(filtered_df.set_index('Fecha')['Visitantes'], color="#2E86C1")
        
    with tab2:
        st.subheader("Distribución por Días")
        st.bar_chart(filtered_df.set_index('Fecha')['Visitantes'], color="#27AE60")

    # Tabla
    st.divider()
    st.subheader("Detalle de Registros")
    st.dataframe(filtered_df.sort_values('Fecha', ascending=False), use_container_width=True)