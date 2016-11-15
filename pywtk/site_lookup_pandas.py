'''Loads site metadata and timezone from files and provides searches for nearest
site to a point and a list of sites within a sshape'''
import csv
import logging
import os
import pandas
import psycopg2
import psycopg2.extras
from shapely import wkb, wkt
from shapely.geometry import Point
import time
import traceback

_logger = logging.getLogger(__name__)
#logging.basicConfig(level=logging.DEBUG)

_dir = os.path.dirname(__file__)
# Loading the module will read in the file and create the Points as they
# will not change
tstart = time.time()
sites = pandas.read_csv(os.path.join(_dir, 'three_tier_site_metadata.csv'), index_col=1)
sites['point'] = sites['the_geom'].apply(wkb.loads, hex=True)
_logger.info("Loaded %s sites in %s seconds", len(sites), time.time()-tstart)
tstart = time.time()
timezones = pandas.read_csv(os.path.join(_dir, 'site_timezone.csv'), index_col=0)
_logger.info("Loaded %s timezones in %s seconds", len(timezones), time.time()-tstart)


def get_3tiersites_from_wkt(wkt_str):
    '''Retrieve 3tier windsites from wkt

    Returns: Dataframe of sites sorted by distance to point or within a polygon
    '''
    shape = wkt.loads(wkt_str)
    if 'POINT' in wkt_str:
        sites['distance'] = sites['point'].apply(shape.distance)
        ret_sites = sites.sort_values('distance', ascending=True)
    else:
        ret_sites = sites.loc[lambda df: df['point'].apply(shape.contains), :].copy()
    return ret_sites
