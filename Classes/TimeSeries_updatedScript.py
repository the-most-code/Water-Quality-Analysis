# -*- coding: utf-8 -*-
"""
Created on Thu Oct 20 11:03:20 2022

@author: Tano_E
"""

import IWRPull as LA
import Plotting as pltng
import pandas as pd

#wbid_input = arcpy.GetParameterAsText(0)
wbid_input = "3002G"
wbid_input = wbid_input.split(", ")
wbid = [x.strip() for x in wbid_input]

#arcpy.GetParameterAsText(1)
datatype = 'AGMs'

#arcpy.GetParameterAsText(2)
lakeWatch = 'No'

#mastercode = arcpy.GetParameterAsText(3)
mastercode = 'Nutrients'

#param_sel = arcpy.GetParameterAsText(4)
param_sel = "TN;TP" # this is fed into bokeh
param_split = param_sel.split(";")
param_list = [i.strip() for i in param_split]
param = str(param_list)[1:-1]

#start_yr = arcpy.GetParameterAsText(5)
start_yr = 2000

try:
    start_yr = int(str(start_yr).strip())
except:
    start_yr = 2000
    
#folder_loc = arcpy.GetParameterAsText(6)
folder_loc =  r'C:\development_2\toolRuns\test_eric\multiple_tables\timeseries'

# i dont have to code in the validation here
# if someone selects bacteria only show AGMs as an option to select 
for w in wbid:
    
    water = LA.dataPull(w, start_yr, str(param))
    # Plot
    plt = pltng.Visualization(w)
    plt.outputLocation(folder_loc, "_TimeSeries_" + str(datatype) + ".html")
    
    if datatype == 'Raw Data':
        # pulling rawdata
        df = water.rawData(lakeWatch = 'No')
        x_axis = 'Date'
        fig = plt.TimeSeriesPlot(w, df, x_axis, param_list, datatype)

    elif datatype == 'AGMs':
        df = water.qaFiltered(lakeWatch = 'No')
        x_axis = 'YEAR'
        df = df.reset_index(drop=True)
        df['YEAR'] = pd.to_datetime(df['YEAR'], format='%Y')
        # df = ColumnDataSource(df)
        fig = plt.TimeSeriesPlot(w, df, x_axis, param_list, datatype)
        
    elif datatype == 'Both':
        df_raw = water.rawData(lakeWatch)
        df_AGM = water.qaFiltered(lakeWatch = 'No')
    plt.columnPlots(fig)
    plt.savePlot(fig)
    
        
        

