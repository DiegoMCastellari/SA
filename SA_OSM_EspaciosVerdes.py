#!/usr/bin/env python
# coding: utf-8

# In[1]:


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


# # Definir ciudad y paths

# In[2]:


# Ciudad de Estudio
Ciudad = 'BuenosAires'

# Path general de la Carpeta (donde se guardarán los resultados)
PATH = 'D:/JOB/SA/EPV_Ciudades/EPV_BuenosAires/'

# Path a los distintos SHPs
Path_AreaInteres = PATH + 'AreaInteres/Conurbano_2D.shp'
Path_Parques = 'D:/JOB/SA/SHP/OSM/EspacioVerdePúblico/OSM_Parks.shp'
Path_Reservas = 'D:/JOB/SA/SHP/OSM/EspacioVerdePúblico/OSM_NatureReserve.shp'
Path_Radios = PATH + 'Radios BA/radios_zonas_amba.shp'
Path_Zonas = PATH + 'Radios BA/zonas_amba.shp'


# # Carga de datos

# In[3]:


AreaInteres = gpd.read_file(Path_AreaInteres)
AreaInteres.head(3)


# In[4]:


Parques = gpd.read_file(Path_Parques)
Parques.head(3)


# In[5]:


Reservas = gpd.read_file(Path_Reservas)
Reservas.head(3)


# In[6]:


Zonas = gpd.read_file(Path_Zonas)
Zonas.head(3)


# # Parques

# In[7]:


Parque_Conurbano = gpd.overlay(Parques, AreaInteres, how='intersection')
Parque_Conurbano.head(3)


# In[9]:


# conda install -c conda-forge descartes


# In[10]:


fig, ax = plt.subplots(figsize=(15,15))
AreaInteres.plot(ax=ax, color='lightgrey')
Parque_Conurbano.plot(ax=ax, color='green');


# # Reserva Natural

# In[11]:


Reservas_Conurbano = gpd.overlay(Reservas, AreaInteres, how='intersection')
Reservas_Conurbano.head(3)


# In[12]:


fig, ax = plt.subplots(figsize=(15,15))
AreaInteres.plot(ax=ax, color='lightgrey')
Parque_Conurbano.plot(ax=ax, color='green')
Reservas_Conurbano.plot(ax=ax, color='yellow');


# # Unimos Parques y Reservas

# In[13]:


EspaciosVerdes = gpd.GeoDataFrame(pd.concat([Parque_Conurbano, Reservas_Conurbano], ignore_index=True))
EspaciosVerdes.head(3)


# In[14]:


fig, ax = plt.subplots(figsize=(15,15))
AreaInteres.plot(ax=ax, color='lightgrey')
EspaciosVerdes.plot(ax=ax, color='green');


# In[15]:


EspaciosVerdes.to_file(PATH + '/EspaciosVerdes_' + Ciudad + '.shp')


# # Poligonos de Espacios Verdes a Linea

# In[16]:


# Generamos un gdf los EVP como líneas
EspaciosVerdes_lineas = pd.DataFrame(EspaciosVerdes.boundary)
EspaciosVerdes_lineas.rename(columns={ EspaciosVerdes_lineas.columns[0]: "geometry" }, inplace = True)

EspaciosVerdes_lineas_GDF = gpd.GeoDataFrame(EspaciosVerdes_lineas, geometry='geometry')


# In[17]:


fig, ax = plt.subplots(figsize=(15,15))
AreaInteres.plot(ax=ax, color='lightgrey')
EspaciosVerdes_lineas_GDF.plot(ax=ax, color='green');


# In[16]:


# Guardamos el gdf como SHP
EspaciosVerdes_lineas_GDF.to_file(PATH + '/EspaciosVerdes_lineas_' + Ciudad + '.shp')


# # Puntos sobre Perímetro de Polígonos

# In[18]:


# Función que devuelve puntos sobre las líneas a una distancia especificada. Si el perímetro es inferior al doble de 
# esta distancia, se calcula el centroide de la línea.-

def Lineas_a_Puntos(DataOriginal, Distancia_entre_puntos):
    
    Inter = Distancia_entre_puntos
    Div = Inter * 1.0457242224755355e-05     # distancia en grados

    DO_Inter = DataOriginal.loc[DataOriginal.Dist > 2*Div]   # lineas con una longitud mayor a Distancia_entre_puntos
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

    DF2 = pd.DataFrame(DataOriginal.loc[DataOriginal.Dist < 2*Div].centroid) # calculamos el centroide para lineas menores a Distancia_entre_puntos
    DF2.rename(columns={DF2.columns[0]: "geometry" }, inplace = True)      # cambiamos el nombre del campo
    DF3 = pd.concat([DF, DF2])      # unimos el df resultante con el obtenido en la iteración anterior 
    
    return DF3


# In[19]:


# Cargamos EPV como líneas y calculamos la longitud
LineasEPV = gpd.read_file(PATH + '/EspaciosVerdes_lineas_' + Ciudad + '.shp')
LineasEPV['Dist'] = LineasEPV.length
LineasEPV.head(3)


# In[20]:


# Corremos la función
DF_Lineas_a_Puntos = Lineas_a_Puntos(LineasEPV, 50)


# In[63]:


# Pasamos el DF a GDF
GDF_Lineas_a_Puntos = gpd.GeoDataFrame(DF_Lineas_a_Puntos, geometry='geometry')


# In[40]:


# Ploteamos para ver el resultado
fig, ax = plt.subplots(figsize=(15,15))
LineasEPV.plot(ax=ax, color='red')
GDF_Lineas_a_Puntos.plot(ax=ax, color='green');


# In[29]:


GDF_Lineas_a_Puntos.to_file(PATH + '/EspaciosVerdes_puntos_' + Ciudad + '.shp')


# # Le asignamos a cada punto un ID de espacio verde

# In[33]:


EspaciosVerdes.crs


# In[79]:


EspaciosVerdes_SJ = EspaciosVerdes[['leisure', 'name', 'osm_type', 'full_id', 'osm_id', 'geometry']]
EspaciosVerdes_SJ['geometry'] = EspaciosVerdes_SJ.geometry.buffer(1.0457242224755355e-05)
EspaciosVerdes_SJ.head(3)


# In[82]:


# Ploteamos para ver el resultado
fig, ax = plt.subplots(figsize=(15,15))
EspaciosVerdes_SJ.loc[EspaciosVerdes_SJ.full_id == 'r454902'].plot(ax=ax, color='red')
EspaciosVerdes.loc[EspaciosVerdes.full_id == 'r454902'].plot(ax=ax, color='green');


# In[69]:


GDF_Lineas_a_Puntos.crs = {'init' :'epsg:4326'}


# In[70]:


GDF_Lineas_a_Puntos.crs 


# In[84]:


GDF_Lineas_a_Puntos.reset_index(inplace=True)
GDF_Lineas_a_Puntos.reset_index(inplace=True)


# In[87]:


GDF_Lineas_a_Puntos_ID = gpd.sjoin(GDF_Lineas_a_Puntos, EspaciosVerdes_SJ, how="left", op='intersects')


# In[ ]:


GDF_Lineas_a_Puntos_ID.rename(columns={ GDF_Lineas_a_Puntos_ID.columns[0]: "ID_Gen" , GDF_Lineas_a_Puntos_ID.columns[1]: "ID_Linea" }, inplace = True)
GDF_Lineas_a_Puntos_ID.drop(columns = 'index_right', inplace=True)
GDF_Lineas_a_Puntos.head()


# In[105]:


GDF_Lineas_a_Puntos_ID = GDF_Lineas_a_Puntos_ID.drop_duplicates(subset='ID_Gen', keep="first")


# In[116]:


GDF_Lineas_a_Puntos_ID.to_file(PATH + '/EspaciosVerdes_puntos_ID_' + Ciudad + '.shp')


# # Calcular distancias más cercana

# In[46]:


Zonas.head(3)


# In[117]:


GDF_Lineas_a_Puntos_ID.head(3)


# In[118]:


EPV_ , EPV_datos = anapos.cercania(Zonas, 'ZONA', 'geometry', GDF_Lineas_a_Puntos_ID, 'ID_Gen', 'geometry', 3, centroid_origen=True, max_distancia=300)


# In[ ]:




