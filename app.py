import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de la página
st.set_page_config(page_title="Dashboard de Reunión Interdisciplinaria", layout="wide")

# Cargar datos
@st.cache_data
def load_data():
    data = {
        'ID': [1, 2, 3, 4, 5],
        'Fecha': ['2026-07-07', '2026-07-07', '2026-07-07', '2026-07-07', '2026-07-07'],
        'Concepto': ['OC cimentaciones', 'OC estructura', 'Entrega diseño de estructura', 'OC de anclas y placas', 'Memoria calculo estructural'],
        'Departamento': ['Compras', 'Compras', 'Diseño', 'Compras', 'Diseño'],
        'Responsable': ['N/A', 'Judith Echeverria', 'Carlos Mendez', 'Judith Echeverria', 'N/A'],
        'Estatus': ['Cerrado', 'Critico', 'En proceso', 'En proceso', 'Cerrado']
    }
    return pd.DataFrame(data)

df = load_data()

st.title("📊 Dashboard: Reunión Interdisciplinaria HLT MEZANINE")

# Sidebar
st.sidebar.header("Filtros")
dept = st.sidebar.multiselect("Departamento", df['Departamento'].unique())
estatus = st.sidebar.multiselect("Estatus", df['Estatus'].unique())

filtered_df = df.copy()
if dept:
    filtered_df = filtered_df[filtered_df['Departamento'].isin(dept)]
if estatus:
    filtered_df = filtered_df[filtered_df['Estatus'].isin(estatus)]

# Métricas
col1, col2, col3 = st.columns(3)
col1.metric("Total Tareas", len(filtered_df))
col2.metric("Tareas Criticas", len(filtered_df[filtered_df['Estatus'] == 'Critico']))
col3.metric("Tareas Cerradas", len(filtered_df[filtered_df['Estatus'] == 'Cerrado']))

# Gráficos
st.subheader("Distribución por Estatus")
fig = px.pie(filtered_df, names='Estatus', title="Tareas por Estatus")
st.plotly_chart(fig, use_container_width=True)

st.subheader("Detalle de Tareas")
st.dataframe(filtered_df, use_container_width=True)
