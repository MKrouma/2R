# geomery
geom = route['features'][0]['geometry']['coordinates']

# geom_df
geom_df = pd.DataFrame(geom, columns=["lon", "lat"])
geom_gdf = gpd.GeoDataFrame(geom_df, 
                        geometry=gpd.points_from_xy(geom_df.lon, geom_df.lat),
                        crs="epsg:4326")

# create linestring
list_geometry = geom_gdf["geometry"].to_list()
geom_ls = None
for point in list_geometry : 
    if list_geometry.index(point) == 0 :
        geom_ls = LineString(point.coords[:] + point.coords[:])

    else : 
        geom_ls = LineString(geom_ls.coords[:] + point.coords[:])


# display
display(geom_ls)