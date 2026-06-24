import pandas as pd
import streamlit as st
import plotly.express as px

# 1. Configuración de la página
st.set_page_config(page_title="Guía de Precios Inmobiliarios", layout="centered", page_icon="🏢")

# 2. Cargar la base de datos
@st.cache_data
def load_data():
    return pd.read_csv("Guia_Inmobiliaria_Pachuca.csv")

df = load_data()

# 3. Encabezado de la App
st.title("🏢 Consulta de Valores de Terreno")
st.markdown("**Soluciones para Inmobiliarias de Precisión | Zona Conurbada Pachuca**")
st.divider()

# 4. LÓGICA DE INTERFAZ (Filtros en cascada)
zonas_disponibles = df['Nombre_Zona'].unique()
zona_seleccionada = st.selectbox("📍 1. Elige la Zona:", zonas_disponibles)

colonias_filtradas = df[df['Nombre_Zona'] == zona_seleccionada]['Colonia_Fraccionamiento'].unique()
colonia_seleccionada = st.selectbox("🏘️ 2. Elige la Colonia o Fraccionamiento:", colonias_filtradas)

st.divider()

# 5. DESPLIEGUE DE RESULTADOS
if colonia_seleccionada:
    filtro = (df['Nombre_Zona'] == zona_seleccionada) & (df['Colonia_Fraccionamiento'] == colonia_seleccionada)
    
    if not df[filtro].empty:
        datos = df[filtro].iloc[0]
        
        st.subheader(f"{datos['Colonia_Fraccionamiento']}")
        st.caption(f"Vocación principal: {datos['Vocación']}")
        
        # Tarjetas numéricas
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="Valor Mínimo", value=f"${datos['Valor_Minimo_m2']:,.2f}")
        with col2:
            st.metric(label="Valor Promedio", value=f"${datos['Valor_Promedio_m2']:,.2f}")
        with col3:
            st.metric(label="Valor Máximo", value=f"${datos['Valor_Maximo_m2']:,.2f}")
            
        st.info(f"📈 **Tasa de Plusvalía (promedio últimos 8 años):** {datos['Tasa_Variacion']}%")
        
        st.divider()
        
        # 6. GRÁFICA DE BARRAS DINÁMICA
        st.subheader("📊 Análisis de Mercado (m²)")
        
        df_grafica = pd.DataFrame({
            'Categoría': ['Mínimo', 'Promedio', 'Máximo'],
            'Valor (MXN)': [float(datos['Valor_Minimo_m2']), float(datos['Valor_Promedio_m2']), float(datos['Valor_Maximo_m2'])]
        })
        
        fig = px.bar(
            df_grafica, 
            x='Categoría', 
            y='Valor (MXN)', 
            text='Valor (MXN)',
            color='Categoría',
            color_discrete_sequence=['#4CAF50', '#2196F3', '#F44336']
        )
        
        fig.update_traces(texttemplate='$%{text:,.2f}', textposition='outside')
        fig.update_layout(showlegend=False, yaxis_title="Precio por m² (MXN)", margin=dict(t=30, b=0, l=0, r=0))
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # 7. SECCIÓN DEL MAPA INTERACTIVO (MAPBOX SATELITAL)
        st.subheader("🗺️ Ubicación y Georreferenciación")
        
        if 'Latitud' in datos and 'Longitud' in datos and pd.notna(datos['Latitud']) and pd.notna(datos['Longitud']):
            try:
                if "MAPBOX_TOKEN" in st.secrets:
                    mapa_df = pd.DataFrame({
                        'lat': [float(datos['Latitud'])],
                        'lon': [float(datos['Longitud'])],
                        'Colonia': [datos['Colonia_Fraccionamiento']],
                        'Precio': [f"${datos['Valor_Promedio_m2']:,.2f}/m²"]
                    })
                    
                    fig_mapa = px.scatter_mapbox(
                        mapa_df,
                        lat="lat",
                        lon="lon",
                        hover_name="Colonia",
                        hover_data={"Precio": True, "lat": False, "lon": False},
                        zoom=16, # Un poco más de zoom para apreciar las calles en el satélite
                        height=450
                    )
                    
                    # FORZAR EL TOKEN Y EL ESTILO SATELITAL DIRECTAMENTE EN EL MAPA
                    fig_mapa.update_layout(
                        mapbox_style="satellite-streets", 
                        mapbox_accesstoken=st.secrets["MAPBOX_TOKEN"],
                        margin=dict(t=0, b=0, l=0, r=0)
                    )
                    
                    fig_mapa.update_traces(marker=dict(size=22, color='#E91E63', symbol='circle'))
                    
                    st.plotly_chart(fig_mapa, use_container_width=True)
                    st.caption("📍 Ubicación precisa. Vista satelital de alta resolución (arrastra y haz zoom).")
                else:
                    st.warning("⚠️ Configura el 'MAPBOX_TOKEN' en los Secrets de Streamlit.")
                    
            except Exception as e:
                st.error("Ocurrió un error al cargar el mapa con las coordenadas proporcionadas.")
        else:
            st.warning("📍 Coordenadas no disponibles para esta colonia en la base de datos actual.")
            
    else:
        st.error("No se encontraron datos para esta selección.")
