import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Configuración de página
st.set_page_config(page_title="Panel de Control de Operaciones", layout="wide")

# 1. Preparación de Datos
def get_data():
    data = [
        {"ID": 1, "Fecha_captura": "2026-07-07", "Concepto": "OC cimentaciones", "Departamento": "Compras", "Contratista": None, "Responsable": None, "Estatus": "Cerrado", "Siguiente_paso": "ya se tiene cotizacion con Rangel, se comparte el dia de hoy para revision"},
        {"ID": 2, "Fecha_captura": "2026-07-07", "Concepto": "OC estructura", "Departamento": "Compras", "Contratista": None, "Responsable": "Judith Echeverria", "Estatus": "Critico", "Siguiente_paso": "Se comparte OC el dia de hoy, anticipo se paga en 15 dias, en confirmacion de reunion el dia de hoy (TECOIMSA)"},
        {"ID": 3, "Fecha_captura": "2026-07-08", "Concepto": "Diseño fachada", "Departamento": "Diseño", "Contratista": "Arq. Ruiz", "Responsable": None, "Estatus": "En Proceso", "Siguiente_paso": "Esperando validación de renders finales"},
        {"ID": 4, "Fecha_captura": "2026-07-09", "Concepto": "Compra acero", "Departamento": "Compras", "Contratista": "Aceros S.A.", "Responsable": "Judith Echeverria", "Estatus": "Critico", "Siguiente_paso": "Urgente: definir proveedor antes de cierre de mes"}
    ]
    df = pd.DataFrame(data)
    df['Fecha_captura'] = pd.to_datetime(df['Fecha_captura'])
    df['Responsable'] = df['Responsable'].fillna('Sin asignar')
    return df

df_base = get_data()

# 2. Barra Lateral (Filtros)
st.sidebar.header("Filtros de Segmentación")
date_range = st.sidebar.date_input("Rango de Fechas", [df_base['Fecha_captura'].min(), df_base['Fecha_captura'].max()])
depto_filter = st.sidebar.multiselect("Departamento", df_base['Departamento'].unique())
status_filter = st.sidebar.multiselect("Estatus", df_base['Estatus'].unique())
resp_filter = st.sidebar.multiselect("Responsable", df_base['Responsable'].unique())
search_text = st.sidebar.text_input("Buscador de Concepto")

# Aplicar Filtros
df_filtered = df_base.copy()
if len(date_range) == 2:
    df_filtered = df_filtered[(df_filtered['Fecha_captura'].dt.date >= date_range[0]) & (df_filtered['Fecha_captura'].dt.date <= date_range[1])]
if depto_filter: df_filtered = df_filtered[df_filtered['Departamento'].isin(depto_filter)]
if status_filter: df_filtered = df_filtered[df_filtered['Estatus'].isin(status_filter)]
if resp_filter: df_filtered = df_filtered[df_filtered['Responsable'].isin(resp_filter)]
if search_text: df_filtered = df_filtered[df_filtered['Concepto'].str.contains(search_text, case=False)]

# 3. Métricas
col1, col2, col3, col4 = st.columns(4)
total = len(df_filtered)
criticos = len(df_filtered[df_filtered['Estatus'] == 'Critico'])
sin_resp = len(df_filtered[df_filtered['Responsable'] == 'Sin asignar'])
efectividad = (len(df_filtered[df_filtered['Estatus'] == 'Cerrado']) / total * 100) if total > 0 else 0

col1.metric("Total de Procesos", total)
col2.metric("En estado Crítico", criticos)
col3.metric("Pendientes de Asignación", sin_resp)
col4.metric("Efectividad de Cierre", f"{efectividad:.1f}%")

# 4. Gráficos
st.divider()
row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    st.subheader("Distribución Operativa")
    fig1 = px.bar(df_filtered, x=df_filtered.index, y="Departamento", color="Estatus", orientation='h', barmode='group')
    st.plotly_chart(fig1, use_container_width=True)

with row1_col2:
    st.subheader("Tendencia de Capturas")
    trend = df_filtered.groupby(['Fecha_captura', 'Departamento']).size().reset_index(name='Cuenta')
    fig2 = px.line(trend, x='Fecha_captura', y='Cuenta', color='Departamento')
    st.plotly_chart(fig2, use_container_width=True)

# 5. Tabla Detalle
st.subheader("Detalle Accionable")
def highlight_row(row):
    return ['background-color: #ffcccc' if row['Estatus'] == 'Critico' else '' for _ in row]

st.dataframe(
    df_filtered.style.apply(highlight_row, axis=1),
    use_container_width=True,
    column_config={
        "Siguiente_paso": st.column_config.TextColumn("Siguiente Paso", width="large")
    }
)