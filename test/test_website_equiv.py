import calendar
import csv
import time
from unittest import TestCase, skip
from zipfile import ZipFile

from wtk_api import get_wind_data_by_wkt, save_wind_data

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
        &site_url=wind-toolkit%2Fwind%2Fwtk_download.json&full_name=Harry+Sorensen&email=harry.sorensen%40nrel.gov&affiliation=NREL&mailing_list=false&reason=Development+testing
        '''
        wind_dict = get_wind_data_by_wkt(wkt, names, attributes=attributes, leap_day=leap_day, utc=utc)
        wind_data = wind_dict["53252"]
        #Year,Month,Day,Hour,Minute,density at hub height (kg/m^3),power (MW),surface air pressure (Pa),air temperature at 2m (K),wind direction at 100m (deg),wind speed at 100m (m/s)
        first_line = [2011,1,1,0,0,1.1320000000000001,15.359,85467.688,259.591,318.124,11.844]
        expected_dict = dict(zip(["density", "power", "pressure", "temperature", "wind_direction", "wind_speed"], first_line[5:]))
        self.assertEqual(expected_dict, wind_data.ix[0].to_dict())
        self.assertEqual(365*24*12, len(wind_data))
        utc = True
        wind_dict = get_wind_data_by_wkt(wkt, ["2011"], attributes=attributes, leap_day=leap_day, utc=utc)
        wind_data = wind_dict["53252"]
        first_line = [2011,1,1,0,0,1.1420000000000001,15.991,85195.768,257.153,322.557,14.126]
        expected_dict = dict(zip(["density", "power", "pressure", "temperature", "wind_direction", "wind_speed"], first_line[5:]))
        self.assertEqual(expected_dict, wind_data.ix[0].to_dict())
        self.assertEqual(365*24*12, len(wind_data))
        #wind_data = get_wind_data(wkt, ["2012"], attributes=attributes, leap_day=leap_day, utc=utc, save_to_zip="output_CO_test_point_2012_utc.csv")

        #print wind_data
        #with ZipFile('test/example1.zip', 'r') as expected_zip:
        #    expected_wind_data = csv.reader(expected_zip.open('53252-2011.csv'))
            # Put csv data into the dataframe format
        # Compare results to dataframe format
        return
        # East coast without conversion to Local
        #https://mapsbeta.nrel.gov/api/developer_proxy?wkt=POINT(-66.8792724609375+44.762336674810996)&
        #attributes=power%2Cwind_direction%2Cwind_speed%2Ctemperature%2Cpressure%2Cdensity&names=2007&
        #site_url=wind-toolkit%2Fwind%2Fwtk_download.json&full_name=Harry+Sorensen&
        #email=harry.sorensen%40nrel.gov&affiliation=NREL&mailing_list=false&
        #reason=Development+testing&leap_day=false&utc=true
        wkt = "POINT(-66.8792724609375 44.762336674810996)"
        names = ["2007"]
        utc = True
        wind_data = get_wind_data(wkt, names, attributes=attributes, leap_day=leap_day, utc=utc, save_to_zip="output_east_test_point_url_utc.csv")
        print "East data utc"
        #print wind_data
        utc = False
        wind_data = get_wind_data(wkt, names, attributes=attributes, leap_day=leap_day, utc=utc, save_to_zip="output_east_test_point_url_local.csv")
        print "East data local"
        #print wind_data

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
        &site_url=wind-toolkit%2Fwind%2Fwtk_download.json&full_name=Harry+Sorensen&email=harry.sorensen%40nrel.gov&affiliation=NREL&mailing_list=false&reason=Development+testing
        '''
        print "CO save data"
        wind_data = get_wind_data(wkt, names, attributes=attributes, leap_day=leap_day, utc=utc)
        save_wind_data({"53252":wind_data}, "output_CO_test_point_2011_utc.zip")
