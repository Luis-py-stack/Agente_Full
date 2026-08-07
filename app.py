import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de la página
st.set_page_config(page_title="Dashboard Reunión Interdisciplinaria", layout="wide")

# Carga de datos
@st.cache_data
def load_data():
    df = pd.read_excel("Reunion_interdisciplinaria-HLT_MEZANINE.xlsx")
    df['Fecha captura'] = pd.to_datetime(df['Fecha captura'])
    return df

df = load_data()

# Título y Sidebar
st.title("📊 Dashboard de Seguimiento - HLT MEZANINE")
st.sidebar.header("Filtros")

# Filtros
status_filter = st.sidebar.multiselect("Filtrar por Estatus:", options=df['Estatus'].unique(), default=df['Estatus'].unique())
depto_filter = st.sidebar.multiselect("Filtrar por Departamento:", options=df['Departamento'].unique(), default=df['Departamento'].unique())

filtered_df = df[(df['Estatus'].isin(status_filter)) & (df['Departamento'].isin(depto_filter))]

# Métricas Principales
col1, col2, col3 = st.columns(3)
col1.metric("Total Tareas", len(filtered_df))
col2.metric("Tareas Críticas", len(filtered_df[filtered_df['Estatus'] == 'Critico']))
col3.metric("Tareas Cerradas", len(filtered_df[filtered_df['Estatus'] == 'Cerrado']))

# Gráfica
st.subheader("Distribución de Estatus")
fig = px.pie(filtered_df, names='Estatus', title='Estatus de los Conceptos')
st.plotly_chart(fig, use_container_width=True)

# Tabla de datos
st.subheader("Detalle de Tareas")
st.dataframe(filtered_df)

# Próximos pasos
st.subheader("Siguientes Pasos")
for _, row in filtered_df.iterrows():
    st.markdown(f"**{row['Concepto']}**: {row['Siguiente paso']}")