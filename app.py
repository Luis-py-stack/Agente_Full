import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de la página
st.set_page_config(page_title="Dashboard de Visitantes", layout="wide")

# Datos simulados (ya que el archivo local no es accesible directamente tras el deploy)
data = {
    'Fecha': ['2026-01-21', '2026-01-20', '2026-01-19', '2026-01-18', '2026-01-17', '2026-01-16', '2026-01-15', '2026-01-14', '2026-01-13', '2026-01-12', '2026-01-11', '2026-01-10', '2026-01-09', '2026-01-08', '2026-01-07', '2026-01-06', '2026-01-05', '2026-01-04', '2026-01-03', '2026-01-02', '2026-01-01', '2025-12-31', '2025-12-30', '2025-12-29', '2025-12-28', '2025-12-27', '2025-12-26', '2025-12-25', '2025-12-24'],
    'Visitantes': [31, 28, 26, 25, 27, 18, 22, 15, 15, 8, 9, 15, 16, 12, 16, 14, 24, 15, 8, 15, 14, 10, 35, 13, 13, 26, 26, 12, 14]
}

df = pd.DataFrame(data)
df['Fecha'] = pd.to_datetime(df['Fecha'])

# Sidebar
st.sidebar.header("Filtros")
rango_fechas = st.sidebar.date_input("Seleccionar rango de fechas", [df['Fecha'].min(), df['Fecha'].max()])

# Filtrado
mask = (df['Fecha'].dt.date >= rango_fechas[0]) & (df['Fecha'].dt.date <= rango_fechas[1])
df_filtrado = df.loc[mask]

# Dashboard
st.title("📊 Dashboard de Visitantes B2C")

col1, col2 = st.columns(2)
col1.metric("Total Visitantes", df_filtrado['Visitantes'].sum())
col2.metric("Promedio Diario", round(df_filtrado['Visitantes'].mean(), 2))

st.subheader("Tendencia de Visitantes")
fig = px.line(df_filtrado, x='Fecha', y='Visitantes', markers=True, title="Evolución temporal")
st.plotly_chart(fig, use_container_width=True)

st.subheader("Datos detallados")
st.dataframe(df_filtrado.sort_values(by='Fecha', ascending=False))