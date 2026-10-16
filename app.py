import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuración de página - DEBE ser la primera llamada de Streamlit
st.set_page_config(page_title="Reporte de Visitantes B2C", layout="wide")

# Registros completos extraídos del esquema JSON
RAW_RECORDS = [
    {"Fecha": "2026-01-21 00:00:00", "Visitantes": 31},
    {"Fecha": "2026-01-20 00:00:00", "Visitantes": 28},
    {"Fecha": "2026-01-19 00:00:00", "Visitantes": 26},
    {"Fecha": "2026-01-18 00:00:00", "Visitantes": 25},
    {"Fecha": "2026-01-17 00:00:00", "Visitantes": 27},
    {"Fecha": "2026-01-16 00:00:00", "Visitantes": 18},
    {"Fecha": "2026-01-15 00:00:00", "Visitantes": 22},
    {"Fecha": "2026-01-14 00:00:00", "Visitantes": 15},
    {"Fecha": "2026-01-13 00:00:00", "Visitantes": 15},
    {"Fecha": "2026-01-12 00:00:00", "Visitantes": 8},
    {"Fecha": "2026-01-11 00:00:00", "Visitantes": 9},
    {"Fecha": "2026-01-10 00:00:00", "Visitantes": 15},
    {"Fecha": "2026-01-09 00:00:00", "Visitantes": 16},
    {"Fecha": "2026-01-08 00:00:00", "Visitantes": 12},
    {"Fecha": "2026-01-07 00:00:00", "Visitantes": 16},
    {"Fecha": "2026-01-06 00:00:00", "Visitantes": 14},
    {"Fecha": "2026-01-05 00:00:00", "Visitantes": 24},
    {"Fecha": "2026-01-04 00:00:00", "Visitantes": 15},
    {"Fecha": "2026-01-03 00:00:00", "Visitantes": 8},
    {"Fecha": "2026-01-02 00:00:00", "Visitantes": 15},
    {"Fecha": "2026-01-01 00:00:00", "Visitantes": 14},
    {"Fecha": "2025-12-31 00:00:00", "Visitantes": 10},
    {"Fecha": "2025-12-30 00:00:00", "Visitantes": 35},
    {"Fecha": "2025-12-29 00:00:00", "Visitantes": 13},
    {"Fecha": "2025-12-28 00:00:00", "Visitantes": 13},
    {"Fecha": "2025-12-27 00:00:00", "Visitantes": 26},
    {"Fecha": "2025-12-26 00:00:00", "Visitantes": 26},
    {"Fecha": "2025-12-25 00:00:00", "Visitantes": 12},
    {"Fecha": "2025-12-24 00:00:00", "Visitantes": 14}
]

# Carga y pipeline de datos defensivo
def load_data(uploaded_file):
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
        except Exception as e:
            st.error(f"Error al leer el archivo subido: {e}")
            df = pd.DataFrame(RAW_RECORDS)
    else:
        df = pd.DataFrame(RAW_RECORDS)

    # Tipado defensivo y validación de columnas
    if 'Fecha' in df.columns:
        df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')
    else:
        st.error("Falta la columna 'Fecha' en los datos.")
        st.stop()

    if 'Visitantes' in df.columns:
        df['Visitantes'] = pd.to_numeric(df['Visitantes'], errors='coerce')
    else:
        st.error("Falta la columna 'Visitantes' en los datos.")
        st.stop()

    df = df.dropna(subset=['Fecha', 'Visitantes']).sort_values('Fecha').reset_index(drop=True)
    
    # Feature Engineering
    df['Fecha_Corta'] = df['Fecha'].dt.date
    dias_es = {
        "Monday": "Lunes",
        "Tuesday": "Martes",
        "Wednesday": "Miércoles",
        "Thursday": "Jueves",
        "Friday": "Viernes",
        "Saturday": "Sábado",
        "Sunday": "Domingo"
    }
    df['Día_Semana'] = df['Fecha'].dt.day_name().map(dias_es)
    
    return df

# Barra Lateral de Configuración y Filtros
st.sidebar.header("⚙️ Configuración y Filtros")

uploaded_file = st.sidebar.file_uploader(
    "Cargar datos opcionales (CSV / Excel)", 
    type=['csv', 'xlsx']
)

df_base = load_data(uploaded_file)

if df_base.empty:
    st.error("El conjunto de datos cargado no contiene registros válidos.")
    st.stop()

# Botón de Restablecimiento
if st.sidebar.button("🔄 Restablecer Filtros"):
    st.rerun()

# Rangos límites para los controles
min_date = df_base['Fecha_Corta'].min()
max_date = df_base['Fecha_Corta'].max()
min_vis = int(df_base['Visitantes'].min())
max_vis = int(df_base['Visitantes'].max())
dias_ordenados = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

# Controles de filtro
date_range = st.sidebar.date_input(
    "Rango de Fechas",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

vis_range = st.sidebar.slider(
    "Rango de Visitantes Diarios",
    min_value=min_vis,
    max_value=max_vis,
    value=(min_vis, max_vis)
)

selected_days = st.sidebar.multiselect(
    "Día de la Semana",
    options=dias_ordenados,
    default=dias_ordenados
)

# Aplicación de Filtros Reactivos
df_filtered = df_base.copy()

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_d, end_d = date_range
    df_filtered = df_filtered[(df_filtered['Fecha_Corta'] >= start_d) & (df_filtered['Fecha_Corta'] <= end_d)]
elif isinstance(date_range, tuple) and len(date_range) == 1:
    df_filtered = df_filtered[df_filtered['Fecha_Corta'] >= date_range[0]]

df_filtered = df_filtered[
    (df_filtered['Visitantes'] >= vis_range[0]) & 
    (df_filtered['Visitantes'] <= vis_range[1])
]

if selected_days:
    df_filtered = df_filtered[df_filtered['Día_Semana'].isin(selected_days)]
else:
    df_filtered = df_filtered.iloc[0:0]

# Validación defensiva de DataFrame vacío tras filtros
if df_filtered.empty:
    st.warning("⚠️ No hay datos disponibles para los filtros seleccionados. Por favor, ajusta los parámetros en la barra lateral.")
    st.stop()

# --- HEADER Y METADATOS PRINCIPALES ---
st.title("Reporte de Visitantes B2C")
st.subheader("ST_B2C - Tráfico de visitantes")

st.info(
    "**Periodo de reporte:** 2025-12-24 a 2026-01-21  \n"
    "**Resumen General:** Registro diario del flujo de visitantes para el segmento B2C correspondiente al periodo de finales de diciembre de 2025 a enero de 2026."
)

# Cálculo dinámico de KPIs
total_visitantes = int(df_filtered['Visitantes'].sum())
promedio_diario = round(df_filtered['Visitantes'].mean(), 2) if len(df_filtered) > 0 else 0
max_val = int(df_filtered['Visitantes'].max())
min_val = int(df_filtered['Visitantes'].min())

max_dates = df_filtered[df_filtered['Visitantes'] == max_val]['Fecha_Corta'].astype(str).tolist()
min_dates = df_filtered[df_filtered['Visitantes'] == min_val]['Fecha_Corta'].astype(str).tolist()

max_sub = f"Pico el {', '.join(max_dates)}" if len(max_dates) <= 2 else f"Pico en {len(max_dates)} días"
min_sub = f"Días: {', '.join(min_dates)}" if len(min_dates) <= 2 else f"Menor en {len(min_dates)} días"

# Bloque Horizontal de Tarjetas Métricas
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Total Visitantes Periodo",
        value=f"{total_visitantes:,}",
        help="Suma total de visitantes registrados en el rango seleccionado."
    )

with col2:
    st.metric(
        label="Promedio Diario",
        value=f"{promedio_diario}",
        help="Promedio de visitas diarias en los días evaluados."
    )

with col3:
    st.metric(
        label="Máximo Diario",
        value=f"{max_val}",
        delta=max_sub,
        delta_color="normal",
        help="Día de mayor afluencia en el periodo."
    )

with col4:
    st.metric(
        label="Mínimo Diario",
        value=f"{min_val}",
        delta=min_sub,
        delta_color="inverse",
        help="Días de menor afluencia en el periodo."
    )

st.markdown("---")

# --- ESTRUCTURA DE PESTAÑAS ---
tab1, tab2 = st.tabs(["📈 Análisis y Tendencias B2C", "📋 Visor de Datos Crudos (ST_B2C)"])

with tab1:
    st.markdown("### 📈 Evolución Temporal del Tráfico")
    
    # Gráfico 1: Evolución Temporal
    fig_line = px.line(
        df_filtered,
        x="Fecha",
        y="Visitantes",
        title="Tráfico Diario de Visitantes B2C",
        labels={"Fecha": "Fecha de Registro", "Visitantes": "Cantidad de Visitantes"},
        markers=True,
        template="plotly_white"
    )
    
    fig_line.add_hline(
        y=promedio_diario,
        line_dash="dash",
        line_color="red",
        annotation_text=f"Promedio ({promedio_diario})",
        annotation_position="top right"
    )
    
    for d_str in max_dates:
        d_row = df_filtered[df_filtered['Fecha_Corta'].astype(str) == d_str]
        if not d_row.empty:
            fig_line.add_annotation(
                x=d_row['Fecha'].values[0],
                y=max_val,
                text=f"Máx: {max_val}",
                showarrow=True,
                arrowhead=2,
                arrowcolor="green",
                ax=0,
                ay=-30
            )

    fig_line.update_layout(
        hovermode="x unified",
        legend=dict(orientation='h', yanchor='bottom', y=-0.25, xanchor='center', x=0.5)
    )
    st.plotly_chart(fig_line, use_container_width=True)
    
    st.markdown("---")
    
    # Gráfico 2: Comportamiento por Día de la Semana
    st.markdown("### 📅 Comportamiento del Tráfico por Día de la Semana")
    
    df_day = df_filtered.groupby("Día_Semana", as_index=False)["Visitantes"].mean()
    df_day['Día_Semana'] = pd.Categorical(df_day['Día_Semana'], categories=dias_ordenados, ordered=True)
    df_day = df_day.sort_values('Día_Semana').dropna()
    df_day['Visitantes'] = df_day['Visitantes'].round(2)
    
    fig_bar = px.bar(
        df_day,
        x="Día_Semana",
        y="Visitantes",
        title="Promedio de Visitantes según Día de la Semana",
        labels={"Día_Semana": "Día de la Semana", "Visitantes": "Promedio de Visitantes"},
        text_auto=True,
        color="Visitantes",
        color_continuous_scale="Blues",
        template="plotly_white"
    )
    fig_bar.update_layout(
        showlegend=False,
        legend=dict(orientation='h', yanchor='bottom', y=-0.25, xanchor='center', x=0.5)
    )
    st.plotly_chart(fig_bar, use_container_width=True)
    
    st.markdown("---")
    
    # Gráfico 3 y 4: Boxplot e Histograma
    st.markdown("### 📊 Distribución y Análisis Estadístico")
    col_a, col_b = st.columns(2)
    
    with col_a:
        fig_box = px.box(
            df_filtered,
            y="Visitantes",
            points="all",
            title="Diagrama de Caja (Boxplot) de Visitantes",
            labels={"Visitantes": "Cantidad de Visitantes"},
            template="plotly_white",
            color_discrete_sequence=["#1f77b4"]
        )
        fig_box.update_layout(
            legend=dict(orientation='h', yanchor='bottom', y=-0.25, xanchor='center', x=0.5)
        )
        st.plotly_chart(fig_box, use_container_width=True)
        
    with col_b:
        fig_hist = px.histogram(
            df_filtered,
            x="Visitantes",
            nbins=10,
            title="Histograma de Frecuencia de Visitas",
            labels={"Visitantes": "Rango de Visitantes", "count": "Frecuencia (Días)"},
            template="plotly_white",
            color_discrete_sequence=["#2ca02c"]
        )
        fig_hist.update_layout(
            bargap=0.1,
            legend=dict(orientation='h', yanchor='bottom', y=-0.25, xanchor='center', x=0.5)
        )
        st.plotly_chart(fig_hist, use_container_width=True)

with tab2:
    st.markdown("### 📋 Visor de Datos Crudos (ST_B2C)")
    
    st.dataframe(
        df_filtered[['Fecha', 'Visitantes', 'Día_Semana']].sort_values('Fecha', ascending=False),
        use_container_width=True,
        column_config={
            "Fecha": st.column_config.DateColumn("Fecha de Registro", format="YYYY-MM-DD"),
            "Visitantes": st.column_config.NumberColumn("Cantidad de Visitantes", format="%d visitantes"),
            "Día_Semana": st.column_config.TextColumn("Día de la Semana")
        }
    )
    
    st.markdown("---")
    st.markdown("### 📊 Resumen Estadístico Rápido")
    
    desc_df = df_filtered[['Visitantes']].describe().T.rename(
        columns={
            "count": "Conteo (Días)",
            "mean": "Media",
            "std": "Desv. Estándar",
            "min": "Mínimo",
            "25%": "Percentil 25",
            "50%": "Mediana (50%)",
            "75%": "Percentil 75",
            "max": "Máximo"
        }
    )
    st.dataframe(desc_df, use_container_width=True)
    
    st.markdown("---")
    st.markdown("### 📥 Exportación de Datos")
    
    csv_data = df_filtered[['Fecha_Corta', 'Visitantes', 'Día_Semana']].rename(columns={'Fecha_Corta': 'Fecha'}).to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Descargar Datos Filtrados (CSV)",
        data=csv_data,
        file_name="visitantes_b2c_filtrados.csv",
        mime="text/csv"
    )