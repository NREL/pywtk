import json
import numpy
import pandas
from unittest import TestCase
import os
from pywtk.wtk_api import FORECAST_ATTRS
import urllib

os.environ["DATA_BUCKET"] = "nrel-pds-wtk/wtk-techno-economic/pywtk-data"
import flask_wtk


class TestFlaskWTK(TestCase):
    def setUp(self):
        self.app = flask_wtk.app.test_client()

    def test_sites(self):
        site_id = "102445"
        req = '/sites?sites=%s&orient=records' % (site_id)
        resp = self.app.get(req)
        resp_data = resp.get_data()
        ret_data = json.loads(resp_data)
        expected = {"site_id": 102445, "gid": 102446, "fraction_of_usable_area": 1.0,
                    "power_curve": "offshore", "capacity": 16.0, "wind_speed": 7.31,
                    "capacity_factor": 0.31, "the_geom": "0101000020E6100000F5D555815AAD51C0AEF204C24EDF4440",
                    "city": None, "state": None, "country": None, "elevation": None,
                    "lat": 41.744591, "lon": -70.708649}
        self.assertEqual(expected, ret_data[0])
        wkt = "POLYGON((-120.82763671875 34.452218472826566,-119.19616699218749 34.452218472826566,-119.19616699218749 33.920571528675104,-120.82763671875 33.920571528675104,-120.82763671875 34.452218472826566))"
        req = '/sites?wkt=%s&orient=columns' % (wkt)
        resp = self.app.get(req)
        resp_data = resp.get_data()
        ret_data = json.loads(resp_data)
        expected = [29375, 29733, 29872, 30019, 30190, 30539, 30712, 30713,
                    30873, 30874, 31032, 31033, 31034, 31189, 31190, 31191,
                    31192, 31320, 31321, 31322, 31323, 31324, 31563, 32060,
                    32314, 32834, 33203, 34828]
        site_ids = ret_data['site_id'].values()
        for site_id in expected:
            self.assertIn(site_id, site_ids)

    def test_met(self):
        site_id = "102445"
        start = pandas.Timestamp('2007-08-01', tz='utc')
        end = pandas.Timestamp('2007-08-15', tz='utc')
        #expected = [2007,8,1,0,0,1.178,0.9530000000000001,101280.25600000001,292.58,216.43200000000002,4.995]
        #expected_dict = dict(zip(["density", "power", "pressure", "temperature", "wind_direction", "wind_speed"], expected[5:]))
        attributes = ["power", "wind_direction", "wind_speed", "temperature",
                      "pressure", "density"]
        expected = [9.53277647e-01, 2.16432190e+02, 4.99592876e+00, 2.92580750e+02,
                    1.01280258e+05, 1.17889750e+00]
        expected_dict = dict(zip(attributes, expected))
        # Bad attributes
        req_args = {'sites': site_id, 'start': start.value//10**9, 'end': end.value//10**9,
                    'attributes': ",".join(attributes)+',bad_attribute'}
        req = '/met?%s' % (urllib.parse.urlencode(req_args))
        # print "Request is %s"%req
        resp = self.app.get(req)
        resp_data = resp.get_data()
        ret_data = json.loads(resp_data)
        self.assertIn("success", ret_data)
        self.assertFalse(ret_data["success"])
        # Good data
        req = '/met?sites=%s&start=%s&end=%s' % (site_id, start.value//10**9, end.value//10**9)
        # print "Request is %s"%req
        resp = self.app.get(req)
        resp_data = resp.get_data()
        ret_data = json.loads(resp_data)
        self.assertIn(site_id, ret_data)
        df = pandas.read_json(json.dumps(ret_data[site_id]))
        #first_row = df.ix[0].to_dict()
        first_row = df.iloc[0].to_dict()
        for n, v in expected_dict.items():
            self.assertEqual(0, round((v - first_row[n])/v, 7))
        # self.assertEqual(expected_dict, df.ix[0].to_dict())
        self.assertEqual(14*24*12+1, len(df)) # End is inclusive of midnight

    def test_fcst(self):
        site_id = "53252"
        start = pandas.Timestamp('2007-01-01', tz='utc')
        end = pandas.Timestamp('2007-01-02', tz='utc')
        e_list = [6.2671943, 8.6079865, 6.7353525, 6.384234, 0.26309761,
                  3.6874273, 1.4196928, 0.53551841, 10.572015, 13.249797,
                  10.526829, 10.306773]
        expected = numpy.array(e_list, dtype='float32')
        ex_dict = dict(zip(FORECAST_ATTRS, expected))
        req = '/fcst?sites=%s&start=%s&end=%s' % (site_id, start.value//10**9, end.value//10**9)
        # print "Request is %s"%req
        resp = self.app.get(req)
        resp_data = resp.get_data()
        ret_data = json.loads(resp_data)
        self.assertIn(site_id, ret_data)
        fcst_data = pandas.read_json(json.dumps(ret_data[site_id]))
        self.assertEqual(25, len(fcst_data))
        for k, v in ex_dict.items():
            #self.assertAlmostEqual(v, fcst_data.ix[0][k])
            self.assertAlmostEqual(v, fcst_data.iloc[0][k])
        return
