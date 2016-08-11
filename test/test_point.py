import calendar
import csv
import time
from unittest import TestCase
from zipfile import ZipFile

from wtk_api import get_wind_data, get_3tiersites_from_wkt, get_nc_data

class example1(TestCase):
    def test_point_url(self):
        '''Make sure POINT results match example data downloaded from
        https://mapsbeta.nrel.gov/api/developer_proxy
        '''
        wkt = "POINT(-103.128662109375 40.24179856487036)"
        attributes = ["power", "wind_direction", "wind_speed", "temperature",
                      "pressure","density"]
        #attributes = ["power"]
        names = ["2011"]
        leap_day = False
        utc = False
        ''' Extra cruft
        &site_url=wind-toolkit%2Fwind%2Fwtk_download.json&full_name=Harry+Sorensen&email=harry.sorensen%40nrel.gov&affiliation=NREL&mailing_list=false&reason=Development+testing
        '''
        wind_data = get_wind_data(wkt, names, attributes, leap_day, utc, save_to_zip="output_CO_test_point_url.csv")
        print "CO data"
        print wind_data
        #with ZipFile('test/example1.zip', 'r') as expected_zip:
        #    expected_wind_data = csv.reader(expected_zip.open('53252-2011.csv'))
            # Put csv data into the dataframe format
        # Compare results to dataframe format

        # East coast without conversion to Local
        #https://mapsbeta.nrel.gov/api/developer_proxy?wkt=POINT(-66.8792724609375+44.762336674810996)&
        #attributes=power%2Cwind_direction%2Cwind_speed%2Ctemperature%2Cpressure%2Cdensity&names=2007&
        #site_url=wind-toolkit%2Fwind%2Fwtk_download.json&full_name=Harry+Sorensen&
        #email=harry.sorensen%40nrel.gov&affiliation=NREL&mailing_list=false&
        #reason=Development+testing&leap_day=false&utc=true
        wkt = "POINT(-66.8792724609375 44.762336674810996)"
        names = ["2007"]
        utc = True
        wind_data = get_wind_data(wkt, names, attributes, leap_day, utc, save_to_zip="output_east_test_point_url.csv")
        print "East data utc"
        print wind_data
        utc = False
        wind_data = get_wind_data(wkt, names, attributes, leap_day, utc, save_to_zip="output_east_test_point_url.csv")
        print "East data local"
        print wind_data

    def test_site_nc(self):
        '''Match site example data downloaded from
        https://mapsbeta.nrel.gov/api/developer_proxy
        '''
        # UTC
        t_start = calendar.timegm((2011,1,1,0,0,0))
        t_end = calendar.timegm((2011,12,31,23,55,0))
        # Local
        t_start = time.mktime((2011, 1, 1, 0, 0, 0, 0, 0, 0))
        t_end = time.mktime((2011, 12, 31, 23, 55, 0, 0, 0, 0))
        attributes = ["power", "wind_direction", "wind_speed", "temperature",
                      "pressure","density"]
        nc_data = get_nc_data(53252, t_start, t_end, attributes)
        print nc_data
