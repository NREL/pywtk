from unittest import TestCase

from pywtk.site_lookup import get_3tiersites_from_wkt

class SiteLookupTest(TestCase):
    def test_point_metadata(self):
        '''Validate pandas return of sites ordered by distance to the nearest point to
        a WKT using metadata
        '''
        wkt = "POINT(-103.128662109375 40.24179856487036)"
        result = get_3tiersites_from_wkt(wkt)
        self.assertEqual(53252, result.index[0])

    def test_rectangle(self):
        '''Validate pandas return of multiple sites within a rectangle using metadata
        '''
        #https://mapsbeta.nrel.gov/api/developer_proxy?wkt=POLYGON((-120.82763671875+34.452218472826566%2C-119.19616699218749+34.452218472826566%2C-119.19616699218749+33.920571528675104%2C-120.82763671875+33.920571528675104%2C-120.82763671875+34.452218472826566))&attributes=power%2Ctemperature&names=2012&site_url=wind-toolkit%2Fwind%2Fwtk_download.json&full_name=Harry+Sorensen&email=harry.sorensen%40nrel.gov&affiliation=NREL&mailing_list=false&reason=Development+testing&leap_day=true&utc=true
        wkt = "POLYGON((-120.82763671875 34.452218472826566,-119.19616699218749 34.452218472826566,-119.19616699218749 33.920571528675104,-120.82763671875 33.920571528675104,-120.82763671875 34.452218472826566))"
        sites = get_3tiersites_from_wkt(wkt)
        from_zip = [29375, 29733, 29872, 30019, 30190, 30539, 30712, 30713,
                    30873, 30874, 31032, 31033, 31034, 31189, 31190, 31191,
                    31192, 31320, 31321, 31322, 31323, 31324, 31563, 32060,
                    32314, 32834, 33203, 34828]
        #expected = set([str(x) for x in from_zip])
        self.assertEqual(set(from_zip), set(sites.index))
