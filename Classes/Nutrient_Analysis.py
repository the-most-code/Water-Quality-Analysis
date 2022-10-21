# -*- coding: utf-8 -*-
"""
Created on Fri Feb  4 11:51:01 2022

@author: Tano_E
"""

'''
Imports PLSM and Septic class to perform nutrient analysis.

'''
import PLSM
import Septic

arcpy.env.overwriteOutput = True


# PLSM class variables
#watershed_input = r'C:\development_2\Test\classes\plsm_septic\inputs\HUC.shp'
watershed_input = arcpy.GetParameterAsText(0)

#waterbody_input = r'C:\development_2\Test\classes\plsm_septic\inputs\Estuary_clipped.shp'
waterbody_input = arcpy.GetParameterAsText(1)

#rainfall_input = r'C:\development_2\Test\classes\plsm\biscayne\Annual_Rain.csv'
rainfall_input = arcpy.GetParameterAsText(2)

#people = 3
people = float(arcpy.GetParameterAsText(3))

#folder_location = r'C:\development_2\Test\classes\plsm_septic'
folder_location = arcpy.GetParameterAsText(4)


# PLSM functions
plsm = PLSM(watershed_input, rainfall_input, folder_location)
rainfall_df = plsm.rainfallQA()
layer_to_process, temp_folder_path = plsm.Clip('Analysis')
dissolve_input, n_rows, clip_input = plsm.Dissolve(layer_to_process, temp_folder_path)
plsm.calculateField(dissolve_input)
plsm.attribute_to_CSV(dissolve_input, temp_folder_path)
join1 = plsm.Merge(temp_folder_path, n_rows)

d = plsm.writeData(rainfall_df, join1)
lta_initial_df = plsm.ltaLoading(dissolve_input, d)

#plsm.annualLoading(dissolve_input, d)
#plsm.plsm_data_extract()

# Septic functions to get nitrogen
septic = Septic(watershed_input, waterbody_input, people, folder_location)
selectionTanks, temp_folder_path = septic.clipTanks()
septic_buffer_count = septic.Buffer(selectionTanks, temp_folder_path)
septic_loading, septic_DF = septic.runCalculation(septic_buffer_count)

# feed septic output in plsm piechart data
plsm.pieChart(d, clip_input, septic_loading, include_septic=True, remove_waters=True)
