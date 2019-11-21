#!/usr/bin/env python
# coding: utf-8

# # <center>Procesamiento de EPV bajado de OSM

# #### Procesamiento de datos de Parques y Reservas Naturalez bajadas de OSM. 
# #### El proceso devuelve un shp con los puntos sobre el périmetro de los polígonos o en el caso de los polígonos pequeños su centroide (ambos parámetros se definen en la función del punto "Generación de los puntos sobre Perímetro"), para luego ser utilizados para generar el archivo para las consultas a la API de Google.
# #### Si los datos están guardados correctamente (nombre y carpeta), solamente cambiando el nombre de la ciudad en "Definir ciudad y paths", las direcciones para cargar y exportar los datos se modifican, y todo el proceso corre de punta a punta.
# 
# <a id='indice'></a>
# ## Indice
#   
# <a href='#section1'>**Punto 1:**</a>   Definir ciudad y paths   
# <a href='#section2'>**Punto 2:**</a>   Carga de datos   
# <a href='#section3'>**Punto 3:**</a>   Proceso de datos de OSM   
# <a href='#section4'>**Punto 4:**</a>   Poligonos a Linea de Perímetro   
# <a href='#section5'>**Punto 5:**</a>   Generación de los puntos sobre Perímetro   
# <a href='#section6'>**Punto 6:**</a>   Calcular distancias más cercana   

# In[15]:


import requests
import numpy as np
import pandas as pd

import geopandas as gpd
import fiona
from shapely.ops import nearest_points
from shapely.geometry import LineString

import matplotlib.pyplot as plt
import seaborn as sns

# some_file.py
import sys
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, 'D:/JOB/Python_Functions/')

import anapos


# <a id='section1'></a>
# 
# <div style="border-bottom:1px solid #000;"> 
# <div align="center"><h2>Definir ciudad y paths</h2></div>
# <div align="right">(volver a <a href='#indice'><b>Indice</b></a>)</div>
# </div>

# In[9]:


# Ciudad de Estudio
Ciudad = 'BuenosAires'

# Path general de la Carpeta (donde se guardarán los resultados)
PATH = 'D:/JOB/SA/EPV_Ciudades/EPV_'+ Ciudad + '/'

# Path a los distintos SHPs
Path_AreaInteres = PATH + 'AreaInteres/' + Ciudad + '.shp'
Path_Parques = 'D:/JOB/SA/SHP/OSM/EspacioVerdePúblico/OSM_Parks.shp'
Path_Reservas = 'D:/JOB/SA/SHP/OSM/EspacioVerdePúblico/OSM_NatureReserve.shp'
Path_Radios = PATH + 'Radios/Radios_' + Ciudad + '.shp'
Path_Zonas = PATH + 'Radios/Zonas_' + Ciudad + '.shp'


# <a id='section2'></a>
# 
# <div style="border-bottom:1px solid #000;"> 
# <div align="center"><h2>Carga de datos</h2></div>
# <div align="right">(volver a <a href='#indice'><b>Indice</b></a>)</div>
# </div>

# In[10]:


AreaInteres = gpd.read_file(Path_AreaInteres)
AreaInteres.head(3)


# In[11]:


Parques = gpd.read_file(Path_Parques)
Parques.head(3)


# In[12]:


Reservas = gpd.read_file(Path_Reservas)
Reservas.head(3)


# In[13]:


Zonas = gpd.read_file(Path_Zonas)
Zonas.crs = {'init' :'epsg:4326'}
Zonas.head(3)


# <a id='section3'></a>
# 
# <div style="border-bottom:1px solid #000;"> 
# <div align="center"><h2>Proceso de datos de OSM</h2></div>
# <div align="right">(volver a <a href='#indice'><b>Indice</b></a>)</div>
# </div>

# ### Parques

# In[ ]:


Parque_Area = gpd.overlay(Parques, AreaInteres, how='intersection')
Parque_Area.head(3)


# In[ ]:


fig, ax = plt.subplots(figsize=(15,15))
AreaInteres.plot(ax=ax, color='lightgrey')
Parque_Area.plot(ax=ax, color='green');


# ### Reserva Natural

# In[ ]:


Reservas_Area = gpd.overlay(Reservas, AreaInteres, how='intersection')
Reservas_Area.head(3)


# In[ ]:


fig, ax = plt.subplots(figsize=(15,15))
AreaInteres.plot(ax=ax, color='lightgrey')
Parque_Area.plot(ax=ax, color='green')
Reservas_Area.plot(ax=ax, color='yellow');


# ### Unimos Parques y Reservas

# In[ ]:


EspaciosVerdes = gpd.GeoDataFrame(pd.concat([Parque_Area, Reservas_Area], ignore_index=True, sort=False))
EspaciosVerdes.crs = {'init' :'epsg:4326'}
EspaciosVerdes.head(3)


# In[ ]:


fig, ax = plt.subplots(figsize=(15,15))
AreaInteres.plot(ax=ax, color='lightgrey')
EspaciosVerdes.plot(ax=ax, color='green');


# In[ ]:


EspaciosVerdes.to_file(PATH + '/EspaciosVerdes_' + Ciudad + '.shp')


# <a id='section4'></a>
# 
# <div style="border-bottom:1px solid #000;"> 
# <div align="center"><h2>Poligonos de Espacios Verdes a Linea</h2></div>
# <div align="right">(volver a <a href='#indice'><b>Indice</b></a>)</div>
# </div>

# In[ ]:


# Generamos un gdf los EVP como líneas
EspaciosVerdes_lineas = pd.DataFrame(EspaciosVerdes.boundary)
EspaciosVerdes_lineas.rename(columns={ EspaciosVerdes_lineas.columns[0]: "geometry" }, inplace = True)
EspaciosVerdes_lineas_GDF = gpd.GeoDataFrame(EspaciosVerdes_lineas, geometry='geometry')
EspaciosVerdes_lineas_GDF.crs = {'init' :'epsg:4326'}


# In[ ]:


fig, ax = plt.subplots(figsize=(15,15))
AreaInteres.plot(ax=ax, color='lightgrey')
EspaciosVerdes.plot(ax=ax, color='yellow')
EspaciosVerdes_lineas_GDF.plot(ax=ax, color='green');


# In[ ]:


# Guardamos el gdf como SHP
EspaciosVerdes_lineas_GDF.to_file(PATH + '/EspaciosVerdes_lineas_' + Ciudad + '.shp')


# <a id='section5'></a>
# 
# <div style="border-bottom:1px solid #000;"> 
# <div align="center"><h2>Generación de los puntos sobre Perímetro</h2></div>
# <div align="right">(volver a <a href='#indice'><b>Indice</b></a>)</div>
# </div>

# ### Puntos sobre Perímetro de Polígonos

# In[ ]:


# Función que devuelve puntos sobre las líneas a una distancia especificada. Si el perímetro es inferior al doble de 
# esta distancia, se calcula el centroide de la línea.-

def Lineas_a_Puntos_Intervalo(DataOriginal, Dist_puntos, Dist_min_perimetro):
     
    Div = Dist_puntos * 1.0457242224755355e-05     # distancia aprox en grados
    DMP = Dist_min_perimetro * 1.0457242224755355e-05    # distancia aprox en grados
    

    DO_Inter = DataOriginal.loc[DataOriginal.Dist > DMP]   # lineas con una longitud mayor a Distancia_entre_puntos
    DO_Inter.reset_index(inplace=True)                     # se resetean los índices para que no haya saltos y corra el for

    DF = pd.DataFrame()    # se genera un df vacío donde almacenar las coordenadas de los puntos

    for c in range(len(DO_Inter)):     # se itera por las líneas
        lista_puntos=[]                # se genera una lista donde guardar las coordenadas
        CantDiv = DO_Inter.length[c]/Div       # se calcula la cantidad de segmentos que entran en la línea en función de Distancia_entre_puntos
        
        for i in range(int(CantDiv)):          # se itera la cantidad de segmentos
            lista_puntos.append(gpd.GeoDataFrame([DO_Inter.iloc[c]]).interpolate(i*Div))
                 # se calcula la coordenada del puntos sobre la línea c para la longitud dada por el segmento i
                 # a i se lo multiplica por Div, lo que nos da la distancia en grados desde el inicio de la línea
            
        DF1 = pd.DataFrame(lista_puntos)  # pasamos la lista a df
        DF1.rename(columns={ DF1.columns[0]: "geometry" }, inplace = True) # cambiamos el nombre del campo
        DF = pd.concat([DF, DF1])    # unimos el df anterior con el df general

    DF2 = pd.DataFrame(DataOriginal.loc[DataOriginal.Dist < DMP].centroid) # calculamos el centroide para lineas menores a Distancia_entre_puntos
    DF2.rename(columns={DF2.columns[0]: "geometry" }, inplace = True)      # cambiamos el nombre del campo
    DF3 = pd.concat([DF, DF2])      # unimos el df resultante con el obtenido en la iteración anterior 
    
    GDF3 = gpd.GeoDataFrame(DF3, geometry='geometry')
    GDF3.crs = {'init' :'epsg:4326'}
    
    return GDF3


# In[ ]:


# Calculamos la longitud y corremos la función
EspaciosVerdes_lineas_GDF['Dist'] = EspaciosVerdes_lineas_GDF.length
GDF_Lineas_a_Puntos = Lineas_a_Puntos_Intervalo(EspaciosVerdes_lineas_GDF, 50, 100)


# In[ ]:


fig, ax = plt.subplots(figsize=(15,15))
AreaInteres.plot(ax=ax, color='lightgrey')
EspaciosVerdes.plot(ax=ax, color='yellow')
EspaciosVerdes_lineas_GDF.plot(ax=ax, color='green');
GDF_Lineas_a_Puntos.plot(ax=ax, color='red');


# In[ ]:


GDF_Lineas_a_Puntos.to_file(PATH + '/EspaciosVerdes_puntos_' + Ciudad + '.shp')


# ### Le asignamos a cada punto un ID de espacio verde

# In[ ]:


EspaciosVerdes_SJ = EspaciosVerdes.loc[:,['leisure', 'name', 'osm_type', 'full_id', 'osm_id', 'geometry']]
EspaciosVerdes_SJ['geometry'] = EspaciosVerdes_SJ.geometry.buffer(1.0457242224755355e-05)
EspaciosVerdes_SJ.head(3)


# In[ ]:


GDF_Lineas_a_Puntos.reset_index(inplace=True)
GDF_Lineas_a_Puntos.reset_index(inplace=True)
GDF_Lineas_a_Puntos.head()


# In[ ]:


GDF_Lineas_a_Puntos_ID = gpd.sjoin(GDF_Lineas_a_Puntos, EspaciosVerdes_SJ, how="left", op='intersects')


# In[ ]:


GDF_Lineas_a_Puntos_ID.rename(columns={ GDF_Lineas_a_Puntos_ID.columns[0]: "ID_Gen" , GDF_Lineas_a_Puntos_ID.columns[1]: "ID_Linea" }, inplace = True)
GDF_Lineas_a_Puntos_ID.drop(columns = 'index_right', inplace=True)
GDF_Lineas_a_Puntos_ID.head()


# In[ ]:


GDF_Lineas_a_Puntos_ID = GDF_Lineas_a_Puntos_ID.drop_duplicates(subset='ID_Gen', keep="first")
len(GDF_Lineas_a_Puntos_ID)


# In[ ]:


GDF_Lineas_a_Puntos_ID.to_file(PATH + '/EspaciosVerdes_puntos_ID_' + Ciudad + '.shp')


# <a id='section6'></a>
# 
# <div style="border-bottom:1px solid #000;"> 
# <div align="center"><h2>Calcular distancias más cercana</h2></div>
# <div align="right">(volver a <a href='#indice'><b>Indice</b></a>)</div>
# </div>

# In[ ]:


# EPV_ , EPV_datos = anapos.cercania(Zonas, 'ZONA', 'geometry', GDF_Lineas_a_Puntos_ID, 'ID_Gen', 'geometry', 3, centroid_origen=True, max_distancia=300)


# In[ ]:




