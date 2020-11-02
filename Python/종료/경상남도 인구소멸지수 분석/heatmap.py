'''
    @Filename | heatmap.py
    @Author   | SoongFish
    @Date     | 2020.10.19. ~ 2020.10.30.
    @Desc     | Visualize GSND population, Extinction Risk on map
'''

import folium as fo
import numpy as np
import pandas as pd
import json
import webbrowser
from folium import plugins
from folium.plugins import HeatMap

# settings
EMD_geo = 'GSND_EMD.geojson'
ingudata = pd.read_csv('GSND_EMD_INGU.csv', encoding = 'cp949')

map = fo.Map(location = [36.5, 127.4], tiles = 'OpenStreetMap', zoom_start = 7)

map_ingu = fo.FeatureGroup(name = '인구').add_to(map)
map_circle = fo.FeatureGroup(name = '원', show = False).add_to(map)
map_heatmap = fo.FeatureGroup(name = '인구 히트맵', show = False).add_to(map)
map_SMGS = fo.FeatureGroup(name = '소멸지수 히트맵', show = False).add_to(map)

fo.Choropleth( 
    geo_data = EMD_geo,
    name = '인구',
    data = ingudata,
    columns = ['코드', '총인구수'],
    key_on = 'feature.properties.adm_cd2',
    fill_color = 'BuPu',
    fill_opacity = 0.6,
    line_opacity = 0.5,
    legend_name = '인구수').add_to(map)

# Circle
for i in range(0, len(ingudata)):
    x = ingudata.iloc[i]['위도']
    y = ingudata.iloc[i]['경도']
    CM = (x, y)
    fo.CircleMarker(CM, radius = ingudata.iloc[i]['총인구수']/2500, color = '#3186cc', fill_color = '#3186cc', popup = (ingudata.iloc[i]['행정구역'], ingudata.iloc[i]['총인구수'])).add_to(map_circle)

# Heatmap_Population
heat_df = ingudata[['위도', '경도', '총인구수']]
heat_data = [[row['위도'], row['경도'], int(row['총인구수'])/500] for index, row in heat_df.iterrows()]

HeatMap(heat_data, radius = 30).add_to(map_heatmap)

# Heatmap_SMGS
heat_df = ingudata[['위도', '경도', '소멸지수']]
heat_data = [[row['위도'], row['경도'], (float(row['소멸지수']-1))*(-200)] for index, row in heat_df.iterrows()]

HeatMap(heat_data, radius = 30).add_to(map_SMGS)

# Combine
fo.LayerControl().add_to(map)
map.save('gdTest.html') 
webbrowser.open('gdTest.html')