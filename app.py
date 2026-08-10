import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Cargar los datos de forma robusta
file_path = 'data/Reunion_interdisciplinaria-HLT_MEZANINE.xlsx'

if not os.path.exists(file_path):
    st.error(f"El archivo no se encontró en la ruta esperada: {file_path}")
    st.info("Por favor, asegúrate de que el archivo esté en la carpeta 'data' de tu repositorio.")
    st.stop()

df = pd.read_excel(file_path)

# Título
st.title("Dashboard de Seguimiento - HLT MEZANINE")

# Filtros
status_filter = st.sidebar.multiselect("Filtrar por Estatus", options=df['Estatus'].unique(), default=df['Estatus'].unique())
dept_filter = st.sidebar.multiselect("Filtrar por Departamento", options=df['Departamento'].unique(), default=df['Departamento'].unique())

filtered_df = df[(df['Estatus'].isin(status_filter)) & (df['Departamento'].isin(dept_filter))]

# Métricas
col1, col2, col3 = st.columns(3)
col1.metric("Total", len(filtered_df))
col2.metric("Críticos", len(filtered_df[filtered_df['Estatus'] == 'Critico']))
col3.metric("Cerrados", len(filtered_df[filtered_df['Estatus'] == 'Cerrado']))

# Gráfico
fig = px.bar(filtered_df, x='Estatus', title="Actividades por Estatus", color='Estatus')
st.plotly_chart(fig)

# Tabla
st.subheader("Detalle de Actividades")
st.dataframe(filtered_df)
