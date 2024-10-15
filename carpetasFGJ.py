import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import datetime
import plotly.express as px
import plotly.graph_objects as go

###################
#Funciones



#######################
# Page configuration
st.set_page_config(
    page_title="Carpetas de investigacion FGJ",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded")

alt.themes.enable("dark")

#######################
# CSS styling
st.markdown("""
<style>

[data-testid="block-container"] {
    padding-left: 2rem;
    padding-right: 2rem;
    padding-top: 1rem;
    padding-bottom: 0rem;
    margin-bottom: -7rem;
}

[data-testid="stVerticalBlock"] {
    padding-left: 0rem;
    padding-right: 0rem;
}

[data-testid="stMetric"] {
    background-color: #393939;
    text-align: center;
    padding: 15px 0;
}

[data-testid="stMetricLabel"] {
  display: flex;
  justify-content: center;
  align-items: center;
}

[data-testid="stMetricDeltaIcon-Up"] {
    position: relative;
    left: 38%;
    -webkit-transform: translateX(-50%);
    -ms-transform: translateX(-50%);
    transform: translateX(-50%);
}

[data-testid="stMetricDeltaIcon-Down"] {
    position: relative;
    left: 38%;
    -webkit-transform: translateX(-50%);
    -ms-transform: translateX(-50%);
    transform: translateX(-50%);
}

</style>
""", unsafe_allow_html=True)

#######################
#Exportación de datos
bd = pd.read_csv('./delitosFGJ.csv',index_col = 'fecha_inicio',parse_dates = True)
bd.fecha_hecho = pd.DatetimeIndex(bd.fecha_hecho)


##
dias = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado", "Domingo"]
mes = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre",
      "Noviembre", "Diciembre"]

##################################################
# Dashboard Main Panel

st.title("Carpetas de investigación de FGJ")
tab1, tab2, tab3 = st.tabs(["General", "Busqueda","Actualidad"])

with tab1:
	st.header("Datos de la base de datos", divider="gray")
	st.markdown("Análisis de la base de datos de Carpetas de Investigación de la Fiscalía General de Justicia (FGJ) de la Ciudad de México. La base de datos utilizada fue obtenida del portal de Datos Abiertos del Gobierno de la Ciudad de México y está disponible en (https://datos.cdmx.gob.mx/dataset/carpetas-de-investigacion-fgj-de-la-ciudad-de-mexico). La base de datos contiene información actualizada sobre las carpetas de investigación de delitos a nivel de calle registradas por la FGJ a partir de enero de 2016.")
	crime_count = bd.categoria_delito.value_counts()
	fig=go.Figure()
	fig.add_trace(go.Bar(x=crime_count.index[:10],y = crime_count.values[:10],
                     text=crime_count.values[:10]))
	fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')
	st.plotly_chart(fig, use_container_width=True) 

	del_alc = bd.groupby([bd.categoria_delito,bd.alcaldia_catalogo]).size()
	fig2=go.Figure()
	for alc in bd.categoria_delito[bd.categoria_delito.notna()].unique() :
  		datos = del_alc[alc]
  		fig2.add_trace(go.Bar(x=datos.index,y = datos.values,name = str(alc)))
	fig2.update_layout(barmode='relative', title_text='Delitos por alcaldía')
	st.plotly_chart(fig2, use_container_width=True)
	option = st.selectbox("Selecciona un periodo de conteo:",("Día", "Mes", "Año"),)
	if option == "Día":
		fecha_count = bd.groupby([bd.index.dayofweek]).size()
		fig3=go.Figure()
		fig3.add_trace(go.Bar(x=dias,y = fecha_count.values,text=fecha_count.values)) 
	elif option == "Mes":
		fecha_count = bd.groupby([bd.index.month]).size()
		fig3=go.Figure()
		fig3.add_trace(go.Bar(x=mes,y = fecha_count.values,text=fecha_count.values)) 
	else:		
		fecha_count = bd.groupby([bd.index.year]).size()
		fig3=go.Figure()
		fig3.add_trace(go.Bar(x=[2020,2021,2022,2023,2024],y = fecha_count.values,text=fecha_count.values)) 
	st.plotly_chart(fig3, use_container_width=True)

with tab2:
	st.header("Busqueda filtrada de datos", divider="gray")
	cat_delitos = bd.categoria_delito.unique()
	delito = st.selectbox("Selecciona una categoría de delito:",cat_delitos,)
	crimes_del = bd[bd['categoria_delito'] == delito]
	a = st.date_input("Fecha inicio", datetime.date(2020, 1, 1))
	b = st.date_input("Fecha final", datetime.date(2024, 6, 15))
	if a<=b: 
		idx =  (crimes_del.fecha_hecho>= str(a))&(crimes_del.fecha_hecho<= str(b))
	else:
		idx =  (crimes_del.fecha_hecho>= str(b))&(crimes_del.fecha_hecho<= str(a))
	crimes_new = crimes_del[idx]
	
	datos = crimes_new.groupby([crimes_new.fecha_hecho]).size()
	fig4=go.Figure()
	fig4.add_trace(go.Scatter(x=datos.index, y=datos.values,
                    mode='lines+markers',name = str(alc)))
	st.plotly_chart(fig4, use_container_width=True)
	
	st.map(crimes_new[(crimes_new["longitud"].notna())&(crimes_new["latitud"].notna())], latitude="latitud", longitude="longitud",use_container_width=True)

with tab3:
	st.header("Carpetas abiertas en 2024", divider="gray")
	bd_2024 = bd[bd.index>='01-01-2024']
	crime_count = bd_2024.categoria_delito.value_counts()
	fig6=go.Figure()
	fig6.add_trace(go.Bar(x=crime_count.index[:10],y = crime_count.values[:10],
                     text=crime_count.values[:10]))
	fig6.update_traces(texttemplate='%{text:.2s}', textposition='outside')
	fig6.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
	st.plotly_chart(fig6, use_container_width=True)
	
	cat_delitos = bd_2024.categoria_delito.unique()
	fig7=go.Figure()
	for delito in cat_delitos:
  		crimes_year = bd_2024[bd_2024['categoria_delito'] == delito]
  		datos = crimes_year.groupby([crimes_year.fecha_hecho]).size()
  		fig7.add_trace(go.Scatter(x=datos.index, y=datos.values,
                      mode='lines+markers',name = delito))
	st.plotly_chart(fig7, use_container_width=True)

	option2 = st.selectbox("Selecciona un periodo de conteo:",("Día", "Mes"),)
	if option2 == "Día":
		fecha_count = bd.groupby([bd.index.dayofweek]).size()
		fig8=go.Figure()
		fig8.add_trace(go.Bar(x=dias,y = fecha_count.values,text=fecha_count.values)) 
	else:
		fecha_count = bd.groupby([bd.index.month]).size()
		fig8=go.Figure()
		fig8.add_trace(go.Bar(x=mes,y = fecha_count.values,text=fecha_count.values)) 
	st.plotly_chart(fig8, use_container_width=True)
