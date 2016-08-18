import calendar
import csv
import pandas
import time
from unittest import TestCase, skip
from zipfile import ZipFile

from wtk_api import get_wind_data, get_wind_data_by_wkt, get_3tiersites_from_wkt, get_nc_data, save_wind_data

class TestGetWindData(TestCase):
    def test_part_year(self):
        '''Pull part of a year
        '''
        attributes = ["power", "wind_direction", "wind_speed", "temperature",
                      "pressure","density"]
        #attributes = ["power"]
        leap_day = False
        utc = True
        start = pandas.Timestamp('2007-08-01', tz='utc')
        end = pandas.Timestamp('2007-08-15', tz='utc')
        wind_data = get_wind_data("102445", start, end, attributes=attributes, leap_day=leap_day, utc=utc)
        expected = [2007,8,1,0,0,1.178,0.9530000000000001,101280.25600000001,292.58,216.43200000000002,4.995]
        expected_dict = dict(zip(["density", "power", "pressure", "temperature", "wind_direction", "wind_speed"], expected[5:]))
        self.assertEqual(expected_dict, wind_data.ix[0].to_dict())
        self.assertEqual(14*24*12+1, len(wind_data)) # End is inclusive of midnight
        utc = False
        start = pandas.Timestamp('2007-08-01', tz='America/New_York')
        end = pandas.Timestamp('2007-08-15', tz='America/New_York')
        # The files return Standard Time rather than Daylight Savings time
        #2007,7,31,23,0,1.176,2.7840000000000003,101219.832,290.957,251.209,6.839
        #2007,8,1,0,0,1.177,2.458,101206.096,290.874,248.353,6.595
        # Testing as though local time should use DST where appropriate
        expected = [2007,7,31,23,0,1.176,2.7840000000000003,101219.832,290.957,251.209,6.839]
        wind_data = get_wind_data("102445", start, end, attributes=attributes, leap_day=leap_day, utc=utc)
        expected_dict = dict(zip(["density", "power", "pressure", "temperature", "wind_direction", "wind_speed"], expected[5:]))
        self.assertEqual(expected_dict, wind_data.ix[0].to_dict())
        self.assertEqual(14*24*12+1, len(wind_data)) # End is inclusive of midnight

    def test_multiple_years(self):
        '''Pull multiple years
        '''
        attributes = ["power", "wind_direction", "wind_speed", "temperature",
                      "pressure","density"]
        #attributes = ["power"]
        leap_day = True
        utc = True
        start = pandas.Timestamp('2007-08-01', tz='utc')
        end = pandas.Timestamp('2008-08-15', tz='utc')
        wind_data = get_wind_data("102445", start, end, attributes=attributes, leap_day=leap_day, utc=utc)
        expected = [2007,8,1,0,0,1.178,0.9530000000000001,101280.25600000001,292.58,216.43200000000002,4.995]
        expected_dict = dict(zip(["density", "power", "pressure", "temperature", "wind_direction", "wind_speed"], expected[5:]))
        self.assertEqual(expected_dict, wind_data.ix[0].to_dict())
        # 2008 is a leap year
        self.assertEqual(366*24*12+14*24*12+1, len(wind_data)) # End is inclusive of midnight
        leap_day = False
        wind_data = get_wind_data("102445", start, end, attributes=attributes, leap_day=leap_day, utc=utc)
        expected = [2007,8,1,0,0,1.178,0.9530000000000001,101280.25600000001,292.58,216.43200000000002,4.995]
        expected_dict = dict(zip(["density", "power", "pressure", "temperature", "wind_direction", "wind_speed"], expected[5:]))
        self.assertEqual(expected_dict, wind_data.ix[0].to_dict())
        # 2008 is a leap year
        self.assertEqual(365*24*12+14*24*12+1, len(wind_data)) # End is inclusive of midnight

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
        save_wind_data({53252:wind_data}, "output_CO_test_point_2011_utc.zip")

    @skip
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
