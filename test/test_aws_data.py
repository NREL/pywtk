import calendar
import csv
import numpy
import os
import pandas
import time
from unittest import TestCase, skip
from zipfile import ZipFile

from pywtk.wtk_api import get_nc_data

class TestAWSData(TestCase):
    def test_aws_wind_data(self):
        '''Pull nc data from AWS
        '''
        filename = os.path.join(os.path.dirname(__file__), "53252.nc")
        nc_dir = "s3://pywtk-data/met_data"
        #wkt = "POINT(-103.128662109375 40.24179856487036)"
        attributes = ["power", "wind_direction", "wind_speed", "temperature",
                      "pressure", "density"]
        #attributes = ["power"]
        #names = ["2011"]
        leap_day = False
        utc = False
        start = pandas.Timestamp('2011-01-01', tz='America/Denver')
        end = pandas.Timestamp('2011-12-31 23:59:59', tz='America/Denver')
        #wind_data = get_nc_data_from_file(filename, start, end, attributes=attributes, leap_day=leap_day, utc=utc)
        wind_data = get_nc_data("53252", start, end, attributes=attributes, leap_day=leap_day, utc=utc, nc_dir=nc_dir)
        #wind_data = wind_dict["53252"]
        #Year,Month,Day,Hour,Minute,density at hub height (kg/m^3),power (MW),surface air pressure (Pa),air temperature at 2m (K),wind direction at 100m (deg),wind speed at 100m (m/s)
        #first_line = [2011,1,1,0,0,1.1320000000000001,15.359,85467.688,259.591,318.124,11.844]
        # Match to the higher accuracy of the nc dataset
        expected = [15.35958480834961, 318.1243896484375, 11.844223022460938, 259.5919494628906, 85467.6875, 1.132704496383667]
        #expected_dict = dict(zip(["density", "power", "pressure", "temperature", "wind_direction", "wind_speed"], first_line[5:]))
        expected_dict = dict(zip(['power', 'wind_direction', 'wind_speed', 'temperature', 'pressure', 'density'], expected))
        self.assertEqual(expected_dict, wind_data.ix[0].to_dict())
        #print map(float, wind_data.ix[0].values)
        #print wind_data.columns.values
        self.assertEqual(365*24*12, len(wind_data))
