import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de página
st.set_page_config(page_title="Command Center Proyectos", layout="wide")

# 1. Carga de Datos Simulados
def get_data():
    data = [
        {"ID": 1, "Fecha_captura": "2026-07-07", "Concepto": "OC cimentaciones", "Departamento": "Compras", "Contratista": None, "Responsable": None, "Estatus": "Cerrado", "Siguiente_paso": "ya se tiene cotizacion con Rangel, se comparte el dia de hoy para revision"},
        {"ID": 2, "Fecha_captura": "2026-07-07", "Concepto": "OC estructura", "Departamento": "Compras", "Contratista": None, "Responsable": "Judith Echeverria", "Estatus": "Critico", "Siguiente_paso": "Se comparte OC el dia de hoy, anticipo se paga en 15 dias, en confirmacion de reunion el dia de hoy (TECOIMSA)"},
        {"ID": 3, "Fecha_captura": "2026-07-08", "Concepto": "Mantenimiento HVAC", "Departamento": "Operaciones", "Contratista": "ClimaTech", "Responsable": "Carlos Ruiz", "Estatus": "En Proceso", "Siguiente_paso": "Esperando refacción"},
    ]
    df = pd.DataFrame(data)
    df['Fecha_captura'] = pd.to_datetime(df['Fecha_captura'])
    df['Responsable'] = df['Responsable'].fillna("Sin Asignar")
    return df

df = get_data()

# 2. Barra Lateral (Filtros)
st.sidebar.header("Filtros de Control")
start_date, end_date = st.sidebar.date_input("Rango de fechas", [df['Fecha_captura'].min(), df['Fecha_captura'].max()])
depto_filter = st.sidebar.multiselect("Departamento", df['Departamento'].unique())
status_filter = st.sidebar.multiselect("Estatus", df['Estatus'].unique())
resp_filter = st.sidebar.multiselect("Responsable", df['Responsable'].unique())
search_term = st.sidebar.text_input("Buscar en Concepto/Pasos")

# Filtrado de datos
mask = (df['Fecha_captura'].dt.date >= start_date) & (df['Fecha_captura'].dt.date <= end_date)
if depto_filter: mask &= df['Departamento'].isin(depto_filter)
if status_filter: mask &= df['Estatus'].isin(status_filter)
if resp_filter: mask &= df['Responsable'].isin(resp_filter)
if search_term: mask &= (df['Concepto'].str.contains(search_term, case=False) | df['Siguiente_paso'].str.contains(search_term, case=False))

df_filtered = df[mask]

# 3. Métricas
st.title("Command Center: Seguimiento Estratégico de Proyectos")

if df_filtered.empty:
    st.info("No se encontraron proyectos con los criterios seleccionados.")
else:
    col1, col2, col3, col4 = st.columns(4)
    total_prog = len(df_filtered[df_filtered['Estatus'] != "Cerrado"])
    criticos = len(df_filtered[df_filtered['Estatus'] == "Critico"])
    sin_asignar = len(df_filtered[df_filtered['Responsable'] == "Sin Asignar"])
    cierre = (len(df_filtered[df_filtered['Estatus'] == "Cerrado"]) / len(df_filtered)) * 100

    col1.metric("Proyectos en curso", total_prog)
    col2.metric("Estado Crítico", criticos, delta_color="inverse")
    col3.metric("Pendientes de Asignar", sin_asignar)
    col4.metric("Eficiencia de Cierre", f"{cierre:.1f}%")

    # 4. Visualización
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("Carga por Departamento")
        fig_bar = px.bar(df_filtered, x="Departamento", color="Estatus", barmode="stack")
        st.plotly_chart(fig_bar, use_container_width=True)

    with c2:
        st.subheader("Tendencia de Captura")
        df_trend = df_filtered.resample('W', on='Fecha_captura').size().reset_index(name='Cuenta')
        fig_line = px.line(df_trend, x='Fecha_captura', y='Cuenta')
        st.plotly_chart(fig_line, use_container_width=True)

    # 5. Bitácora Interactiva
    st.subheader("Bitácora Detallada")
    
    def color_status(val):
        color = 'red' if val == 'Critico' else ('green' if val == 'Cerrado' else 'transparent')
        return f'background-color: {color}; color: white'

    st.dataframe(
        df_filtered[['ID', 'Concepto', 'Responsable', 'Estatus', 'Siguiente_paso']],
        use_container_width=True,
        hide_index=True
    )

    # Expander de detalle
    with st.expander("Ver detalles del siguiente paso (Seleccionar ID)"):
        selected_id = st.selectbox("Seleccionar ID de proyecto", df_filtered['ID'].unique())
        detail = df_filtered[df_filtered['ID'] == selected_id].iloc[0]
        st.write(f"**Concepto:** {detail['Concepto']}")
        st.write(f"**Siguiente paso:** {detail['Siguiente_paso']}")