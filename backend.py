"""docstring to make pylint happy
"""

import os
import folium
import glob
import pyproj
import pandas as pd
import geopandas as gpd
import plotly_express as px
from datetime import datetime, date
import openrouteservice as ors
import matplotlib.pyplot as plt
from shapely.ops import transform
from IPython.display import display
from geopy.geocoders import Nominatim
from shapely.geometry import Point, LineString, Polygon

def addresses_to_coords(address_from, address_to) :

    # geocode addresses
    geolocator = Nominatim(user_agent="app")

    # coords from
    coords_from = [geolocator.geocode(address_from).longitude, 
                    geolocator.geocode(address_from).latitude]

    # coords_to
    coords_to = [geolocator.geocode(address_to).longitude, 
                geolocator.geocode(address_to).latitude]

    # put in coordinates
    coordinates = [coords_from, coords_to]
    return coordinates


def coords_to_geodataframe(coords) :
    
    # get direction with ors
    # openrouteservices 
    client = ors.Client(key='5b3ce3597851110001cf62485169f9e2d05c419eaf0607fe2b5b0bfa')

    #requete openrouteservice
    route = client.directions(
        coordinates=coords,
        profile='cycling-regular',
        format ='geojson',
        units ='km'
    )

    # user route to df
    user_line_coords = route['features'][0]['geometry']['coordinates']
    user_line_df = pd.DataFrame(user_line_coords,
                                columns=["lon", "lat"])

    # df to gdf
    user_line_gdf = gpd.GeoDataFrame(user_line_df, 
                        geometry=gpd.points_from_xy(user_line_df.lon, user_line_df.lat),
                        crs="epsg:4326")

    # return 
    return user_line_gdf, user_line_coords


def load_cluster_polygons(cluster_poly_file, buffer_in_m) :

    # get clusters
    gdf_cluster = gpd.read_file(cluster_poly_file)

    # clusters with buffer
    orig_crs = 4326
    fr_crs = 2154
    gdf_cluster = gdf_cluster.to_crs(epsg=fr_crs)

    # add buffer
    gdf_cluster['geometry'] = gdf_cluster.geometry.buffer(buffer_in_m)

    # set crs to wgs84
    gdf_cluster = gdf_cluster.to_crs(epsg=orig_crs)

    return gdf_cluster.copy()
    

def cluster_signale(user_line_gdf, gdf_cluster) :
    # intersect : spatial join
    cluster_on_route = gpd.sjoin(gdf_cluster, user_line_gdf)[gdf_cluster.columns]

    # display
    # print(f"{len(set(cluster_on_route))} clusters on user direction.")
    # display(cluster_on_route.sample(2))

    # return 
    return cluster_on_route


def map_config(gdf, scale=15) :

    # get centroid
    user_route_centroid = gdf.copy().geometry.unary_union.centroid

    # map center
    c_lon = round(user_route_centroid.x,5)
    c_lat = round(user_route_centroid.y,5)

    # map scale
    scale = scale

    # tile
    tile = 'cartodbpositron'

    # config
    config = {
        "c_lon" : c_lon,
        "c_lat" : c_lat, 
        "scale" : scale, 
        "tile" : tile
    }
    return config 


def plot_geosignale(user_line_coords, cluster_on_route, gdf_cluster, config) :

    # get map configurations
    c_lon = config["c_lon"]
    c_lat = config["c_lat"]
    scale = config["scale"]
    tile = config["tile"]

    # init folium map
    m = folium.Map(location=[c_lat, c_lon], tiles=tile, zoom_start=scale)

    # all cluster on map
    gdf = gdf_cluster.copy()
    for _, r in gdf.iterrows():
        # Without simplifying the representation of each borough,
        # the map might not be displayed
        sim_geo = gpd.GeoSeries(r['geometry']).simplify(tolerance=0.001)
        geo_j = sim_geo.to_json()
        geo_j = folium.GeoJson(data=geo_j,
                               style_function=lambda x: 
                               {'fillColor': '#669bbc',
                                'color': '#669bbc',
                                'weight':4,
                                'stroke':False}
        )
        
        text = f"""Nombre d'accidents : {r['n_accidents']}"""
        folium.Popup(text, min_width=100, max_width=150).add_to(geo_j)
        geo_j.add_to(m)

    # cluster intersection map
    gdf = cluster_on_route
    for _, r in gdf.iterrows():
        # Without simplifying the representation of each borough,
        # the map might not be displayed
        sim_geo = gpd.GeoSeries(r['geometry']).simplify(tolerance=0.001)
        geo_j = sim_geo.to_json()
        geo_j = folium.GeoJson(data=geo_j,
                            style_function=lambda x: 
                            {'fillColor': '#eb353c',
                                'color': '#eb353c',
                                'weight':5,
                                'stroke':False,
                                'opacity':1}
        )
        
        text = f"""Indice cluster: {r['cluster_index']}<br>Nombre d'accidents : {r['n_accidents']}"""
        folium.Popup(text, min_width=100, max_width=150).add_to(geo_j)
        geo_j.add_to(m)
        
    # add user itinerary polyline
    folium.PolyLine(locations=[list(reversed(coord)) 
                            for coord in user_line_coords],
                            color = '#84dcc6',
                            smooth_factor=0.9,
                            weight = 4
    ).add_to(m)

    # export map
    signale_map = "./templates/map.html"
    if os.path.exists(signale_map) :
        m.save(signale_map)

    #display(m)


def geofencing(user_gdf, cluster_gdf) : 

    ## GEOFENCING
    # add time field in user route 
    pip_mask_geofence = user_gdf.copy().intersects(cluster_gdf.unary_union)

    # geofence column
    user_gdf["geofence"] = pip_mask_geofence

    # add time
    number_of_points = user_gdf.shape[0]
    start_date = datetime(2021, 11, 22, 12, 10)
    date_range = pd.date_range(start=start_date, periods=number_of_points) #, freq="min"

    # time column
    user_gdf["time"] = date_range

    # transform time format to string for geofencing animation
    user_gdf["time"] = user_gdf["time"].apply(lambda x: x.strftime('%Y-%m-%d')) #-%H:%M


    # replace gepfencing by In and Out
    user_gdf["geofence"] = user_gdf["geofence"].replace({True: "Out", False: "In"})

    # size
    user_gdf["track_id"] = user_gdf["geofence"].apply(lambda x : 0.5 if x=="In" else 0.5)
    display(user_gdf.sample(2))
    return user_gdf, date_range


def manage_iframe(clean_dir=False) : 
    """ copy recent iframe html as geofencing.html
    """
    # read recent file
    iframe_dir = "./iframe_figures"
    iframe_html_files = "./iframe_figures/*html"
    files = glob.glob(iframe_html_files)
    try : 
        recent_file = max(files, key=os.path.getctime)

        # copy to template as geofencing.html
        cmd_copy_iframe_html = f"cp {recent_file} ./templates/geofencing.html"
        os.system(cmd_copy_iframe_html)

        # clean ifram dir
        if clean_dir : 
            cmd_clean_iframe_dir = f"cd {iframe_dir} && rm *"
            os.system(cmd_clean_iframe_dir)
            recent_file

    except :
        pass


def plot_geofencing(gdf, config, token) :

    # map config
    geofence_map_center = {
        "lat" : config["c_lat"],
        "lon": config["c_lon"]
    }

    scale = config["scale"] - 2
    px.set_mapbox_access_token(token)

    # geofencing animation
    fig_3 = px.scatter_mapbox(
        gdf, 
        lat="lat", 
        lon="lon", 
        color="geofence", 
        animation_frame="time", 
        # size="track_id",
        size_max=100, 
        zoom=scale, 
        width=1200, 
        height=750,
        center=geofence_map_center
    )
    fig_3.show(renderer="iframe")

    # copy iframe to template
    manage_iframe()


def run(addr_from, addr_to, log=False) :
    """automate backend process
    """

    # print
    print("Backend : geofencing project.\n\n")

    # addresses to coords
    coordinates = addresses_to_coords(addr_from, addr_to)

    ## coords to geodataframe
    user_line_gdf, user_line_coords = coords_to_geodataframe(coordinates)

    ## load cluster polygons
    buffer_in_m = 10
    cluster_polygons_file = "./model/model_cluster/cluster_polygons.geojson"
    gdf_cluster = load_cluster_polygons(cluster_polygons_file, buffer_in_m)
    
    ## fetch cluster on user direction
    cluster_on_route = cluster_signale(user_line_gdf.copy(), gdf_cluster.copy())

    ## set map configurations
    scale = 14
    m_config = map_config(user_line_gdf, scale)
    
    ## plot geo signalization 
    plot_geosignale(user_line_coords, cluster_on_route, gdf_cluster, m_config)

    ## arrange data for geofencing 
    user_geofence_gdf, date_range = geofencing(user_line_gdf.copy(), gdf_cluster.copy())
    
    # plot geofencing
    mapbox_token = "pk.eyJ1Ijoic2hha2Fzb20iLCJhIjoiY2plMWg1NGFpMXZ5NjJxbjhlM2ttN3AwbiJ9.RtGYHmreKiyBfHuElgYq_w"
    plot_geofencing(user_geofence_gdf, m_config, mapbox_token)

    if log : 
        print("\naddresses to coordinates :")
        display(coordinates)

        print("\ncoords to geodataframe :")
        display(user_line_gdf.sample(2))

        print("\nload cluster polygons :")
        display(gdf_cluster.sample(2))

        print("\nfetch clusters on user direction:\n")
        
        print("set map configurations:")
        display(m_config)

        print("\nplot geo signalization:\n")

        print("arrange data for geofencing :\n")
        display(user_geofence_gdf.sample(2))

        print("\nplot geofencing:\n")

        print("done - whoops !")


if __name__ == "__main__" :
    pass
    # address_from = "55 Rue du Faubourg Saint-Honoré, 75008 Paris"
    # address_to = "12 Rue Olivier Métra, 75020 Paris"
    # run(address_from, address_to, log=True)


