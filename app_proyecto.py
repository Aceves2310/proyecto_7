#importar librerias
import pandas as pd
import plotly.express as px
import streamlit as st

#carga de datos
df= pd.read_csv('https://repodatos.atdt.gob.mx/api_update/senasica/padron_clinicas_farmacias_hospitales/59_padron-de-clinicas-hospitales-y-farmacias.csv')

# Titulo
st.header('Hospitales y clinicas veterinarias en México', divider = "gray")

# Boton Descargar
st.download_button(
    label = "Descargar dataset", 
    data = df.to_csv(index=False), 
    file_name = "df.csv"
)

st.divider()

#Se crea y se aplica una función para categorizar el nombre de la empresa en base a las palabras que tiene su nombre

def clasificar_empresa(nombre):
    nombre = nombre.lower()
    if any(razon in nombre for razon in ['s de rl', 's.a.', 's.a. de c.v.', 's. de r.l.', 'sapi', 's.c.', 'cv']):
        return 'persona_moral'
    elif any(palabra in nombre for palabra in ['veterinarios', 'hospital', 'centro', 'servicios', 'clínica', 'grupo', 'corporativo', 'friends', 'pets']):
        return 'persona_moral'
    elif 'y o' in nombre or len(nombre.split()) >= 3:
        return 'persona_fisica'
    else:
        return 'indeterminado'

df['tipo_empresa'] = df['empresa'].apply(clasificar_empresa)

columnas_numericas = ['clinica_veterinaria', 'farmacia_veterinaria', 'hospital_veterinario']

df[columnas_numericas] = (
    df[columnas_numericas]
      .replace({'si': 1, 'no': 0})
      .apply(pd.to_numeric, errors='coerce')  # valores inválidos  NaN
      .astype('Int64') )

# Eliminar filas que tengan NaN en *cualquiera* de esas columnas
df = df.dropna(subset=columnas_numericas)
df[columnas_numericas] = df[columnas_numericas].astype(int)


# Calcular cobertura total
df['cobertura_total'] = df[['clinica_veterinaria', 'farmacia_veterinaria', 'hospital_veterinario']].sum(axis=1)

# Agrupamiento
df['tipo_empresa_legible'] = df['tipo_empresa'].map({
    'persona_fisica': 'Persona Física',
    'persona_moral': 'Persona Moral'
})
agrupado = df.groupby(['tipo_empresa_legible', 'cobertura_total']).size().reset_index(name='frecuencia')

# Titulo
st.header('Dispersión por tipo de empresa', divider='gray')

# Botón para mostrar gráfico
if st.button('Mostrar gráfico de frecuencia'):
    fig = px.scatter(
        agrupado,
        x='tipo_empresa_legible',
        y='cobertura_total',
        size='frecuencia',
        color='frecuencia',
        title='Frecuencia de empresas por tipo y cobertura',
        labels={'tipo_empresa_legible': 'Tipo de Empresa', 'cobertura_total': 'Cobertura Total'},
        template='plotly_white'
    )
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig)

st.metric("Total de empresas", len(df))
st.metric("Cobertura promedio", round(df['cobertura_total'].mean(), 2))

# Título
st.header('Distribución por estado', divider='gray')

# Agrupar por estado
conteo_estados = df['estado'].value_counts().reset_index()
conteo_estados.columns = ['estado', 'cantidad']

# Botón para mostrar gráfico
if st.button('Mostrar gráfico de barras'):
    fig = px.bar(
        conteo_estados,
        x='estado',
        y='cantidad',
        text='cantidad',
        title='Distribución de empresas veterinarias por estado',
        labels={'estado': 'Estado', 'cantidad': 'Cantidad de empresas'},
        template='plotly_white',
        color='estado'
    )
    fig.update_traces(textposition='outside')
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig)

# Conteo de estados
total_estados = conteo_estados['estado'].nunique()

# Estado con mayor cantidad de empresas
estado_top = conteo_estados.loc[conteo_estados['cantidad'].idxmax()]

# Estado con menor cantidad de empresas
estado_min = conteo_estados.loc[conteo_estados['cantidad'].idxmin()]

# Promedio de empresas por estado
promedio_empresas = round(conteo_estados['cantidad'].mean(), 2)

# Mostrar métricas
st.subheader('Indicadores clave')
col1, col2, col3, col4 = st.columns(4)
col1.metric("Estados representados", total_estados)
col2.metric("Estado con más empresas", f"{estado_top['estado']}", delta=int(estado_top['cantidad']))
col3.metric("Estado con menos empresas", f"{estado_min['estado']}", delta=int(estado_min['cantidad']))
col4.metric("Promedio por estado", promedio_empresas)
 
st.divider()

st.header(' Histograma de cobertura total por empresa')

if st.button(' Mostrar histograma'):
    fig = px.histogram(
        df,
        x='cobertura_total',
        nbins=6,
        title='Distribución de cobertura total por empresa',
        labels={'cobertura_total': 'Cobertura Total'},
        template='plotly_white',
        
    )
    fig.update_layout(
        xaxis_title='Número de servicios ofrecidos',
        yaxis_title='Cantidad de empresas',
        bargap=0.2
    )
    st.plotly_chart(fig)
