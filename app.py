import streamlit as st
import pandas as pd
import plotly.express as px

# Cargar datos
@st.cache_data
def load_data():
    # En un escenario real, cargaríamos el archivo procesado. 
    # Aquí usamos el esquema detectado.
    data = {
        'ID': [1, 2, 3, 4, 5],
        'Fecha captura': ['2026-07-07', '2026-07-07', '2026-07-07', '2026-07-07', '2026-07-07'],
        'Concepto': ['OC cimentaciones', 'OC estructura', 'Entrega diseño de estructura', 'OC de anclas y placas', 'Memoria calculo estructural (estructura metalica)'],
        'Departamento': ['Compras', 'Compras', 'Diseño', 'Compras', 'Diseño'],
        'Estatus': ['Cerrado', 'Critico', 'En proceso', 'En proceso', 'Cerrado']
    }
    return pd.DataFrame(data)

df = load_data()

st.set_page_config(page_title="Dashboard Reunión HLT", layout="wide")
st.title("📊 Dashboard de Seguimiento: HLT MEZANINE")

# Sidebar
st.sidebar.header("Filtros")
dept_filter = st.sidebar.multiselect("Departamento", df['Departamento'].unique())
status_filter = st.sidebar.multiselect("Estatus", df['Estatus'].unique())

# Aplicar filtros
filtered_df = df.copy()
if dept_filter:
    filtered_df = filtered_df[filtered_df['Departamento'].isin(dept_filter)]
if status_filter:
    filtered_df = filtered_df[filtered_df['Estatus'].isin(status_filter)]

# Métricas
col1, col2, col3 = st.columns(3)
col1.metric("Total Tareas", len(filtered_df))
col2.metric("En Proceso/Critico", len(filtered_df[filtered_df['Estatus'].isin(['En proceso', 'Critico'])]))
col3.metric("Cerradas", len(filtered_df[filtered_df['Estatus'] == 'Cerrado']))

# Gráficos
st.subheader("Tareas por Estatus")
fig = px.pie(filtered_df, names='Estatus', title="Distribución de tareas por estatus")
st.plotly_chart(fig, use_container_width=True)

st.subheader("Detalle de Tareas")
st.dataframe(filtered_df)
