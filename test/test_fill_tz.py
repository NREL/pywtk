import csv
from unittest import TestCase, skip

class TimezoneTest(TestCase):
    @skip('Will modify existing data')
    def test_tz_for_site(self):
        '''Validate timezone for sites
        '''
        from fill_tz import fill_tz, get_tz_for_site, save_tz_to_file
        #SiteID, 102445.0
        #Longitude, -70.708649
        #Latitude, 41.744591
        tz = get_tz_for_site("102445")
        print tz
        save_tz_to_file("output_test_tz_for_site.csv")
        # This command will loop forever
        fill_tz("site_timezone.csv")
