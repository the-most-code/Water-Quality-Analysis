"""
Created on 1/26/2022

@author: Tano_E
"""

import pandas as pd
import scipy
from scipy.stats.mstats import gmean
import math
from math import sqrt
from math import exp
import numpy as np
import statsmodels.api as sm

# import os.path
import os
import shutil
import sqlite3
import xlsxwriter
import openpyxl

import bokeh
from bokeh.models import ColumnDataSource #CategoricalColorMapper
from bokeh.io import save, output_file, show
from bokeh.plotting import figure
from bokeh.models import HoverTool, Legend
from bokeh.transform import factor_cmap
import bokeh.palettes as bkplt
from bokeh.io import save, output_file
from bokeh.layouts import column, row
from bokeh.models import Range1d
from bokeh.models import DatetimeTicker
from bokeh.models import Panel, Tabs
from bokeh.models import DatetimeTickFormatter
from statistics import mean, median, mode, stdev
from scipy.stats.mstats import gmean
from bokeh.io import curdoc

# this class has waterbody characteristics
class Waterbody:
    def __init__(self, wbid, start_yr, analyte):
        self.wbid = wbid
        self.start_yr = start_yr
        self.analyte = analyte

# waterbodies have data
class sourceData(Waterbody):
    def __init__(self, wbid, start_yr, analyte,
        sqlite_current = sqlite3.connect(r'C:\sqlite\IWR64.sqlite'),
        derivationData = pd.read_csv(r'C:\development_2\NNC_data.csv')):
        super().__init__(wbid, start_yr, analyte)
        # self.NNC = NNC
        self.sqlite = sqlite_current
        self.derivationData = derivationData

    def sqliteDestination(self, folder):
        self.sqlite  = sqlite3.connect(folder)
        return self.sqlite

    def dataExtraction(self):
        SQLquery = '''SELECT * FROM RawData WHERE wbid in ('%s')
        AND mastercode in (%s)
        AND year >= (%s)''' %(self.wbid, self.analyte, self.start_yr) 
        nutrients_df = pd.read_sql_query(SQLquery, self.sqlite)
        return nutrients_df
    

class dataPull:
    def __init__(self, wbid, start_yr, analyte):
        self.nutrients =  sourceData(wbid, start_yr, analyte)

    def iwrRUN(self, folder): #r'C:\sqlite\IWR62.sqlite'
        self.nutrients.sqliteDestination(str(folder))
        
    def factTable(self):
        fact_df = self.nutrients.dataExtraction()
        return fact_df

    def rawData(self, lakeWatch = 'No'):
        raw_df = self.nutrients.dataExtraction()
        raw_df = raw_df[(raw_df['result'] > 0)]
        if lakeWatch == 'No':
            raw_df = raw_df[raw_df.STA.str.contains("21FLKWAT") == False]
        # adding dates
        raw_df['date'] = pd.to_datetime(raw_df[['day', 'month', 'year']])
        raw_df['date'] = raw_df['date'].dt.date
        # setting index to date
        raw_df.index = raw_df.date
        # Drop NaN values so that data is not lost to pivot table
        raw_df = raw_df.dropna(subset=['result'])
        # casting raw data to pivot table
        raw_df = raw_df.reset_index(drop=True)
        # gets rid of duplicate station dates by aggregating daily medians
        raw_df = pd.pivot_table(raw_df, values = 'result', index=['date', 'STA'], columns = 'mastercode', aggfunc={"result":[median]}).reset_index()
        raw_df.columns = raw_df.columns.droplevel()
        raw_df.columns.values[[0, 1]] = ['Date', 'STA']
        return raw_df

    def NNC_derivation(self):
        return self.nutrients.derivationData
    
    def NNC_criteria(self):
        NNC = {'Type': [1, 2, 3], 'Color_&_Alk': ['> 40 Platinum Colbalt Units',
                           '≤ 40 Platinum Cobalt Units and > 20 mg/L CaCO3',
                           '≤ 40 Platinum Cobalt Units and ≤ 20 mg/L CaCO3' ],
                           'Min_TP_NNC_(mg/L)': [0.05, 0.03, 0.01],
                           'Min_TN_NNC_(mg/L)': [1.27, 1.05, 0.51]}
        NNC = pd.DataFrame.from_dict(NNC).set_index('Type')
        return NNC

    def wbid(self):
        return self.nutrients.wbid
    
    def wbidCheck(self):
        wbid_check = "SELECT * FROM RawData WHERE wbid in ('%s')" % (self.nutrients.wbid)
        wbid_check = pd.read_sql_query(wbid_check, self.nutrients.sqlite)
        if len(wbid_check) == 0:
            error_string = "WBID " + "'" + self.nutrients.wbid + "' " + "does not exist or input is not formatted correctly!"
            print(error_string)

    def colorClass(self):
        # Performing Color Classification
        color_class = "SELECT * FROM LakeClass WHERE wbid in ('%s')" % (self.nutrients.wbid)
        color_check = pd.read_sql_query(color_class, self.nutrients.sqlite)
        
        color_check.columns.values[[0, 1]] = ['WBID', 'COLOR']
        color_check = color_check.reset_index()
        color = color_check.loc[0, "COLOR"]
        
        if color == 1:
            clr_type = 'color'
            print(self.nutrients.wbid + ' is a high color lake')
        else:
            clr_type = 'clear'
            print(self.nutrients.wbid + ' is a low color lake')
        return clr_type, color
        
    def qaFiltered(self, lakeWatch = 'No', selectYears = 'No', years_df = None):
        nutrients_df = self.nutrients.dataExtraction()
        if lakeWatch == 'No':
            nutrients_df = nutrients_df[nutrients_df.STA.str.contains("21FLKWAT") == False]
        nutrients_df = nutrients_df[(nutrients_df['result'] > 0)]
        # Filter qualifier codes
        nutrients_df["mdl"] = pd.to_numeric(nutrients_df["mdl"])
        square_2 = sqrt(2)
        expression = nutrients_df["mdl"]/square_2
        nutrients_df["result"] = np.where((nutrients_df["rcode"] == "U") | (nutrients_df["rcode"] == "T"), expression, nutrients_df["result"])
        nutrients_df = nutrients_df.drop(nutrients_df[(nutrients_df["rcode"] == "G") | (nutrients_df["rcode"] == "V")].index)
        # Creating unique ID to calculate daily median of results with same date, station ID, and mastercode
        nutrients_df['date'] = pd.to_datetime(nutrients_df[['year','month', 'day']])
        nutrients_df['date'] = nutrients_df['date'].dt.strftime('%Y-%m-%d')
        nutrients_df['med_date'] = nutrients_df[['date', 'STA','mastercode']].apply(lambda x: ''.join(x), axis=1)
        avg_samples = nutrients_df.groupby('med_date', as_index=False).agg({"result": "median"})
        # Creating dictionary of avg samples by station and date
        avg_dict = avg_samples.set_index('med_date').to_dict()['result']
        # Dropping duplicate Station Dates
        nutrients_df = nutrients_df.drop_duplicates(subset=['med_date'])
        # Replacinnutrients_dfg main dataframe with averages
        nutrients_df['result'] = nutrients_df['med_date'].map(avg_dict)
        # Filter results for calculating geomeans - must be >= 4 samples per year and at least 1 sample in wet season and at least 1 sample in dry
        nutrients_df['result'] = nutrients_df.groupby(["year", "mastercode"])['result'].transform(lambda x: x if len(x) >= 4 else np.nan)
        nutrients_df = nutrients_df.sort_values(["year"])
        nutrients_df['Season'] = 'N'
        nutrients_df.loc[(nutrients_df['month'].between(4,10, inclusive = False)), 'Season'] = 'G'
        nutrients_df['Count_G'] = nutrients_df.groupby(['year', 'mastercode'])['Season'].transform(lambda x: x[x.str.contains('G')].count())
        nutrients_df['Count_N'] = nutrients_df.groupby(['year', 'mastercode'])['Season'].transform(lambda x: x[x.str.contains('N')].count())
        mask = ((nutrients_df['Count_G'] <= 0) | (nutrients_df['Count_N'] <= 0))
        nutrients_df.loc[mask, ['result']] = np.nan
        # Drop NaN values so that data is not lost to pivot table
        nutrients_df = nutrients_df.dropna(subset=['result'])
        # Calculate geometric means
        nutrients_df = pd.pivot_table(nutrients_df, values = 'result', index=['wbid','year'], columns = 'mastercode',aggfunc={"result":[gmean]}).reset_index()
        nutrients_df.columns = nutrients_df.columns.droplevel()
        nutrients_df.columns.values[[0, 1]] = ['WBID', 'YEAR']
        
        if selectYears == "Yes":
            # Omit Undesired Years
            y = nutrients_df.YEAR.isin(years_df.YEAR)
            nutrients_df_filter = nutrients_df[y]
            
            nutrients_df = nutrients_df[nutrients_df.isin(nutrients_df_filter) == False]
        return nutrients_df

class Analysis:
    def __init__(self, df):
        self.df = df

    def regression(self, predictor, response):
        df = self.df.dropna()

        y = df[str(response)]
        x = df[str(predictor)].astype(float)
        x = sm.add_constant(x)

        results = sm.OLS(y, x, missing='drop').fit()
        reg_results = results.summary()

        results_as_html = reg_results.tables[1].as_html()
        regression = pd.read_html(results_as_html, header=0, index_col=0)[0]
        regression = regression.reset_index()
        regression = regression.rename(columns={"coef": str(predictor)})
        regression = pd.pivot_table(regression, columns='index', values=str(predictor))
        regression = regression.reset_index()
        regression.columns.values[[0, 1, 2]] = ['Analyte', 'Slope', 'Y-Intercept']

        slope = regression.loc[0, 'Slope']
        intercept = regression.loc[0, 'Y-Intercept']
        R_squared = round(results.rsquared, 2)
        P_value = round(results.pvalues[1], 2)
        y_predicted = slope * x + intercept

        return R_squared, P_value, y_predicted, x, slope, intercept



