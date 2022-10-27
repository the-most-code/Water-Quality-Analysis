# -*- coding: utf-8 -*-
"""
Created on Mon Oct 24 11:27:08 2022

@author: Tano_E
"""

import IWRPull as LA
import Plotting as pltng
import PLSM as plm
import Septic as spc

import pandas as pd
import bokeh
from bokeh.layouts import layout
#from bokeh.io import curdoc

#wbid_input = arcpy.GetParameterAsText(0)
wbid_input = "3002G"
wbid_input = wbid_input.split(", ")
wbid = [x.strip() for x in wbid_input]

#arcpy.GetParameterAsText(1)
y_axis_select = 'CHLAC'


#arcpy.GetParameterAsText(3)
lakeWatch = 'No'

#param_sel = arcpy.GetParameterAsText(4)
param_sel = "TN;TP" # this is fed into bokeh
param_split = param_sel.split(";")
param_list = [i.strip() for i in param_split] 
param_list.append(str(y_axis_select)) 
param = str(param_list)[1:-1] ### this part will need conditions

#start_yr = arcpy.GetParameterAsText(5)
start_yr = 2000

try:
    start_yr = int(str(start_yr).strip())
except:
    start_yr = 2000
    
#folder_loc = arcpy.GetParameterAsText(6)
folder_loc =  r'C:\development_2\toolRuns\test_eric\multiple_tables\dashboard'

watershed_input = r'C:\development_2\toolRuns\test_eric\multiple_tables\dashboard\Lake_lotta_Updated_Watershed.shp'

waterbody_input = r'C:\development_2\toolRuns\test_eric\multiple_tables\dashboard\Lake Lotta Wbid.shp'

rainfall_input = r'C:\development_2\toolRuns\test_eric\multiple_tables\dashboard\Annual_rain_lotta.csv'

people = 3


for w in wbid:
    paramTab = []

    water = LA.dataPull(w, start_yr, str(param))
    plt = pltng.Visualization(w)
    
    plsm = plm.PLSM(watershed_input, rainfall_input, folder_loc)
    rainfall_df = plsm.rainfallQA()
    layer_to_process, temp_folder_path = plsm.Clip('Analysis')
    dissolve_input, n_rows, clip_input = plsm.Dissolve(layer_to_process, temp_folder_path)
    plsm.calculateField(dissolve_input)
    plsm.attribute_to_CSV(dissolve_input, temp_folder_path)
    join1 = plsm.Merge(temp_folder_path, n_rows)

    d = plsm.writeData(rainfall_df, join1)
    lta_initial_df = plsm.ltaLoading(dissolve_input, d)
    
    # Septic functions to get nitrogen
    septic = spc.Septic(watershed_input, waterbody_input, people, folder_loc)
    selectionTanks, temp_folder_path = septic.clipTanks()
    septic_buffer_count = septic.Buffer(selectionTanks, temp_folder_path)
    septic_loading, septic_DF = septic.runCalculation(septic_buffer_count)

    # feed septic output in plsm piechart data
    lvl_LU_df = plsm.lvl_1_landuse(d, clip_input, septic_loading, include_septic=True, remove_waters=True)
    
    
    for p in param_split:

        plt.outputLocation(folder_loc, "_Dashboard.html")
        
        #### RawData ### 
        df_raw = water.rawData(lakeWatch = 'No')
        XY_raw = plt.XYPlot(w, df_raw, [p], y_axis_select, 'Raw Data')
        TS_raw = plt.TimeSeriesPlot(w, df_raw, 'Date', [p], 'Raw Data')
        
        ### AGMs ###
        df_AGM = water.qaFiltered(lakeWatch = 'No')
        XY_AGM = plt.XYPlot(w, df_AGM, [p], y_axis_select, 'AGM')
        
        df_AGM = df_AGM.reset_index(drop=True)
        df_AGM['YEAR'] = pd.to_datetime(df_AGM['YEAR'], format='%Y')
        TS_AGM = plt.TimeSeriesPlot(w, df_AGM, 'YEAR', [p], 'AGM')
        
        pc = plsm.pie_chart(lvl_LU_df, [p])
        
        db_raw = layout([[TS_raw], [XY_raw, pc]], sizing_mode = 'scale_width')
        db_AGM = layout([[TS_AGM], [XY_AGM, pc]], sizing_mode = 'scale_width')
        
        tab_raw = plt.createPanel(db_raw, 'Raw Data')
        tab_AGM = plt.createPanel(db_AGM, 'AGM')
        
        dataTabs = plt.createTabs([tab_raw, tab_AGM], 'left')

        # db = layout([[TS_raw, XY_raw], [TS_AGM, XY_AGM]], sizing_mode = 'scale_width')

        tab = plt.createPanel(dataTabs, str(p))
        paramTab.append(tab)
    
    paramTabs = plt.createTabs(paramTab, 'above')
    plt.savePlot(paramTabs)
        

























