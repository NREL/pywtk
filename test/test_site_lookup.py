import csv
from unittest import TestCase
from zipfile import ZipFile

from site_lookup import get_3tiersites_from_wkt, get_3tiersites_from_postgis

class SiteLookupTest(TestCase):
    def test_point_metadata(self):
        '''Validate return of the nearest point to a WKT using metadata
        '''
        wkt = "POINT(-103.128662109375 40.24179856487036)"
        nearest_site = get_3tiersites_from_wkt(wkt)
        expected_meta = dict(zip(["gid","site_id","fraction_of_usable_area","power_curve","capacity","wind_speed","capacity_factor","the_geom","city","state","country","elevation"],
                ["53253","53252","1.0","2","16.0","7.98","0.413","0101000020E6100000C5707500C4C259C0D07CCEDDAE394440","","Colorado","United States",]))
        #print nearest_site
        self.assertEqual(expected_meta['site_id'], nearest_site['site_id'])

    def test_point_postgis(self):
        '''Validate return of the nearest point to a WKT using postgis
        '''
        wkt = "POINT(-103.128662109375 40.24179856487036)"
        nearest_site = get_3tiersites_from_postgis(wkt)
        expected_meta = dict(zip(["gid","site_id","fraction_of_usable_area","power_curve","capacity","wind_speed","capacity_factor","the_geom","city","state","country","elevation"],
                ["53253","53252","1.0","2","16.0","7.98","0.413","0101000020E6100000C5707500C4C259C0D07CCEDDAE394440","","Colorado","United States",]))
        print nearest_site.items()
        self.assertEqual(expected_meta['site_id'], str(nearest_site['site_id']))
