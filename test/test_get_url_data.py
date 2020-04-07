#import calendar
#import csv
import numpy
import pandas
#import time
from unittest import TestCase, skip
#from zipfile import ZipFile

#from pywtk.wtk_api import get_wind_data, get_wind_data_by_wkt, get_3tiersites_from_wkt, get_nc_data, save_wind_data, WIND_MET_NC_DIR
from pywtk.wtk_api import get_nc_data_from_url
#WTK_URL = "https://h2oq9ul559.execute-api.us-west-2.amazonaws.com/dev"
WTK_URL = "https://f9g6p4cbvi.execute-api.us-west-2.amazonaws.com/prod"


class TestGetWindData(TestCase):
    def test_part_year(self):
        '''Pull part of a year using URL
        '''
        attributes = ["power", "wind_direction", "wind_speed", "temperature",
                      "pressure","density"]
        #attributes = ["power"]
        leap_day = False
        utc = True
        start = pandas.Timestamp('2007-08-01', tz='utc')
        end = pandas.Timestamp('2007-08-15', tz='utc')
        wind_data = get_nc_data_from_url(WTK_URL+"/met", "102445", start, end, attributes=attributes, leap_day=leap_day, utc=utc)
        #expected = [2007,8,1,0,0,1.178,0.9530000000000001,101280.25600000001,292.58,216.43200000000002,4.995]
        #expected_dict = dict(zip(["density", "power", "pressure", "temperature", "wind_direction", "wind_speed"], expected[5:]))
        #self.assertEqual(expected_dict, wind_data.iloc[0].to_dict())
        expected = [9.53277647e-01, 2.16432190e+02, 4.99592876e+00, 2.92580750e+02,
                    1.01280258e+05, 1.17889750e+00]
        numpy.testing.assert_allclose(expected, wind_data.iloc[0].values)
        self.assertEqual(14*24*12+1, len(wind_data)) # End is inclusive of midnight
        self.assertEqual(start, wind_data.index[0])
        utc = False
        start = pandas.Timestamp('2007-08-01', tz='America/New_York')
        end = pandas.Timestamp('2007-08-15', tz='America/New_York')
        # The files return Standard Time rather than Daylight Savings time
        #2007,7,31,23,0,1.176,2.7840000000000003,101219.832,290.957,251.209,6.839
        #2007,8,1,0,0,1.177,2.458,101206.096,290.874,248.353,6.595
        # Testing as though local time should use DST where appropriate
        #expected = [2007,7,31,23,0,1.176,2.7840000000000003,101219.832,290.957,251.209,6.839]
        wind_data = get_nc_data_from_url(WTK_URL+"/met", "102445", start, end, attributes=attributes, leap_day=leap_day, utc=utc)
        #expected_dict = dict(zip(["density", "power", "pressure", "temperature", "wind_direction", "wind_speed"], expected[5:]))
        #self.assertEqual(expected_dict, wind_data.iloc[0].to_dict())
        expected = [2.78404403e+00, 2.51209885e+02, 6.83912182e+00, 2.90957336e+02,
                    1.01219828e+05, 1.17690361e+00]
        numpy.testing.assert_allclose(expected, wind_data.iloc[0].values)
        self.assertEqual(14*24*12+1, len(wind_data)) # End is inclusive of midnight

    def test_multiple_years(self):
        '''Pull multiple years using URL
        '''
        attributes = ["power", "wind_direction", "wind_speed", "temperature",
                      "pressure","density"]
        #attributes = ["power"]
        leap_day = True
        utc = True
        start = pandas.Timestamp('2007-08-01', tz='utc')
        end = pandas.Timestamp('2008-08-15', tz='utc')
        wind_data = get_nc_data_from_url(WTK_URL+"/met", "102445", start, end, attributes=attributes, leap_day=leap_day, utc=utc)
        #wind_data = get_wind_data("102445", start, end, attributes=attributes, leap_day=leap_day, utc=utc, source="hdf")
        #expected = [2007,8,1,0,0,1.178,0.9530000000000001,101280.25600000001,292.58,216.43200000000002,4.995]
        #expected_dict = dict(zip(["density", "power", "pressure", "temperature", "wind_direction", "wind_speed"], expected[5:]))
        #self.assertEqual(expected_dict, wind_data.iloc[0].to_dict())
        expected = [9.53277647e-01, 2.16432190e+02, 4.99592876e+00, 2.92580750e+02,
                    1.01280258e+05, 1.17889750e+00]
        numpy.testing.assert_allclose(expected, wind_data.iloc[0].values)
        # 2008 is a leap year
        self.assertEqual(366*24*12+14*24*12+1, len(wind_data)) # End is inclusive of midnight
        return
        # Test leap day
        leap_day = False
        utc = False
        start = pandas.Timestamp('2007-08-01', tz='America/New_York')
        end = pandas.Timestamp('2008-08-15', tz='America/New_York')
        wind_data = get_nc_data_from_url(WTK_URL+"/met", "102445", start, end, attributes=attributes, leap_day=leap_day, utc=utc)
        #wind_data = get_wind_data("102445", start, end, attributes=attributes, leap_day=leap_day, utc=utc, source="hdf")
        #expected = [2007,8,1,0,0,1.178,0.9530000000000001,101280.25600000001,292.58,216.43200000000002,4.995]
        #expected_dict = dict(zip(["density", "power", "pressure", "temperature", "wind_direction", "wind_speed"], expected[5:]))
        #self.assertEqual(expected_dict, wind_data.iloc[0].to_dict())
        expected = [2.78404403e+00, 2.51209885e+02, 6.83912182e+00, 2.90957336e+02,
                    1.01219828e+05, 1.17690361e+00]
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
        &site_url=wind-toolkit%2Fwind%2Fwtk_download.json&full_name=Your+Name&email=your.email%40here&affiliation=NREL&mailing_list=false&reason=Development+testing
        '''
        # print "CO save data"
        # wind_data = get_wind_data(wkt, names, attributes=attributes, leap_day=leap_day, utc=utc)
        # save_wind_data({53252:wind_data}, "output_CO_test_point_2011_utc.zip")

    @skip
    def test_site_nc(self):
        '''Pull met data using the nc files
        '''
        attributes = ["power", "wind_direction", "wind_speed", "temperature",
                      "pressure","density"]
        leap_day = True
        utc = True
        start = pandas.Timestamp('2007-08-01', tz='utc')
        end = pandas.Timestamp('2007-08-15', tz='utc')
        wind_data = get_nc_data("102445", start, end, attributes=attributes, leap_day=leap_day, utc=utc, nc_dir=WIND_MET_NC_DIR)
        expected = [9.53277647e-01, 2.16432190e+02, 4.99592876e+00, 2.92580750e+02,
                    1.01280258e+05, 1.17889750e+00]
        numpy.testing.assert_allclose(expected, wind_data.iloc[0].values)
        self.assertEqual(14*24*12+1, len(wind_data)) # End is inclusive of midnight
        utc = False
        start = pandas.Timestamp('2007-08-01', tz='America/New_York')
        end = pandas.Timestamp('2007-08-15', tz='America/New_York')
        # The files return Standard Time rather than Daylight Savings time
        #2007,7,31,23,0,1.176,2.7840000000000003,101219.832,290.957,251.209,6.839
        #2007,8,1,0,0,1.177,2.458,101206.096,290.874,248.353,6.595
        # Testing as though local time should use DST where appropriate
        expected = [2.78404403e+00, 2.51209885e+02, 6.83912182e+00, 2.90957336e+02,
                    1.01219828e+05, 1.17690361e+00]
        wind_data = get_nc_data("102445", start, end, attributes=attributes, leap_day=leap_day, utc=utc, nc_dir=WIND_MET_NC_DIR)
        numpy.testing.assert_allclose(expected, wind_data.iloc[0].values)
        self.assertEqual(14*24*12+1, len(wind_data)) # End is inclusive of midnight

    @skip
    def test_wind_data_nc(self):
        '''Pull nc data from get_wind_data
        '''
        #wkt = "POINT(-103.128662109375 40.24179856487036)"
        attributes = ["power", "wind_direction", "wind_speed", "temperature",
                      "pressure", "density"]
        #attributes = ["power"]
        #names = ["2011"]
        leap_day = False
        utc = False
        start = pandas.Timestamp('2011-01-01', tz='America/Denver')
        end = pandas.Timestamp('2011-12-31 23:59:59', tz='America/Denver')
        wind_data = get_wind_data("53252", start, end, attributes=attributes, leap_day=leap_day, utc=utc, source="nc")
        #wind_data = wind_dict["53252"]
        #Year,Month,Day,Hour,Minute,density at hub height (kg/m^3),power (MW),surface air pressure (Pa),air temperature at 2m (K),wind direction at 100m (deg),wind speed at 100m (m/s)
        #first_line = [2011,1,1,0,0,1.1320000000000001,15.359,85467.688,259.591,318.124,11.844]
        # Match to the higher accuracy of the nc dataset
        expected = [15.35958480834961, 318.1243896484375, 11.844223022460938, 259.5919494628906, 85467.6875, 1.132704496383667]
        #expected_dict = dict(zip(["density", "power", "pressure", "temperature", "wind_direction", "wind_speed"], first_line[5:]))
        expected_dict = dict(zip(['power', 'wind_direction', 'wind_speed', 'temperature', 'pressure', 'density'], expected))
        self.assertEqual(expected_dict, wind_data.iloc[0].to_dict())
        #print map(float, wind_data.iloc[0].values)
        #print wind_data.columns.values
        self.assertEqual(365*24*12, len(wind_data))
