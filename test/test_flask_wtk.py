import json
import numpy
import pandas
from unittest import TestCase, skip
import flask_wtk
from pywtk.wtk_api import FORECAST_ATTRS

class TestFlaskWTK(TestCase):
    def setUp(self):
        self.app = flask_wtk.app.test_client()

    def test_met(self):
        site_id = "102445"
        start = pandas.Timestamp('2007-08-01', tz='utc')
        end = pandas.Timestamp('2007-08-15', tz='utc')
        #expected = [2007,8,1,0,0,1.178,0.9530000000000001,101280.25600000001,292.58,216.43200000000002,4.995]
        #expected_dict = dict(zip(["density", "power", "pressure", "temperature", "wind_direction", "wind_speed"], expected[5:]))
        attributes = ["power", "wind_direction", "wind_speed", "temperature",
                      "pressure","density"]
        expected = [9.53277647e-01, 2.16432190e+02, 4.99592876e+00, 2.92580750e+02,
                    1.01280258e+05, 1.17889750e+00]
        expected_dict = dict(zip(attributes, expected))
        req = '/met?site_id=%s&start=%s&end=%s'%(site_id,start.value//10**9, end.value//10**9)
        #print "Request is %s"%req
        resp = self.app.get(req)
        resp_data = resp.get_data()
        ret_data = json.loads(resp_data)
        self.assertIn(site_id, ret_data)
        df = pandas.read_json(json.dumps(ret_data[site_id]))
        first_row = df.ix[0].to_dict()
        for n,v in expected_dict.items():
            self.assertEqual(0, round((v - first_row[n])/v, 7))
        #self.assertEqual(expected_dict, df.ix[0].to_dict())
        self.assertEqual(14*24*12+1, len(df)) # End is inclusive of midnight


    def test_fcst(self):
        site_id = "53252"
        start = pandas.Timestamp('2007-01-01', tz='utc')
        end = pandas.Timestamp('2007-01-02', tz='utc')
        expected = numpy.array([6.2671943, 8.6079865, 6.7353525,
                    6.384234, 0.26309761, 3.6874273, 1.4196928, 0.53551841,
                    10.572015, 13.249797, 10.526829, 10.306773], dtype='float32')
        ex_dict = dict(zip(FORECAST_ATTRS, expected))
        req = '/fcst?site_id=%s&start=%s&end=%s'%(site_id,start.value//10**9, end.value//10**9)
        #print "Request is %s"%req
        resp = self.app.get(req)
        resp_data = resp.get_data()
        ret_data = json.loads(resp_data)
        self.assertIn(site_id, ret_data)
        fcst_data = pandas.read_json(json.dumps(ret_data[site_id]))
        self.assertEqual(25, len(fcst_data))
        for k, v in ex_dict.items():
            self.assertAlmostEqual(v, fcst_data.ix[0][k])
        return


        start = pandas.Timestamp('2007-01-01', tz='utc')
        end = pandas.Timestamp('2007-01-02', tz='utc')
        fcst_data = get_forecast_data("53252", start, end, utc=True)
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







        self.assertIn(site_id, ret_data)
        df = pandas.read_json(ret_data[site_id])
        first_row = df.ix[0].to_dict()
        for n,v in expected_dict.items():
            self.assertAlmostEqual(v, first_row[n])
        #self.assertEqual(expected_dict, df.ix[0].to_dict())
        self.assertEqual(14*24*12+1, len(df)) # End is inclusive of midnight
