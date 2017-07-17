import calendar
import csv
import numpy
import time
from unittest import TestCase, skip
from zipfile import ZipFile

from pywtk.wtk_api import get_wind_data_by_wkt, save_wind_data

class TestWebsiteEquiv(TestCase):
    def test_point_url(self):
        '''Make sure POINT results match example data downloaded from
        https://mapsbeta.nrel.gov/api/developer_proxy
        '''
        wkt = "POINT(-103.128662109375 40.24179856487036)"
        attributes = ["power", "wind_direction", "wind_speed", "temperature",
                      "pressure", "density"]
        #attributes = ["power"]
        names = ["2011"]
        leap_day = False
        utc = False
        ''' Extra cruft
        &site_url=wind-toolkit%2Fwind%2Fwtk_download.json&full_name=Your+Name&email=your.email%40here&affiliation=NREL&mailing_list=false&reason=Development+testing
        '''
        wind_dict = get_wind_data_by_wkt(wkt, names, attributes=attributes, leap_day=leap_day, utc=utc)
        wind_data = wind_dict[53252]
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
        utc = True
        wind_dict = get_wind_data_by_wkt(wkt, ["2011"], attributes=attributes, leap_day=leap_day, utc=utc)
        wind_data = wind_dict[53252]
        #first_line = [2011,1,1,0,0,1.1420000000000001,15.991,85195.768,257.153,322.557,14.126]
        expected = [15.991483688354492, 322.55743408203125, 14.126996040344238, 257.1535339355469, 85195.765625, 1.1426444053649902]
        #expected_dict = dict(zip(["density", "power", "pressure", "temperature", "wind_direction", "wind_speed"], first_line[5:]))
        expected_dict = dict(zip(['power', 'wind_direction', 'wind_speed', 'temperature', 'pressure', 'density'], expected))
        self.assertEqual(expected_dict, wind_data.ix[0].to_dict())
        self.assertEqual(365*24*12, len(wind_data))

    @skip
    def test_point_save(self):
        '''Make sure POINT zip match example data downloaded from
        https://mapsbeta.nrel.gov/api/developer_proxy
        '''
        wkt = "POINT(-103.128662109375 40.24179856487036)"
        attributes = ["power", "wind_direction", "wind_speed", "temperature",
                      "pressure","density"]
        names = ["2011"]
        leap_day = False
        utc = False
        ''' Extra cruft
        &site_url=wind-toolkit%2Fwind%2Fwtk_download.json&full_name=Your+Name&email=your.email%40here&affiliation=NREL&mailing_list=false&reason=Development+testing
        '''
        print "CO save data"
        wind_data = get_wind_data(wkt, names, attributes=attributes, leap_day=leap_day, utc=utc)
        save_wind_data({"53252":wind_data}, "output_CO_test_point_2011_utc.zip")
