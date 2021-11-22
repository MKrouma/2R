"""dockstring
"""

# import
import os
import folium
import pandas as pd
import geopandas as gpd
import openrouteservice as ors
from IPython.display import display
from shapely.geometry import Point, LineString, Polygon

# openrouteservices 
client = ors.Client(key='5b3ce3597851110001cf62485169f9e2d05c419eaf0607fe2b5b0bfa')

# input coordinates
coordinates = [[2.3668617010116577,48.86100925394748 ], [2.4125343561172485, 48.83392954811057]]

#requete openrouteservice
route = client.directions(
    coordinates=coordinates,
    profile='cycling-regular',
    format ='geojson',
    units ='km'
)

# get clusters


# localisation Paris
m = folium.Map(location=[48.862, 2.346], tiles='cartodbpositron', zoom_start=13)
folium.PolyLine(locations=[list(reversed(coord)) 
                           for coord in 
                           route['features'][0]['geometry']['coordinates']]).add_to(m)
    
m.save("./templates/map.html")


