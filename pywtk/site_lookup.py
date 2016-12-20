'''Loads site metadata and timezone from files and provides searches for nearest
site to a point and a list of sites within a shape'''
import csv
import logging
import os
import psycopg2
import psycopg2.extras
from shapely import wkb, wkt
from shapely.geometry import Point
import time
import traceback

_logger = logging.getLogger(__name__)
_dir = os.path.dirname(__file__)
# Loading the module will read in the file and create the Points as they
# will not change
tstart = time.time()
sites = {}
with open(os.path.join(_dir, 'three_tier_site_metadata.csv')) as csvfile:
    metadata = csv.DictReader(csvfile)
    for row in metadata:
        point = wkb.loads(row['the_geom'], hex=True)
        row['point'] = point
        sites[row['site_id']] = row
_logger.info("Loaded %s sites in %s seconds", len(sites), time.time()-tstart)
tstart = time.time()
timezones = {}
with open(os.path.join(_dir, 'site_timezone.csv')) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        timezones[row['site_id']] = row
_logger.info("Loaded %s timezones in %s seconds", len(timezones), time.time()-tstart)


def get_3tiersites_from_wkt(wkt_str):
    '''Retrieve 3tier windsite ids from wkt

    Returns: List of site_id Strings representing those closest to point or
             within a polygon'''
    ret_sites = []
    if 'POINT' in wkt_str:
        point = wkt.loads(wkt_str)
        min_dist, min_key = min((point.distance(v['point']), k) for (k, v) in sites.items())
        ret_sites.append(min_key)
    else:
        rect = wkt.loads(wkt_str)
        ret_sites = [k for (k,v) in sites.items() if rect.contains(v['point'])]
    return ret_sites


def get_3tiersites_from_postgis(wkt):
    '''Return list of sites data within the geometry defined in wtk from postgis
        Kept as a simple test of existing functionality on the website, not to
        be used for production
    Args:
        wkt - (String) Well Known Text describing a point of area for use in GIS
              mapping to wind sites
    Returns:
        List of site_id dicts representing those closest to point or within a
        polygon
    '''
    try:
        conn = psycopg2.connect("dbname=opencarto_development user=opencarto_app host=maps-dev-db.nrel.gov password=I7uHpKulUVkOatClZ7UF")
    except:
        _logger.error("Database connection unavailable", exc_info=1)
        traceback.print_exc()
        return None
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    attributes = ('hdf5_id, site_id, fraction_of_usable_area, power_curve, '
                  'capacity, wind_speed, capacity_factor, state, country, '
                  'ST_X(the_geom) as lon, ST_Y(the_geom) as lat')
    table_name = 'wind_prospector.three_tier_site_metadata'
    geometry_column = 'the_geom'
    if 'POINT' in wkt:
        cmd = """SELECT {0} FROM {1} WHERE ST_DWithin({2}, ST_GeomFromText('{3}', 4326), 1)
                 ORDER BY ST_Distance({2}, ST_GeomFromText('{3}', 4326))
                 LIMIT 1""".format(attributes, table_name, geometry_column, wkt)
    else:
        cmd = """SELECT {0} FROM {1} WHERE ST_Intersects({2}, ST_GeomFromText({3}, 4326), 1)
                 ORDER BY site_id
                 LIMIT 50000""".format(attributes, table_name, geometry_column, wkt)
    _logger.info("Querying metadata with '%s'", cmd)
    cur.execute(cmd)
    matching_sites = list(cur.fetchall())
    return matching_sites
