import json
import pandas
from unittest import TestCase, skip
import flask_wtk

class TestFlaskWTK(TestCase):
    def setUp(self):
        self.app = flask_wtk.app.test_client()

    def test_met(self):
        site_id = "102445"
        start = pandas.Timestamp('2007-08-01', tz='utc')
        end = pandas.Timestamp('2007-08-15', tz='utc')
        expected = [2007,8,1,0,0,1.178,0.9530000000000001,101280.25600000001,292.58,216.43200000000002,4.995]
        expected_dict = dict(zip(["density", "power", "pressure", "temperature", "wind_direction", "wind_speed"], expected[5:]))
        req = '/met?site_id=%s&start=%s&end=%s'%(site_id,start.value//10**9, end.value//10**9)
        #print "Request is %s"%req
        resp = self.app.get(req)
        resp_data = resp.get_data()
        ret_data = json.loads(resp_data)
        self.assertIn(site_id, ret_data)
        df = pandas.read_json(ret_data[site_id])
        first_row = df.ix[0].to_dict()
        for n,v in expected_dict.items():
            self.assertAlmostEqual(v, first_row[n])
        #self.assertEqual(expected_dict, df.ix[0].to_dict())
        self.assertEqual(14*24*12+1, len(df)) # End is inclusive of midnight
