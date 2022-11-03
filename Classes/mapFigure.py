# -*- coding: utf-8 -*-
"""
Created on Wed Oct 26 15:45:41 2022

@author: Tano_E
"""
import geopandas as gpd
import json
# import xyzservices.providers as xyz

from bokeh.plotting import save, figure, show
from bokeh.models import GeoJSONDataSource, LinearColorMapper, ColorBar, HoverTool
from bokeh.palettes import brewer
from bokeh.tile_providers import ESRI_IMAGERY, OSM, get_provider


tile_provider = get_provider(ESRI_IMAGERY)

loading = r'C:\development_2\toolRuns\test_eric\multiple_tables\dashboard\PLSM_shapefiles\landuse_dissolveLTA_Loading.shp'
wbid =  r'C:\development_2\toolRuns\test_eric\multiple_tables\dashboard\Lake Lotta Wbid.shp'

# read the data
SHP = gpd.read_file(loading)
w = gpd.read_file(wbid)
# print(SHP)

SHP = SHP.to_crs(epsg=3857)
w = w.to_crs(epsg=3857)

load_json = json.loads(SHP.to_json())
load_wbid = json.loads(w.to_json())

json_data = json.dumps(load_json)
json_wbid = json.dumps(load_wbid)

geosource = GeoJSONDataSource(geojson = json_data)
wbid_geo = GeoJSONDataSource(geojson = json_wbid)

palette = brewer['OrRd'][8]
palette = palette[::-1]
color_mapper = LinearColorMapper(palette= palette)
color_bar = ColorBar(color_mapper= color_mapper)
hover = HoverTool(tooltips= [('Landuse', '@LEVEL2_L_1'), ('TN Kg/Acre', '@TN_Acre')])

TOOLS = "pan,wheel_zoom,reset,save"

LTA_map = figure(title= 'LTA Level 2 Landuse Loading TN Kg/Acre', tools=[hover, TOOLS],
                 x_axis_type="mercator", y_axis_type="mercator")
LTA_map.add_tile(tile_provider)
LTA_map.add_layout(color_bar, 'below')

LTA_map.patches(source=wbid_geo, fill_color = 'blue', line_color='black', line_width= 1)
LTA_map.patches(source=geosource, fill_color = {'field':'TN_Acre', 'transform':color_mapper}, \
                line_color='black', line_width= 1)
LTA_map.grid.grid_line_color = None
LTA_map.axis.visible = False

show(LTA_map)