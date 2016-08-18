import csv
import h5py
import logging
import netCDF4
import os
import numpy
import pandas
import psycopg2
from tempfile import NamedTemporaryFile
from zipfile import ZipFile

from site_lookup import get_3tiersites_from_wkt, timezones, sites

_logger = logging.getLogger(__name__)
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

def get_wind_data_by_wkt(wkt, names, attributes=None, interval=5, leap_day=False,
                  utc=False):
    '''Duplicate functionality of URL data grabber at
    https://mapsbeta.nrel.gov/api/developer_proxy

    The data in both the condensed hdf and original nc files are in UTC

    Required Args:
        wkt - (String) Well Known Text describing a point of area for use in GIS
              mapping to wind sites
        names - (List of Strings) List of year names

    Optional Args:
        attributes - (String or List of Strings) List of attributes to retrieve
                      from the database.  Limited to VALID_ATTRS.
        interval - Limited to H5_AVAILABLE_DATA_INTERVALS
        leap_day - Not sure
        utc - Keep as UTC or convert to local time

    Returns:
        Pandas dataframe containing requested data
    '''
    matching_sites = get_3tiersites_from_wkt(wkt)
    # TODO: Multiple sites support
    site_id = matching_sites['site_id']
    site_tz = timezones[matching_sites['site_id']]['zoneName']
    _logger.info("Site %s is in %s", site_id, site_tz)
    ret_df = pandas.DataFrame()
    for year in names:
        if utc == False:
            # Min datetime in UTC
            min_dt = pandas.Timestamp('%s-01-01'%year, tz=site_tz).tz_convert('utc')
            # Max datetime in UTC
            max_dt = pandas.Timestamp('%s-12-31 23:59:59'%year, tz=site_tz).tz_convert('utc')
        else:
            min_dt = pandas.Timestamp('%s-01-01'%year, tz='utc')
            max_dt = pandas.Timestamp('%s-12-31 23:59:59'%year, tz='utc')
        ret_df = ret_df.append(get_wind_data(site_id, min_dt, max_dt, attributes, leap_day, utc))
        '''print "After conversion dates are %s to %s"%(min_dt, max_dt)
        file_years = range(min_dt.year, max_dt.year+1)
        # Must pull data for each year from min_dt to max_dt
        for file_year in file_years:
            print "pulling in %s"%(file_year)
            year_df = pandas.DataFrame()
            with h5py.File(WIND_MET_DIR+"/wtk_%s.h5"%file_year, "r") as h5_file:
                year_df['datetime'] = h5_file[H5_TIME_INDEX_NAME][:]
                #year_df.index = pandas.to_datetime(year_df.pop('datetime'), format='%Y-%m-%d %H:%M:%S', utc=True)
                # Someone with better pandas skills will code this nicer
                year_df.index = pandas.to_datetime(year_df.pop('datetime'))
                year_df.index = year_df.index.tz_localize('utc')
                #print (year_df.index[0].__repr__())
                #print (year_df.index[0].tz_localize('utc').__repr__())
                #print (year_df.index[0].__repr__())
                #year_df.index.tz_localize('utc')
                if utc == False:
                    year_df.index = year_df.index.tz_convert(site_tz)
                #print "%s len is %s"%('datetime', len(h5_file[H5_TIME_INDEX_NAME][:]))
                for attr in attributes:
                    #print "%s len is %s"%(attr, len(h5_file[attr][site_id][:]))
                    scale = h5_file[attr].attrs['scale_factor']
                    year_df[attr] = h5_file[attr][:,site_id] * scale
                #start_date = pandas.Timestamp('%s-01-01'%file_year)
                #end_date = pandas.Timestamp('%s-12-31 23:59:59'%file_year)
#                year_df = year_df.truncate(before=start_date, after=end_date)
                year_df = year_df.truncate(before=min_dt, after=max_dt)
                print "year_df shape is %s"%(repr(year_df.shape))
                ret_df = ret_df.append(year_df)
            #get_timestamp_data(HDF5Dataset.get_dataset(h5_file, self.class::H5_TIME_INDEX_NAME, false), name)
        #read_datetime = pandas.read_hdf(WIND_MET_DIR+"/wtk_%s.h5"%year, '/time_index')#, columns=['datetime'])
        # These files do not conform to pandas hdf5 standards
        #store = pandas.HDFStore(WIND_MET_DIR+"/wtk_%s.h5"%year, "r")
        #read_
'''


    return ret_df

def get_wind_data(site_id, start, end, attributes=None, leap_day=True, utc=False):
    '''Retrieve wind data for a specific site for a range of times

    Required Args:
        site_id - (String) Wind site id
        start - (pandas.Timestamp) Timestamp for start of data
        end - (pandas.Timestamp) Timestamp for end of data
        names - (List of Strings) List of year names

    Optional Args:
        attributes - (String or List of Strings) List of attributes to retrieve
                      from the database.  Limited to VALID_ATTRS.  Defaults to
                      all available.
        leap_day - (boolean) Include leap day data or remove it.  Defaults to
                   True, include leap day data
        utc - (boolean) Keep as UTC or convert to local time.  Defaults to local

    Returns:
        Pandas dataframe containing requested data
    '''
    if attributes is None:
        attributes = VALID_ATTRS
    site_tz = timezones[site_id]['zoneName']
    _logger.info("Site %s is in %s", site_id, site_tz)
    ret_df = pandas.DataFrame()
    _logger.info("utc is %s", utc)
    min_dt = start.tz_convert('utc')
    max_dt = end.tz_convert('utc')
    _logger.info("After conversion dates are %s to %s", min_dt, max_dt)
    file_years = range(min_dt.year, max_dt.year+1)
    # Must pull data for each year from start to end
    for file_year in file_years:
        if file_year < 2007 or file_year > 2012:
            _logger.info("Skipping year that has no data: %s", file_year)
            next
        _logger.info("pulling in %s"%(file_year))
        year_df = pandas.DataFrame()
        with h5py.File(WIND_MET_DIR+"/wtk_%s.h5"%file_year, "r") as h5_file:
            year_df['datetime'] = h5_file[H5_TIME_INDEX_NAME][:]
            # Someone with better pandas skills will code this nicer
            year_df.index = pandas.to_datetime(year_df.pop('datetime'))
            year_df.index = year_df.index.tz_localize('utc')
            if utc == False:
                year_df.index = year_df.index.tz_convert(site_tz)
            for attr in attributes:
                scale = h5_file[attr].attrs['scale_factor']
                year_df[attr] = h5_file[attr][:,int(site_id)] * scale
            year_df = year_df.truncate(before=min_dt, after=max_dt)
            _logger.info("year_df shape is %s", repr(year_df.shape))
            ret_df = ret_df.append(year_df)
    if leap_day == False:
        ret_df = ret_df[~((ret_df.index.month == 2) & (ret_df.index.day == 29))]
    return ret_df

def save_wind_data(datadict, zipfilename):
    '''Save the wind data to a csv file to match the download format at
    https://mapsbeta.nrel.gov/api/developer_proxy

    Required Args:
        datadict - (dict) Map of site ids to dataframe
        zipfilename - (Strings) Name of file to create zip archive
    '''
    with ZipFile(zipfilename, 'w') as zfile:
        # Each site and year gets its own csv file
        for (site_id, site_data) in datadict.iteritems():
            min_year = site_data.index.min().year
            max_year = site_data.index.max().year
            for cur_year in range(min_year, max_year+1):
                fname = "%s-%s.csv"%(site_id, cur_year)
                # Write each site, year Temp csv file
                with NamedTemporaryFile() as cur_file:
                    cur_data = site_data[site_data.index.year == cur_year]
                    wtk_writer = csv.writer(cur_file)
                    wtk_writer.writerow(["SiteID", site_id])
                    wtk_writer.writerow(["Longitude", sites[site_id]['point'].y])
                    wtk_writer.writerow(["Latitude", sites[site_id]['point'].x])
                    # Header data
                    cols = cur_data.columns.values.tolist()
                    wtk_writer.writerow(["Year", "Month", "Day", "Hour", "Minute"] + cols)
                    # Each row
                    for d, row in cur_data.iterrows():
                        this_row = [d.year, d.month, d.day, d.hour, d.minute] + list(row)
                        wtk_writer.writerow(this_row)
                    # Add to zip archive with name site-year.csv
                    zfile.write(cur_file.name, fname)

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
        utc - Convert to UTC or keep as local time

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
