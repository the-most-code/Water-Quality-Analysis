# -*- coding: utf-8 -*-
"""
Created on Fri Oct 21 15:52:21 2022

@author: Tano_E
"""

import IWRPull as LA
import Plotting as pltng
#import pandas as pd

#wbid_input = arcpy.GetParameterAsText(0)
wbid_input = "3002G"
wbid_input = wbid_input.split(", ")
wbid = [x.strip() for x in wbid_input]

#arcpy.GetParameterAsText(1)
y_axis_select = 'CHLAC'

#arcpy.GetParameterAsText(2)
datatype = 'AGMs'

#arcpy.GetParameterAsText(3)
lakeWatch = 'No'

#param_sel = arcpy.GetParameterAsText(4)
param_sel = "TN;TP" # this is fed into bokeh
param_split = param_sel.split(";")
param_list = [i.strip() for i in param_split] 
param_list.append(str(y_axis_select)) #append CHLAC string into this list before sql query
param = str(param_list)[1:-1]

#start_yr = arcpy.GetParameterAsText(5)
start_yr = 2000

try:
    start_yr = int(str(start_yr).strip())
except:
    start_yr = 2000
    
#folder_loc = arcpy.GetParameterAsText(6)
folder_loc =  r'C:\development_2\toolRuns\test_eric\multiple_tables\xyplots'


for w in wbid:
    water = LA.dataPull(w, start_yr, str(param))
    # plot
    plt = pltng.Visualization(w)
    plt.outputLocation(folder_loc, "_XY_" + str(datatype) + ".html")
    
    if datatype == 'Raw Data':
        df =  water.rawData(lakeWatch = 'No')
        fig = plt.XYPlot(w, df, param_split, y_axis_select, datatype)
        
    elif datatype == 'AGMs':
        df = water.qaFiltered(lakeWatch = 'No')
        fig = plt.XYPlot(w, df, param_split, y_axis_select, datatype)
    
    elif datatype == 'Both':
        df_raw = water.rawData(lakeWatch)
        df_AGM = water.qaFiltered(lakeWatch = 'No')
    plt.columnPlots(fig)
    plt.savePlot(fig)       
    
        

        


















