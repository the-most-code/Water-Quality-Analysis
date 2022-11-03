import IWRPull as LA
import Plotting as pltng
import pandas as pd
import xlsxwriter
import openpyxl
# import sqlite3

wbid_input = "3002G"
wbid_input = wbid_input.split(", ")
wbid = [x.strip() for x in wbid_input]


start_yr = 2000

try:
    start_yr = int(str(start_yr).strip())
except:
    start_yr = 2000

folder_loc = r'C:\development_2\toolRuns\test_eric\multiple_tables'

lakeWatch = 'No'


param_all = "TN;TP" # this is fed into bokeh
param_split = param_all.split(";")
param = [i.strip() for i in param_split]

df_length = {}
result_df = {}

select_years = 'No'
years_df = None

if select_years == "Yes":
    years_input = "2018"
    #years_input = arcpy.GetParameterAsText(5)
    years_input = years_input.split(";")
    map_years = map(float, years_input)
    map_years = list(map_years)

    year_exclusion = {'YEAR': map_years}
    years_df = pd.DataFrame(year_exclusion)



for w in wbid:
    water = LA.dataPull(w, start_yr, "'CHLAC', 'TP', 'TN'")
    
    # Performing wbid input check
    water.wbidCheck()
    
    AGMs = water.qaFiltered(lakeWatch, select_years, years_df)
    #df_length[str(w)] = str(len(AGMs) + 1)
    
    NNC_df = water.NNC_derivation()
    
    plt = pltng.Visualization(w)
    plt.outputLocation(folder_loc, "_NNC_Derivation_Plot.html")
    
    clr_type, color = water.colorClass()
    
    fig = plt.NonH1Plot(w, AGMs, clr_type, param, NNC_df)
    plt.savePlot(fig)
    
    # Casting Minimum NNC criteria for TN and TP to variables
    NNC_TP = water.NNC_criteria().loc[int(color), 'Min_TP_NNC_(mg/L)']
    NNC_TN = water.NNC_criteria().loc[int(color), 'Min_TN_NNC_(mg/L)']
    
    # Taking Max AGMs
    AGM_max = AGMs[['CHLAC', 'TN', 'TP']].max()
    AGM_max = AGM_max.reset_index()
    AGM_max = pd.pivot_table(AGM_max, columns='mastercode')

    # Casting Max AGMs to Variables
    Max_TP = AGM_max.loc[0, 'TP']
    Max_TN = AGM_max.loc[0, 'TN']
    
    # # Performing % Reduction
    if NNC_TN < Max_TN:
        percent_reduction_TN = ((Max_TN - NNC_TN) / Max_TN) * 100
    elif NNC_TN > Max_TN:
        percent_reduction_TN = 0

    if NNC_TP < Max_TP:
        percent_reduction_TP = ((Max_TP - NNC_TP) / Max_TP) * 100
    elif NNC_TP > Max_TP:
        percent_reduction_TP = 0

    # Renaming columns for excel output
    AGMs = AGMs.rename(columns={'CHLAC': 'CHLAC (μg/L)',
                                'TN':    'TN (mg/L)',
                                'TP':    'TP (mg/L)'})
    reductions = pd.DataFrame({'TN % Reduction': percent_reduction_TN,
                                'TP % Reduction': percent_reduction_TP}, index=[0])

    #concatinating AGM dataframe and % reduction dataframe
    results = pd.concat([AGMs, reductions]).reset_index(drop=True)
    cols = ['YEAR', 'CHLAC (μg/L)', 'TN (mg/L)', 'TP (mg/L)', 'TN % Reduction',  'TP % Reduction']
    results = results[cols].round(3)
    # Appending key:value pair to the result_df dictionary
    result_df[str(w)] = results

    # Creating Filepath to xlsx file
filepath = folder_loc + "\\Percent_Reductions.xlsx"
writer = pd.ExcelWriter(filepath, engine='xlsxwriter')

workbook = writer.book

for w in wbid:
    result = result_df[str(w)].to_excel(writer, sheet_name= str(w) + 'Percent_Reductions')
    
    # column formatting
    worksheet = writer.sheets[str(w) + 'Percent_Reductions']
    # worksheet.conditional_format('C2:C' + df_length[str(w)], {'type': '3_color_scale'})
    # worksheet.conditional_format('D2:D' + df_length[str(w)], {'type': '3_color_scale'})
    # worksheet.conditional_format('E2:D' + df_length[str(w)], {'type': '3_color_scale'})
    worksheet.set_column(2, 4, 12)
    worksheet.set_column(5, 6, 20)
    
writer.close()






