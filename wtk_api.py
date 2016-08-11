import csv
import h5py
import netCDF4
import os
import numpy
import pandas
import psycopg2

from site_lookup import get_3tiersites_from_wkt

#VALID_ATTRS = set(['wind_speed', 'wind_direction', 'power', 'temperature',
#                  'pressure', 'density'])
# Order per output csvfile from website
# density at hub height (kg/m^3),power (MW),surface air pressure (Pa),air
# temperature at 2m (K),wind direction at 100m (deg),wind speed at 100m (m/s)
VALID_ATTRS = ['density', 'power', 'pressure', 'temperature', 'wind_direction',
               'wind_speed']
WIND_MET_DIR = "/projects/hpc-apps/wtk/data/hdf"
WIND_NC_DIR = "/projects/hpc-apps/wtk/data/met_data"

H5_AVAILABLE_DATA_INTERVALS = [5, 60] #??? defined in two places with different values
# name of the dataset containing time stamps
H5_TIME_INDEX_NAME = 'time_index'
# native data interval in minutes
H5_DATA_INTERVAL = 60
# array of all intervals chosen for exposure to the client for this H5 data (must be increments of H5_DATA_INTERVAL)
H5_AVAILABLE_DATA_INTERVALS = [60]

def get_wind_data(wkt, names, attributes=None, interval=5, leap_day=False,
                  utc=False, save_to_zip=None):
    '''Duplicate functionality of URL data grabber at
    https://mapsbeta.nrel.gov/api/developer_proxy

    Required Args:
        wkt - (String) Well Known Text describing a point of area for use in GIS
              mapping to wind sites
        names - (List of Strings) List of year names

    Optional Args:
        attributes - (String or List of Strings) List of attributes to retrieve
                      from the database.  Limited to VALID_ATTRS.
        interval - Limited to H5_AVAILABLE_DATA_INTERVALS
        leap_day - Not sure
        utc - Convert to local time or keep as UTC
        save_to_zip - (String) If this string is defined, save wind data to zip
                      file

    Returns:
        Pandas dataframe containing requested data
    '''
    sites = get_3tiersites_from_wkt(wkt)
    # TODO: Multiple sites support
    site_id = int(sites['site_id'])
    ret_df = pandas.DataFrame()
    for year in names:
        # TODO: Sort years, append data on multi year queries
        with h5py.File(WIND_MET_DIR+"/wtk_%s.h5"%year, "r") as h5_file:
            ret_df['datetime'] = h5_file[H5_TIME_INDEX_NAME][:]
            #print "%s len is %s"%('datetime', len(h5_file[H5_TIME_INDEX_NAME][:]))
            for attr in attributes:
                #print "%s len is %s"%(attr, len(h5_file[attr][site_id][:]))
                scale = h5_file[attr].attrs['scale_factor']
                ret_df[attr] = h5_file[attr][:,site_id] * scale
            #get_timestamp_data(HDF5Dataset.get_dataset(h5_file, self.class::H5_TIME_INDEX_NAME, false), name)
        #read_datetime = pandas.read_hdf(WIND_MET_DIR+"/wtk_%s.h5"%year, '/time_index')#, columns=['datetime'])
        # These files do not conform to pandas hdf5 standards
        #store = pandas.HDFStore(WIND_MET_DIR+"/wtk_%s.h5"%year, "r")
        #read_
    if save_to_zip is not None:
        # TODO: Start with zip
        # TODO: Handle multiple sites
        with open(save_to_zip, 'w') as csvfile:
            wtk_writer = csv.writer(csvfile)
            wtk_writer.writerow(["SiteID", sites['site_id']])
            wtk_writer.writerow(["Longitude", sites['Longitude']])
            wtk_writer.writerow(["Latitude", sites['Latitude']])
            # Header data
            # Each row


    return ret_df

def get_nc_data(site, start_time, end_time, attributes=None, leap_day=False,
                utc=False):
    '''Return site data within the times from the netcdf files

    Required Args:
        site - (int) Site identifier
        start_time - (int) Unix timestamp of start
        end_time - (int) Unix timestamp of end

    Optional Args:
        attributes - (String or List of Strings) List of attributes to retrieve
                      from the database.  Limited to VALID_ATTRS.
        TBD interval - Limited to H5_AVAILABLE_DATA_INTERVALS
        leap_day - Include leap day in data TODO: IMPLEMENT
        utc - Convert to local time or keep as UTC

    Returns:
        Pandas dataframe containing requested data
    '''
    site_file = os.path.join(WIND_NC_DIR, str(site/500), "%s.nc"%site)
    print "site file %s"%site_file
    nc = netCDF4.Dataset(site_file)
    first_dp = int((start_time - nc.start_time)/nc.sample_period)
    last_dp = int((end_time - nc.start_time)/nc.sample_period) + 1
    print "Reading %s:%s"%(first_dp,last_dp)
    ret_df = pandas.DataFrame()
    ret_df['timestamp'] = numpy.arange(start_time, end_time + 1, int(nc.sample_period))
    for attr in attributes:
        ret_df[attr] = nc[attr][first_dp:last_dp]
    return ret_df


#def get_3tiersites_from_wkt(wkt):
    '''Return list of sites data within the geometry defined in wtk

    Args:
        wkt - (String) Well Known Text describing a point of area for use in GIS
              mapping to wind sites
    Returns:
        List of site data dicts
    '''
    '''
    try:
        conn = psycopg2.connect("dbname='opencarto_development', user='opencarto_app', host='maps-dev-db.nrel.gov', password='I7uHpKulUVkOatClZ7UF'")
    except:
        print "Database connection unavailable"
        return None
    cur = conn.cursor()
    attributes = ('hdf5_id, site_id, fraction_of_usable_area, power_curve, '
                  'capacity, wind_speed, capacity_factor, state, country, '
                  'ST_X(the_geom) as lon, ST_Y(the_geom) as lat')
    table_name = 'wind_prospector.three_tier_site_metadata'
    geometry_column = 'the_geom'
    if 'POINT' in wkt:
        cmd = """SELECT {0} FROM {1} WHERE ST_DWithin({2}, ST_GeomFromText({3}, 4326), 1)
                 ORDER BY ST_Distance({2}, ST_GeomFromText({3}, 4326))
                 LIMIT 1""".format(attributes, table_name, geometry_column, wkt)
    else:
        cmd = """SELECT {0} FROM {1} WHERE ST_Intersects({2}, ST_GeomFromText({3}, 4326), 1)
                 ORDER BY site_id
                 LIMIT 50000""".format(attributes, table_name, geometry_column, wkt)
    print "Querying metadata with '%s'"%cmd
    cur.execute(cmd)
    '''
