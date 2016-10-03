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
        self.assertEqual(1, len(nearest_site))
        self.assertEqual(expected_meta['site_id'], nearest_site[0])

    def test_point_postgis(self):
        '''Validate return of the nearest point to a WKT using postgis
        '''
        wkt = "POINT(-103.128662109375 40.24179856487036)"
        nearest_site = get_3tiersites_from_postgis(wkt)
        expected_meta = dict(zip(["gid","site_id","fraction_of_usable_area","power_curve","capacity","wind_speed","capacity_factor","the_geom","city","state","country","elevation"],
                ["53253","53252","1.0","2","16.0","7.98","0.413","0101000020E6100000C5707500C4C259C0D07CCEDDAE394440","","Colorado","United States",]))
        #print nearest_site.items()
        self.assertEqual(expected_meta['site_id'], str(nearest_site[0]['site_id']))

    def test_rectangle(self):
        '''Validate return of multiple sites within a rectangle using metadata
        '''
        #https://mapsbeta.nrel.gov/api/developer_proxy?wkt=POLYGON((-120.82763671875+34.452218472826566%2C-119.19616699218749+34.452218472826566%2C-119.19616699218749+33.920571528675104%2C-120.82763671875+33.920571528675104%2C-120.82763671875+34.452218472826566))&attributes=power%2Ctemperature&names=2012&site_url=wind-toolkit%2Fwind%2Fwtk_download.json&full_name=Harry+Sorensen&email=harry.sorensen%40nrel.gov&affiliation=NREL&mailing_list=false&reason=Development+testing&leap_day=true&utc=true
        wkt = "POLYGON((-120.82763671875 34.452218472826566,-119.19616699218749 34.452218472826566,-119.19616699218749 33.920571528675104,-120.82763671875 33.920571528675104,-120.82763671875 34.452218472826566))"
        sites = get_3tiersites_from_wkt(wkt)
        from_zip = [29375, 29733, 29872, 30019, 30190, 30539, 30712, 30713,
                    30873, 30874, 31032, 31033, 31034, 31189, 31190, 31191,
                    31192, 31320, 31321, 31322, 31323, 31324, 31563, 32060,
                    32314, 32834, 33203, 34828]
        expected = set([str(x) for x in from_zip])
        self.assertEqual(expected, set(sites))
