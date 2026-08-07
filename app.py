import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de la página
st.set_page_config(page_title="Dashboard de Reunión Interdisciplinaria", layout="wide")

# Carga de datos (simulando la estructura del archivo original)
@st.cache_data
def load_data():
    data = {
        'ID': [1, 2, 3, 4, 5],
        'Fecha captura': ['2026-07-07', '2026-07-07', '2026-07-07', '2026-07-07', '2026-07-07'],
        'Concepto': ['OC cimentaciones', 'OC estructura', 'Entrega diseño de estructura', 'OC de anclas y placas', 'Memoria calculo estructural'],
        'Departamento': ['Compras', 'Compras', 'Diseño', 'Compras', 'Diseño'],
        'Estatus': ['Cerrado', 'Critico', 'En proceso', 'En proceso', 'Cerrado'],
        'Siguiente paso': ['Revision Rangel', 'Pago anticipo', 'Revision NIDEC', 'Cotizacion materiales', 'Espera entrega']
    }
    return pd.DataFrame(data)

df = load_data()

# Título y Sidebar
st.title("📊 Dashboard de Seguimiento de Reunión Interdisciplinaria")
st.sidebar.header("Filtros")

# Filtros
depto_filter = st.sidebar.multiselect("Filtrar por Departamento", options=df['Departamento'].unique(), default=df['Departamento'].unique())
status_filter = st.sidebar.multiselect("Filtrar por Estatus", options=df['Estatus'].unique(), default=df['Estatus'].unique())

# Aplicar filtros
filtered_df = df[(df['Departamento'].isin(depto_filter)) & (df['Estatus'].isin(status_filter))]

# Métricas
col1, col2, col3 = st.columns(3)
col1.metric("Total de Pendientes", len(filtered_df))
col2.metric("Completados", len(filtered_df[filtered_df['Estatus'] == 'Cerrado']))
col3.metric("En Riesgo/Criticos", len(filtered_df[filtered_df['Estatus'] == 'Critico']))

# Gráfica
st.subheader("Distribución por Estatus")
fig = px.pie(filtered_df, names='Estatus', title="Estatus de las Actividades")
st.plotly_chart(fig, use_container_width=True)

# Tabla de detalles
st.subheader("Detalle de Actividades")
st.dataframe(filtered_df)
