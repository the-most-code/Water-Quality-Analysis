

userString = 'polygon'
#userString = arcpy.GetParameterAsTex(0)

polygon = r'C:\dummy.shp'
#layer = arcpy.GetParameterAsText(1)

import pandas as pd
import arcpy

class WAFR:
    def __init__(self, polygon = None, station_list = None,
                 facilities = r'C:\facilities.shp'):
        self.polygon = polygon
        self.station_list = station_list
        self.facilities = facilities

    def get_facilites(self, userString):
        if userString == 'polygon':
            arcpy.Clip_analysis(self.facilites, self.polygon, temp_out_clip)


        elif userString == 'stations':
            sta = pd.unique(station_list)






