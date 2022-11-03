# -*- coding: utf-8 -*-
"""
Created on Wed Oct 12 16:24:32 2022

@author: Tano_E
"""


import pandas as pd
import scipy
from scipy.stats.mstats import gmean
import math
from math import sqrt
from math import exp
import numpy as np

# import os.path
import os
import geopandas as gpd
import json


import bokeh
import bokeh.layouts
from bokeh.models import ColumnDataSource, GeoJSONDataSource, LinearColorMapper, ColorBar, HoverTool, Legend
from bokeh.io import save, output_file, show
from bokeh.plotting import figure

from bokeh.plotting import save, figure, show
from bokeh.palettes import brewer
from bokeh.tile_providers import ESRI_IMAGERY, OSM, get_provider
from bokeh.layouts import column, row
from bokeh.models import Panel, Tabs


# import pandas_bokeh

class Visualization:

    def __init__(self, wbid,
                 Title_dict = {'TN': 'Total Nitrogen', 'TP': 'Total Phosphorus', 'CHLAC': 'Chlorophyll-a',
                               'FCOLI': 'Fecal Coliform', 'ECOLI': 'Escherichia coli', 'ENCOC': 'Enterococci',
                               'PB': 'Lead', 'CU': 'Copper', 'FE': 'Iron'},
                 Label_dict = {'TN': 'Total Nitrogen (mg/L)', 'TP': 'Total Phosphorus (mg/L)', 'CHLAC': 'Chlorophyll-a (μg/L)',
                               'FCOLI': 'Fecal Coliform (cfu/100mL)', 'ECOLI': 'Escherichia coli (cfu/100mL)', 'ENCOC': 'Enterococci (cfu/100mL)',
                               'PB': 'Lead (g/L)', 'CU': 'Copper (g/L)', 'FE': 'Iron (g/L)'}):
        self.w = wbid
        self.Title_dict = Title_dict
        self.Label_dict = Label_dict

    def outputLocation(self, folder_loc, plotnameString):
        dir = folder_loc + '\html_files'
        if not os.path.exists(dir):
            os.makedirs(dir)
        return output_file(folder_loc + "\\html_files\\" + str(self.w) + plotnameString, title= "WBID " + str(self.w))

    def NonH1Plot(self, w, df, clr_type, xVar, NNC_derivation):
        plot_list = []

        for p in xVar:
            df = df.reset_index(drop=True)
            df['YEAR'] = pd.to_datetime(df['YEAR'], format= '%Y')
            CDS1 = df

            fig = figure(x_axis_type = "log", y_axis_type= "log", plot_width=1200, plot_height=600,
                                  title = 'WBID ' + str(self.w) + ' ' + str(self.Title_dict.get(str(p))) + ' vs ' + str(self.Title_dict.get("CHLAC")))
            scatt = fig.scatter(str(p), "CHLAC", source = CDS1, fill_alpha=0.6, fill_color= 'red', size = 8)
            fig.add_tools(HoverTool(renderers=[scatt], tooltips=[(str(self.w), '@'+ str(p))]))

            fig.x(NNC_derivation[str(p) + '_' + str(clr_type)], NNC_derivation['CHLA_' + str(clr_type)], fill_alpha= 0.6, line_color='grey', size = 8,
                                    legend_label= 'NNC Derivation ' + str(clr_type) + ' Data')

            fig.line(NNC_derivation[str(p) + '_AGMs_' + str(clr_type)], NNC_derivation[str(p) + '_Upper_' + str(clr_type)], line_dash = 'dashed')
            fig.line(NNC_derivation[str(p) + '_AGMs_' + str(clr_type)], NNC_derivation[str(p) + '_Predicted_' + str(clr_type)], line_dash = 'solid', line_color= 'black')
            fig.line(NNC_derivation[str(p) + '_AGMs_' + str(clr_type)], NNC_derivation[str(p) + '_Lower_' + str(clr_type)],line_dash = 'dashed')

            fig.title.align = 'center'
            fig.title.text_font_size = '16pt'
            fig.yaxis.axis_label = str(self.Label_dict.get("CHLAC"))
            fig.yaxis.axis_label_text_font_size = "12pt"
            fig.yaxis.major_label_text_font_size = "12pt"
            fig.xaxis.axis_label = str(self.Label_dict.get(str(p)))
            fig.xaxis.axis_label_text_font_size = "12pt"
            fig.xaxis.major_label_text_font_size = "12pt"
            fig.axis.axis_label_text_font_style = 'bold'

            # legend alteration
            fig.legend.location = 'top_left'
            fig.legend.click_policy = 'hide'

            plot_list.append(fig)
        plots = column(*plot_list)
        return plots

    def TimeSeriesPlot(self, w, df, x_axis, param_list, dataString):
        plot_list = []
        
        for p in param_list:
            
            fig = figure(x_axis_type="datetime", plot_width=1200, plot_height=600, \
                         title= str(self.Title_dict.get(str(p))) + ' ' + dataString)
            fig.sizing_mode = 'scale_width'
            circ = fig.circle(source=df, x= x_axis, y= str(p), fill_color= 'lightblue', size=8, legend_label = str(p), muted_alpha=0.3)
            fig.add_tools(HoverTool(renderers=[circ], tooltips=[(self.w, '@' + str(p))]))

            fig.background_fill_color = 'beige'
            fig.grid.grid_line_color = None

            fig.title.align = 'center'
            fig.title.text_font_size = '16pt'
            fig.yaxis.axis_label = str(self.Label_dict.get(str(p)))
            fig.yaxis.axis_label_text_font_size = "12pt"
            fig.yaxis.major_label_text_font_size = "12pt"
            fig.xaxis.axis_label = x_axis
            fig.xaxis.axis_label_text_font_size = "12pt"
            fig.xaxis.major_label_text_font_size = "12pt"
            fig.axis.axis_label_text_font_style = 'bold'
            
            fig.legend.visible = False
            
            plot_list.append(fig)
        
        return plot_list
        
    def XYPlot(self, w, df, param_list, y_axis_select, R_squared, y_predicted, x, slope, intercept, dataString):
        plot_list = []
        
        for p in param_list:

            
            fig = figure(plot_width=1200, plot_height=900, title = str(self.Title_dict.get(str(p))) + ' vs ' + \
                         str(self.Title_dict.get(y_axis_select)) + ' ' + dataString)
            fig.sizing_mode = 'scale_width'
            scatt = fig.scatter(str(p), y_axis_select, source = df, fill_alpha=0.6, fill_color= 'red', size= 8)
            fig.add_tools(HoverTool(renderers=[scatt], tooltips=[(self.w, '@' + str(p))]))
            fig.line(x[str(p)], y_predicted[str(p)], line_width= 2, line_color='orange', 
                      legend_label = 'y='+ str(round(slope, 2)) + 'x + ' + str(round(intercept, 2)) + ', R-squared:' + str(R_squared))
        
            # Edit title and axes
            fig.background_fill_color = 'beige'
            fig.grid.grid_line_color = None

            fig.title.align = 'center'
            fig.title.text_font_size = '16pt'
            fig.yaxis.axis_label = str(self.Label_dict.get(y_axis_select))
            fig.yaxis.axis_label_text_font_size = "12pt"
            fig.yaxis.major_label_text_font_size = "12pt"
            fig.xaxis.axis_label = str(self.Label_dict.get(str(p)))
            fig.xaxis.axis_label_text_font_size = "12pt"
            fig.xaxis.major_label_text_font_size = "12pt"
            fig.axis.axis_label_text_font_style = 'bold'

            #fig.legend.click_policy = 'mute'
            
            plot_list.append(fig)
        
        return plot_list
    
    def mapFigure(self, landuse, wbid, param_list):
        plot_list = []
        
        tile_provider = get_provider(ESRI_IMAGERY)

        # read the data
        SHP = gpd.read_file(landuse)
        w = gpd.read_file(wbid)
        # print(SHP)

        SHP = SHP.to_crs(epsg=3857)
        w = w.to_crs(epsg=3857)

        load_json = json.loads(SHP.to_json())
        load_wbid = json.loads(w.to_json())

        json_data = json.dumps(load_json)
        json_wbid = json.dumps(load_wbid)

        wtshed_geo = GeoJSONDataSource(geojson=json_data)
        wbid_geo = GeoJSONDataSource(geojson=json_wbid)
        
        palette = brewer['OrRd'][8]
        palette = palette[::-1]
        color_mapper = LinearColorMapper(palette= palette, low=0)
        color_bar = ColorBar(color_mapper= color_mapper)
        TOOLS = "pan,wheel_zoom,reset,save"
        
        for p in param_list:
            hover = HoverTool(tooltips= [('Landuse', '@LEVEL2_L_1'), (str(p) + ' Kg/Acre', '@' + str(p) + '_Acre')])
            
            LTA_map = figure(height=600, width=1200, title= 'Long Term Average Level 2 Loading ' + str(p) + ' Kg/Acre', tools=[hover, TOOLS],
                             x_axis_type="mercator", y_axis_type="mercator")
            LTA_map.add_tile(tile_provider)
            LTA_map.add_layout(color_bar, 'below')
            LTA_map.patches(source=wbid_geo, fill_color = 'blue', line_color='black', line_width= 1)
            LTA_map.patches(source=wtshed_geo, fill_color = {'field': str(p) + '_Acre', 'transform':color_mapper},
                            line_color='black', line_width= 1)
            LTA_map.grid.grid_line_color = None
            LTA_map.axis.visible = False
            
            LTA_map.title.align = 'center'
            LTA_map.title.text_font_size = '16pt'
        
            plot_list.append(LTA_map)
            
        return plot_list

           
    def columnPlots(self, plot_list):
        plots = column(*plot_list)
        plots.sizing_mode = 'scale_width'
        return plots  
    
    def rowPlots(self, plot_list):
        plots = row(*plot_list)
        plots.sizing_mode = 'scale_width'
        return plots 
              
    def savePlot(self, plots):
        save(plots)
        
    def buildDashboard(self, plots):
        plots.sizing_mode = 'scale_width'
        return plots                
    
    def createPanel(self, tab, tabName):
        tab = Panel(child= tab, title= tabName)
        return tab
        
    def createTabs(self, panels, stringLocation):
        tabs = Tabs(tabs=panels, tabs_location= stringLocation)
        return tabs
        
    
        
        
        
        
        
        
        
        
        
        
        
        

