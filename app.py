import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- Configuración de página ---
st.set_page_config(page_title="Control de Gestión", layout="wide")

# --- Datos Simulados ---
@st.cache_data
def get_data():
    data = [
        {"ID": 1, "Fecha_captura": "2026-07-07", "Concepto": "OC cimentaciones", "Departamento": "Compras", "Contratista": None, "Responsable": None, "Estatus": "Cerrado", "Siguiente_paso": "ya se tiene cotizacion con Rangel, se comparte el dia de hoy para revision"},
        {"ID": 2, "Fecha_captura": "2026-07-07", "Concepto": "OC estructura", "Departamento": "Compras", "Contratista": None, "Responsable": "Judith Echeverria", "Estatus": "Critico", "Siguiente_paso": "Se comparte OC el dia de hoy, anticipo se paga en 15 dias, en confirmacion de reunion el dia de hoy (TECOIMSA)"},
        {"ID": 3, "Fecha_captura": "2026-07-07", "Concepto": "Entrega diseño de estructura", "Departamento": "Diseño", "Contratista": None, "Responsable": "Carlos Mendez", "Estatus": "En proceso", "Siguiente_paso": "En proceso de revision y vobo de NIDEC"}
    ]
    df = pd.DataFrame(data)
    df['Fecha_captura'] = pd.to_datetime(df['Fecha_captura'])
    # Manejo de nulos
    df['Responsable'] = df['Responsable'].fillna('Sin Asignar')
    df['Contratista'] = df['Contratista'].fillna('Sin Asignar')
    return df

df_full = get_data()

# --- Sidebar (Filtros) ---
st.sidebar.header("Filtros de Control")
fecha_range = st.sidebar.date_input("Rango de Fechas", [df_full['Fecha_captura'].min(), df_full['Fecha_captura'].max()])
status_filter = st.sidebar.multiselect("Filtro de Estatus", df_full['Estatus'].unique(), default=df_full['Estatus'].unique())
dept_filter = st.sidebar.multiselect("Departamento", df_full['Departamento'].unique(), default=df_full['Departamento'].unique())
resp_filter = st.sidebar.multiselect("Responsable", df_full['Responsable'].unique(), default=df_full['Responsable'].unique())
busqueda = st.sidebar.text_input("Buscar en Concepto")

# --- Aplicación de Filtros ---
df = df_full[
    (df_full['Estatus'].isin(status_filter)) &
    (df_full['Departamento'].isin(dept_filter)) &
    (df_full['Responsable'].isin(resp_filter)) &
    (df_full['Concepto'].str.contains(busqueda, case=False, na=True))
]

# --- Métricas ---
col1, col2, col3, col4 = st.columns(4)
total = len(df)
criticos = len(df[df['Estatus'] == 'Critico'])
efectividad = (len(df[df['Estatus'] == 'Cerrado']) / total * 100) if total > 0 else 0
pendientes = len(df[df['Responsable'] == 'Sin Asignar'])

col1.metric("Total Registros", total)
col2.metric("Ítems Críticos", criticos)
col3.metric("Efectividad (Cierre)", f"{efectividad:.1f}%")
col4.metric("Carga Pendiente", pendientes)

st.markdown("---")

# --- Gráficos ---
c1, c2 = st.columns(2)

with c1:
    fig_bar = px.bar(df.groupby('Departamento').size().reset_index(name='Cuenta'), 
                     x='Cuenta', y='Departamento', orientation='h', title="Distribución por Departamento")
    st.plotly_chart(fig_bar, use_container_width=True)

with c2:
    fig_pie = px.pie(df, names='Estatus', title="Composición por Estatus", color='Estatus', 
                     color_discrete_map={'Critico':'red', 'En proceso':'orange', 'Cerrado':'green'})
    st.plotly_chart(fig_pie, use_container_width=True)

# --- Análisis de Responsables ---
st.subheader("Carga de Trabajo por Responsable")
df_resp = df.groupby(['Responsable', 'Estatus']).size().reset_index(name='Cantidad')
fig_resp = px.bar(df_resp, x='Responsable', y='Cantidad', color='Estatus', barmode='group')
st.plotly_chart(fig_resp, use_container_width=True)

# --- Tabla Detallada con Estilo ---
def color_status(val):
    if val == 'Critico': return 'background-color: #ffcccc'
    if val == 'Cerrado': return 'background-color: #ccffcc'
    return ''

st.subheader("Detalle de Proyectos")
st.dataframe(
    df.style.map(color_status, subset=['Estatus']),
    column_config={"Siguiente_paso": st.column_config.TextColumn("Siguiente paso", width="large")},
    use_container_width=True
)
