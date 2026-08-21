import streamlit as st
import pandas as pd
import numpy as np
import datetime
import plotly.express as px

# Configuración de página en modo ancho (Wide)
st.set_page_config(
    page_title="Panel de Control y Seguimiento Operativo",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# 1. CARGA DE DATOS Y ALMACENAMIENTO EN CACHÉ
# -----------------------------------------------------------------------------
@st.cache_data
def cargar_datos():
    # Datos semilla basados en el esquema JSON provisto
    datos_iniciales = [
        {
            "ID": 1,
            "Fecha captura": "2026-07-07",
            "Concepto": "OC cimentaciones",
            "Departamento": "Compras",
            "Contratista": None,
            "Responsable": None,
            "Estatus": "Cerrado",
            "Siguiente paso": "ya se tiene cotizacion con Rangel, se comparte el dia de hoy para revision"
        },
        {
            "ID": 2,
            "Fecha captura": "2026-07-07",
            "Concepto": "OC estructura",
            "Departamento": "Compras",
            "Contratista": None,
            "Responsable": "Judith Echeverria",
            "Estatus": "Critico",
            "Siguiente paso": "Se comparte OC el dia de hoy, anticipo se paga en 15 dias, en confirmacion de reunion el dia de hoy  (TECOIMSA)"
        },
        {
            "ID": 3,
            "Fecha captura": "2026-07-07",
            "Concepto": "Entrega diseño de estructura",
            "Departamento": "Diseño",
            "Contratista": None,
            "Responsable": "Carlos Mendez",
            "Estatus": "En proceso",
            "Siguiente paso": "En proceso de revision y vobo de NIDEC"
        },
        # Registros sintéticos adicionales para robustecer las visualizaciones
        {
            "ID": 4,
            "Fecha captura": "2026-07-08",
            "Concepto": "Licitación instalaciones eléctricas",
            "Departamento": "Compras",
            "Contratista": "Sinergia Eléctrica S.A.",
            "Responsable": "Judith Echeverria",
            "Estatus": "En proceso",
            "Siguiente paso": "Esperando el envío de la propuesta técnica corregida"
        },
        {
            "ID": 5,
            "Fecha captura": "2026-07-10",
            "Concepto": "Aprobación planos arquitectónicos",
            "Departamento": "Diseño",
            "Contratista": None,
            "Responsable": "Carlos Mendez",
            "Estatus": "Critico",
            "Siguiente paso": "Revisar observaciones del cliente sobre salidas de emergencia"
        },
        {
            "ID": 6,
            "Fecha captura": "2026-07-12",
            "Concepto": "Movimiento de tierras",
            "Departamento": "Construcción",
            "Contratista": "Excavaciones de México",
            "Responsable": "Ing. Eduardo Ruiz",
            "Estatus": "Cerrado",
            "Siguiente paso": "Cierre de bitácora y firma de actas de entrega de fase"
        },
        {
            "ID": 7,
            "Fecha captura": "2026-07-14",
            "Concepto": "Instalación de faena y oficinas temporales",
            "Departamento": "Construcción",
            "Contratista": "Construcciones del Norte",
            "Responsable": "Ing. Eduardo Ruiz",
            "Estatus": "En proceso",
            "Siguiente paso": "Conexión provisional de acometida eléctrica para contratistas"
        },
        {
            "ID": 8,
            "Fecha captura": "2026-07-15",
            "Concepto": "Gestión de permisos de descarga pluvial",
            "Departamento": "Legal",
            "Contratista": None,
            "Responsable": "Sofía Castro",
            "Estatus": "Critico",
            "Siguiente paso": "Ingresar recurso de reconsideración ante ventanilla única municipal"
        }
    ]
    
    df = pd.DataFrame(datos_iniciales)
    
    # Conversión de tipos de datos obligatorios
    df["Fecha captura"] = pd.to_datetime(df["Fecha captura"]).dt.date
    
    # Tratamiento de nulos/vacíos para filtros interactivos limpios
    df["Responsable"] = df["Responsable"].fillna("Sin Responsable Asignado")
    df["Contratista"] = df["Contratista"].fillna("Sin Contratista Asignado")
    
    return df

try:
    df_raw = cargar_datos()
except Exception as e:
    st.error(f"Error al inicializar la base de datos: {e}")
    st.stop()

# -----------------------------------------------------------------------------
# 2. CONFIGURACIÓN DEL MENÚ LATERAL (FILTROS INTERACTIVOS)
# -----------------------------------------------------------------------------
st.sidebar.header("Filtros de Control")

# Obtener límites de fechas dinámicos
min_fecha = df_raw["Fecha captura"].min()
max_fecha = df_raw["Fecha captura"].max()

# 1. Rango de Fechas
st.sidebar.subheader("Periodo de Captura")
rango_fechas = st.sidebar.date_input(
    "Selecciona el rango de fechas:",
    value=(min_fecha, max_fecha),
    min_value=min_fecha,
    max_value=max_fecha
)

# 2. Filtro de Departamento
departamentos_disponibles = sorted(df_raw["Departamento"].dropna().unique())
departamentos_seleccionados = st.sidebar.multiselect(
    "Departamento:",
    options=departamentos_disponibles,
    default=departamentos_disponibles
)

# 3. Filtro de Estatus
estatus_disponibles = sorted(df_raw["Estatus"].dropna().unique())
estatus_seleccionados = st.sidebar.multiselect(
    "Estatus del Requerimiento:",
    options=estatus_disponibles,
    default=estatus_disponibles
)

# 4. Filtro de Responsable
responsables_disponibles = sorted(df_raw["Responsable"].unique())
responsables_seleccionados = st.sidebar.multiselect(
    "Responsable Asignado:",
    options=responsables_disponibles,
    default=responsables_disponibles
)

# 5. Filtro de Contratista
contratistas_disponibles = sorted(df_raw["Contratista"].unique())
contratistas_seleccionados = st.sidebar.multiselect(
    "Contratista:",
    options=contratistas_disponibles,
    default=contratistas_disponibles
)

# Aplicar filtros interactivos al DataFrame principal
df_filtrado = df_raw.copy()

# Validación del rango de fechas seleccionado
if isinstance(rango_fechas, tuple) and len(rango_fechas) == 2:
    fecha_inicio, fecha_fin = rango_fechas
    df_filtrado = df_filtrado[
        (df_filtrado["Fecha captura"] >= fecha_inicio) & 
        (df_filtrado["Fecha captura"] <= fecha_fin)
    ]
elif isinstance(rango_fechas, datetime.date):
    df_filtrado = df_filtrado[df_filtrado["Fecha captura"] == rango_fechas]

# Aplicación de los filtros categóricos si el usuario tiene selecciones activas
if departamentos_seleccionados:
    df_filtrado = df_filtrado[df_filtrado["Departamento"].isin(departamentos_seleccionados)]
else:
    df_filtrado = df_filtrado[df_filtrado["Departamento"].isin([])]

if estatus_seleccionados:
    df_filtrado = df_filtrado[df_filtrado["Estatus"].isin(estatus_seleccionados)]
else:
    df_filtrado = df_filtrado[df_filtrado["Estatus"].isin([])]

if responsables_seleccionados:
    df_filtrado = df_filtrado[df_filtrado["Responsable"].isin(responsables_seleccionados)]
else:
    df_filtrado = df_filtrado[df_filtrado["Responsable"].isin([])]

if contratistas_seleccionados:
    df_filtrado = df_filtrado[df_filtrado["Contratista"].isin(contratistas_seleccionados)]
else:
    df_filtrado = df_filtrado[df_filtrado["Contratista"].isin([])]


# -----------------------------------------------------------------------------
# 3. CUERPO PRINCIPAL DE LA APLICACIÓN
# -----------------------------------------------------------------------------
st.title("Panel de Control y Seguimiento Operativo")
st.markdown(
    """
    Bienvenido al centro de control operativo del proyecto. Utilice los filtros del panel lateral para 
    segmentar los requerimientos, evaluar cuellos de botella mediante las métricas en tiempo real 
    y revisar las minutas de los siguientes pasos para la toma de decisiones ágiles.
    """
)
st.divider()

# Métricas Clave
col_metric1, col_metric2, col_metric3, col_metric4 = st.columns(4)

total_requerimientos = int(df_filtrado["ID"].nunique())
total_criticos = int(df_filtrado[df_filtrado["Estatus"] == "Critico"].shape[0])
total_proceso = int(df_filtrado[df_filtrado["Estatus"] == "En proceso"].shape[0])
total_cerrados = int(df_filtrado[df_filtrado["Estatus"] == "Cerrado"].shape[0])

with col_metric1:
    st.metric(label="Total de Requerimientos", value=total_requerimientos)

with col_metric2:
    st.metric(label="⚠️ Estatus Crítico", value=total_criticos, delta_color="inverse")

with col_metric3:
    st.metric(label="🔄 En Proceso", value=total_proceso)

with col_metric4:
    st.metric(label="✅ Completadas", value=total_cerrados)

st.divider()

# -----------------------------------------------------------------------------
# 4. TABLA DE DATOS PRINCIPAL INTERACTIVA CON FORMATO CONDICIONAL
# -----------------------------------------------------------------------------
st.subheader("📋 Registro de Tareas y Requerimientos")

def formatear_filas(row):
    # Formato condicional: fondo rojo suave para los registros críticos
    color_critico = "background-color: #ffdddd; color: #900000; font-weight: bold;"
    default = ""
    return [color_critico if row["Estatus"] == "Critico" else default for _ in row]

if not df_filtrado.empty:
    df_ordenado = df_filtrado.sort_values(by="ID", ascending=True)
    
    # Convertimos ID a string para evitar formato numérico con comas en el visualizador
    df_mostrar = df_ordenado.copy()
    df_mostrar["ID"] = df_mostrar["ID"].astype(str)
    
    # Aplicar estilos interactivos
    styled_df = df_mostrar.style.apply(formatear_filas, axis=1)
    
    st.dataframe(
        styled_df,
        column_order=["ID", "Fecha captura", "Concepto", "Departamento", "Contratista", "Responsable", "Estatus", "Siguiente paso"],
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("No se encontraron registros bajo los filtros configurados.")

st.divider()

# -----------------------------------------------------------------------------
# 5. VISUALIZACIONES (GRÁFICOS)
# -----------------------------------------------------------------------------
col_chart1, col_chart2 = st.columns(2)

# Mapeo de colores semáforo consistentes
colores_semaforo = {
    "Critico": "#ef553b",     # Rojo
    "En proceso": "#fecb52",  # Amarillo/Naranja
    "Cerrado": "#00cc96"      # Verde
}

with col_chart1:
    st.subheader("📊 Carga de Trabajo por Departamento")
    if not df_filtrado.empty:
        # Generar datos agrupados para barras apiladas
        df_agrupado = df_filtrado.groupby(["Departamento", "Estatus"]).size().reset_index(name="Tareas")
        
        fig_barras = px.bar(
            df_agrupado,
            x="Departamento",
            y="Tareas",
            color="Estatus",
            color_discrete_map=colores_semaforo,
            category_orders={"Estatus": ["Critico", "En proceso", "Cerrado"]},
            labels={"Tareas": "Cantidad de Tareas", "Departamento": "Departamento Responsable"},
            barmode="stack",
            height=380
        )
        fig_barras.update_layout(
            legend_title_text="Estatus",
            margin=dict(l=20, r=20, t=30, b=20)
        )
        st.plotly_chart(fig_barras, use_container_width=True)
    else:
        st.info("Filtre datos para generar la distribución por departamento.")

with col_chart2:
    st.subheader("🍕 Distribución del Estado del Proyecto")
    if not df_filtrado.empty:
        # Generar conteo de estatus
        df_estatus = df_filtrado.groupby("Estatus").size().reset_index(name="Total")
        
        fig_pastel = px.pie(
            df_estatus,
            names="Estatus",
            values="Total",
            color="Estatus",
            color_discrete_map=colores_semaforo,
            category_orders={"Estatus": ["Critico", "En proceso", "Cerrado"]},
            hole=0.4,
            height=380
        )
        fig_pastel.update_layout(
            margin=dict(l=20, r=20, t=30, b=20)
        )
        fig_pastel.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pastel, use_container_width=True)
    else:
        st.info("Filtre datos para visualizar la distribución del estatus.")

st.divider()

# -----------------------------------------------------------------------------
# 6. DETALLE DE PRÓXIMAS ACCIONES (LISTA DE SEGUIMIENTO)
# -----------------------------------------------------------------------------
st.subheader("📋 Lista de Próximas Acciones de Seguimiento")
st.markdown(
    """
    **Minuta de Trabajo Rápida:** Visualización enfocada exclusivamente en tareas pendientes 
    (`Crítico` y `En proceso`) para guiar reuniones operativas diarias y resolver cuellos de botella rápidamente.
    """
)

# Filtrado específico para pendientes
df_pendientes = df_filtrado[df_filtrado["Estatus"].isin(["Critico", "En proceso"])]

if not df_pendientes.empty:
    for idx, row in df_pendientes.iterrows():
        # Determinamos colores del indicador basado en el estatus
        es_critico = row["Estatus"] == "Critico"
        status_emoji = "🚨" if es_critico else "🔄"
        status_label = "CRÍTICO" if es_critico else "EN PROCESO"
        
        # Presentación en contenedores de tipo tarjeta informativa
        with st.container():
            col_icon, col_content = st.columns([0.08, 0.92])
            with col_icon:
                st.markdown(f"<h2 style='text-align: center;'>{status_emoji}</h2>", unsafe_allow_html=True)
            with col_content:
                st.markdown(f"#### {row['Concepto']} (`{row['Departamento']}`)")
                st.write(f"**Responsable:** {row['Responsable']} | **Contratista:** {row['Contratista']} | **Estatus:** :red[{status_label}]" if es_critico else f"**Responsable:** {row['Responsable']} | **Contratista:** {row['Contratista']} | **Estatus:** :orange[{status_label}]")
                st.info(f"👉 **Siguiente Paso:** {row['Siguiente paso']}")
            st.markdown("---")
else:
    st.success("🎉 ¡Excelente trabajo! No hay requerimientos críticos o pendientes registrados bajo la selección actual.")