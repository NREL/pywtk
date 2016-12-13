import calendar
import csv
import numpy
import pandas
import time
from unittest import TestCase, skip
from zipfile import ZipFile

from pywtk.wtk_api import get_nc_data, get_wind_data_by_wkt, FORECAST_ATTRS, WIND_FCST_DIR

class TestGetForecastData(TestCase):
    def test_multiple_years(self):
        '''Match site data from forecast nc files for multiple years
        '''
        # UTC
        start = pandas.Timestamp('2007-01-01', tz='utc')
        end = pandas.Timestamp('2008-08-02', tz='utc')
        fcst_data = get_nc_data("53252", start, end, utc=True, nc_dir=WIND_FCST_DIR)
        self.assertEqual(start, fcst_data.index[0])
        self.assertEqual(end, fcst_data.index[-1])

    def test_partial_year(self):
        '''Match site data from forecast nc files
        '''
        # UTC
        start = pandas.Timestamp('2007-01-01', tz='utc')
        end = pandas.Timestamp('2007-01-02', tz='utc')
        fcst_data = get_nc_data("53252", start, end, utc=True, nc_dir=WIND_FCST_DIR)
        self.assertEqual(start, fcst_data.index[0])
        # From ncdump, all values are float32 which do not compare easily to
        # python floats which are float64
        expected = numpy.array([6.2671943, 8.6079865, 6.7353525,
                    6.384234, 0.26309761, 3.6874273, 1.4196928, 0.53551841,
                    10.572015, 13.249797, 10.526829, 10.306773], dtype='float32')
        self.assertEqual(25, len(fcst_data))
        self.assertTrue(numpy.array_equal(expected, list(fcst_data.ix[0])))
        ex_dict = dict(zip(FORECAST_ATTRS, expected))
        # Verify column names are correct
        for k, v in ex_dict.items():
            self.assertEqual(v, fcst_data.ix[0][k])
        # Local
        #start = pandas.Timestamp('2007-01-01', tz='America/Denver')
        #end = pandas.Timestamp('2007-01-02', tz='America/Denver')
        fcst_data = get_nc_data("53252", start, end, utc=False, nc_dir=WIND_FCST_DIR)
        self.assertEqual(start, fcst_data.index[0])
        # From ncdump, all values are float32 which do not compare easily to
        # python floats which are float64
        expected = numpy.array([6.2671943, 8.6079865, 6.7353525,
                    6.384234, 0.26309761, 3.6874273, 1.4196928, 0.53551841,
                    10.572015, 13.249797, 10.526829, 10.306773], dtype='float32')
        self.assertEqual(25, len(fcst_data))
        self.assertTrue(numpy.array_equal(expected, list(fcst_data.ix[0])))
        ex_dict = dict(zip(FORECAST_ATTRS, expected))
        # Verify column names are correct
        for k, v in ex_dict.items():
            self.assertEqual(v, fcst_data.ix[0][k])
    def test_get_forecast_from_wkt(self):
        '''Test retrieval of data based on wkt
        '''
        wkt = 'POINT(-103.0432 40.4506)'
        fcst_dict = get_wind_data_by_wkt(wkt, ["2007"], utc=True, dataset="forecast")
        self.assertIn("53252", fcst_dict)
        fcst_data = fcst_dict["53252"]
        start = pandas.Timestamp('2007-01-01', tz='UTC')
        self.assertEqual(start, fcst_data.index[0])
        # From ncdump, all values are float32 which do not compare easily to
        # python floats which are float64
        expected = numpy.array([6.2671943, 8.6079865, 6.7353525,
                    6.384234, 0.26309761, 3.6874273, 1.4196928, 0.53551841,
                    10.572015, 13.249797, 10.526829, 10.306773], dtype='float32')
        self.assertEqual(24*365, len(fcst_data))
        self.assertTrue(numpy.array_equal(expected, list(fcst_data.ix[0])))
        ex_dict = dict(zip(FORECAST_ATTRS, expected))
        # Verify column names are correct
        for k, v in ex_dict.items():
            self.assertEqual(v, fcst_data.ix[0][k])
