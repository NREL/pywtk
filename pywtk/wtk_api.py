import csv
import h5py
import logging
import math
import netCDF4
import numpy
import os
import pandas
from tempfile import NamedTemporaryFile
from zipfile import ZipFile

from pywtk.site_lookup import get_3tiersites_from_wkt, timezones, sites

_logger = logging.getLogger(__name__)
# logging.basicConfig(level=logging.INFO)
FORECAST_ATTRS = [ "day_ahead_power", "hour_ahead_power", "4_hour_ahead_power",
                   "6_hour_ahead_power", "day_ahead_power_p90", "hour_ahead_power_p90",
                   "4_hour_ahead_power_p90", "6_hour_ahead_power_p90", "day_ahead_power_p10",
                   "hour_ahead_power_p10", "4_hour_ahead_power_p10", "6_hour_ahead_power_p10"]
# Order per output csvfile from website
# density at hub height (kg/m^3),power (MW),surface air pressure (Pa),air
# temperature at 2m (K),wind direction at 100m (deg),wind speed at 100m (m/s)
MET_ATTRS = ['density', 'power', 'pressure', 'temperature', 'wind_direction',
               'wind_speed']
S3_BUCKET = "nrel-pds-wtk"
S3_KEYDIR = "wtk-techno-economic/pywtk-data"
if 'PYWTK_CACHE_DIR' in os.environ:
    # Set FCST and MET dirs appropriately
    WIND_MET_NC_DIR = os.path.join(os.environ['PYWTK_CACHE_DIR'], "met_data")
    WIND_FCST_DIR = os.path.join(os.environ['PYWTK_CACHE_DIR'], "fcst_data")
    # HDF data not available in bucket yet
    WIND_MET_DIR = os.path.join(os.environ['PYWTK_CACHE_DIR'], "hdf")
    # Check for existing cache directories
    for req_dir in [WIND_MET_NC_DIR, WIND_FCST_DIR]:
        if not os.path.exists(req_dir):
            # Warn that cache dir is being created
            _logger.warning("Creating cache dir %s"%req_dir)
            os.makedirs(req_dir)
else:
    # HPC directories
    WIND_MET_NC_DIR = "/projects/hpc-apps/wtk/data/met_data"
    WIND_FCST_DIR = "/projects/hpc-apps/wtk/data/fcst_data"
    WIND_MET_DIR = "/projects/hpc-apps/wtk/data/hdf"

H5_AVAILABLE_DATA_INTERVALS = [5, 60] #??? defined in two places with different values
# name of the dataset containing time stamps
H5_TIME_INDEX_NAME = 'time_index'
# native data interval in minutes
H5_DATA_INTERVAL = 60
# array of all intervals chosen for exposure to the client for this H5 data (must be increments of H5_DATA_INTERVAL)
H5_AVAILABLE_DATA_INTERVALS = [60]

def get_wind_data_by_wkt(wkt, names, attributes=None, interval=5, leap_day=True,
                  utc=False, dataset="met"):
    '''Duplicate functionality of URL data grabber at
    https://mapsbeta.nrel.gov/api/developer_proxy

    The data in both the condensed hdf and original nc files are in UTC

    Required Args:
        wkt - (String) Well Known Text describing a point of area for use in GIS
              mapping to wind sites
        names - (List of Strings) List of year names

    Optional Args:
        attributes - (String or List of Strings) List of attributes to retrieve
                      from the database.  Limited to MET_ATTRS.
        interval - Limited to H5_AVAILABLE_DATA_INTERVALS
        leap_day - (boolean) Include leap day data or remove it.  Defaults to
                   True, include leap day data
        utc - (boolean) Keep as UTC or convert to local time.  Defaults to local
        dataset - (String) Dataset to retrieve, met or forecast.  Defaults to met

    Returns:
        dict of site_id to Pandas dataframe containing requested data
    '''
    if dataset == "met":
        data_dir = WIND_MET_NC_DIR
    elif dataset == "forecast":
        data_dir = WIND_FCST_DIR
    else:
        raise Exception("Invalid data to retrieve: %s"%type)
    ret_dict = {}
    for site_id in get_3tiersites_from_wkt(wkt).index.values:
        site_tz = timezones.iloc[site_id]['zoneName']
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
            #ret_df = ret_df.append(data_function(site_id, min_dt, max_dt, attributes, leap_day, utc))
            #ret_df = ret_df.append(get_nc_data(site_id, min_dt, max_dt, attributes, leap_day, utc, data_dir))
            ret_df = pandas.concat([ret_df, get_nc_data(site_id, min_dt, max_dt, attributes, leap_day, utc, data_dir)], ignore_index=True)
        ret_dict[site_id] = ret_df
        # Break on POINT as it will return all sites in order of distance to the
        # wkt point
        if 'POINT' in wkt:
            break
    return ret_dict

def get_wind_data(site_id, start, end, attributes=None, leap_day=True, utc=False, source="hdf"):
    '''Retrieve wind data for a specific site for a range of times

    Required Args:
        site_id - (String or int) Wind site id
        start - (pandas.Timestamp) Timestamp for start of data
        end - (pandas.Timestamp) Timestamp for end of data
        names - (List of Strings) List of year names

    Optional Args:
        attributes - (String or List of Strings) List of attributes to retrieve
                      from the database.  Limited to MET_ATTRS.  Defaults to
                      all available.
        leap_day - (boolean) Include leap day data or remove it.  Defaults to
                   True, include leap day data
        utc - (boolean) Keep as UTC or convert to local time.  Defaults to local
        source - (String) Source of data to retrieve, either "nc" or "hdf".  Defaults to "hdf"

    Returns:
        Pandas dataframe containing requested data
    '''
    site_id = int(site_id)
    if attributes is None:
        attributes = MET_ATTRS
    site_tz = timezones.iloc[site_id]['zoneName']
    _logger.info("Site %s is in %s", site_id, site_tz)
    ret_df = pandas.DataFrame()
    _logger.info("utc is %s", utc)
    min_dt = start.tz_convert('utc')
    max_dt = end.tz_convert('utc')
    _logger.info("After conversion dates are %s to %s", min_dt, max_dt)
    if source == "hdf":
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
                # ret_df = ret_df.append(year_df)
                ret_df = pandas.concat([ret_df, year_df], ignore_index=True)
        if leap_day == False:
            ret_df = ret_df[~((ret_df.index.month == 2) & (ret_df.index.day == 29))]
    elif source == "nc":
        ret_df = get_nc_data(site_id, start, end, attributes, leap_day, utc, nc_dir=WIND_MET_NC_DIR)
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

def get_nc_data(site_id, start, end, attributes=None, leap_day=True, utc=False, nc_dir=WIND_FCST_DIR):
    '''Retrieve nc data for a specific site for a range of times from a directory
       that matches forecast and met layouts.

    Required Args:
        site_id - (String or int) Wind site id
        start - (pandas.Timestamp) Timestamp for start of data
        end - (pandas.Timestamp) Timestamp for end of data

    Optional Args:
        attributes - (List of Strings) List of attributes to retrieve
                      from the database.  Limited to FORECAST_ATTRS.  Defaults to
                      all available.
        leap_day - (boolean) Include leap day data or remove it.  Defaults to
                   True, include leap day data
        utc - (boolean) Keep as UTC or convert to local time.  Defaults to local
        nc_dir - (String) Directory containing site nc files in specific layout,
                 Defaults to WIND_FCST_DIR, WIND_MET_NC_DIR is where met data is
                 stored in nc format.  Can work with s3:// URLs but attributes
                 must be passed in.

    Returns:
        Pandas dataframe containing requested data
    '''
    if attributes is None:
        if nc_dir == WIND_FCST_DIR:
            attributes = FORECAST_ATTRS
        elif nc_dir == WIND_MET_NC_DIR:
            attributes = MET_ATTRS
    site = int(site_id)
    if nc_dir.startswith("s3://"):
        import boto3
        from botocore import UNSIGNED
        from botocore.client import Config
        s3 =  boto3.client('s3', config=Config(signature_version=UNSIGNED))
        (bucket, directory) = nc_dir[5:].split("/", 1)
        key = os.path.join(directory, str(int(site/500)), "%s.nc"%site)
        _logger.info("Attempting to download from s3 bucket %s key %s", bucket, key)
        with NamedTemporaryFile(suffix="%s.nc"%site) as tfile:
            s3.download_file(Bucket=bucket, Key=key, Filename=tfile.name)
            #s3.download_fileobj(Bucket="pywtk-data", Key="met_data/0/90.nc", Fileobj=tfile)
            data = get_nc_data_from_file(tfile.name, start, end, attributes=attributes, leap_day=leap_day, utc=utc, site_id=site)
        return data
    elif "PYWTK_CACHE_DIR" in os.environ:
        site_file = site_from_cache(site, nc_dir)
    else:
        site_file = os.path.join(nc_dir, str(int(site/500)), "%s.nc"%site)
    _logger.info("Site file %s", site_file)
    return get_nc_data_from_file(site_file, start, end, attributes=attributes, leap_day=leap_day, utc=utc)

def get_nc_data_from_file(filename, start, end, attributes=None, leap_day=True, utc=False, site_id=None):
    '''Retrieve nc data from a file for a range of times that matches forecast
        and met layouts.

    Required Args:
        filename - (String) Location of nc file
        start - (pandas.Timestamp) Timestamp for start of data
        end - (pandas.Timestamp) Timestamp for end of data

    Optional Args:
        attributes - (List of Strings) List of attributes to retrieve
                      from the database.
        leap_day - (boolean) Include leap day data or remove it.  Defaults to
                   True, include leap day data
        utc - (boolean) Keep as UTC or convert to local time.  Defaults to local
        nc_dir - (String) Directory containing site nc files in specific layout,
                 Defaults to WIND_FCST_DIR, WIND_MET_NC_DIR is where met data is
                 stored in nc format.
        site_id - (String or int) Wind site id.  If not provided, this will be
                  pulled from the filename.

    Returns:
        Pandas dataframe containing requested data
    '''
    # Get timezone from filename.  Assume site_id.nc as the site_id is not part
    # of the dataset
    site_tz = None
    filedir, filebase = os.path.split(filename)
    if site_id:
        site = int(site_id)
    else:
        try:
            site_id = filebase[:-3]
            site = int(site_id)
        except:
            raise Exception("Unable to determine site id from filename, should be format of site_id.nc")
    site_tz = timezones.iloc[site]['zoneName']
    _logger.info("Site %s is in %s", site_id, site_tz)
    if utc == False and site_tz is None:
        raise Exception("Use utc=True for sites without defined timezones")
    nc = netCDF4.Dataset(filename)
    data_size = nc.dimensions['time'].size
    _logger.info("Site data points %s", data_size)
    min_dt = start.tz_convert('utc')
    max_dt = end.tz_convert('utc')
    _logger.info("After conversion dates are %s to %s", min_dt, max_dt)
    start_time = min_dt.value // 10 ** 9
    end_time = max_dt.value // 10 ** 9
    # Convert the min_dt and max_dt to match the sample_period, getting the data indexes
    start_idx = max(0, int(math.ceil((start_time - nc.start_time)/float(nc.sample_period))))
    end_idx = min(data_size, int(math.floor((end_time - nc.start_time)/float(nc.sample_period))) + 1)
    _logger.info("Reading %s:%s", start_idx, end_idx)
    ret_df = pandas.DataFrame()
    ret_df['datetime'] = numpy.arange((nc.start_time + start_idx * float(nc.sample_period)) * 10 ** 9,
                                      (nc.start_time + end_idx * float(nc.sample_period)) * 10 ** 9,
                                      float(nc.sample_period) * 10 ** 9)
    # Someone with better pandas skills will code this nicer
    ret_df.index = pandas.to_datetime(ret_df.pop('datetime'))
    ret_df.index = ret_df.index.tz_localize('utc')
    if not utc:
        ret_df.index = ret_df.index.tz_convert(site_tz)
    _logger.info("Attributes are %s", attributes)
    for atrb in attributes:
        ret_df[atrb] = nc[atrb][start_idx:end_idx]
    if not leap_day:
        ret_df = ret_df[~((ret_df.index.month == 2) & (ret_df.index.day == 29))]
    return ret_df

# Backwards compatability
get_forecast_data = get_nc_data

def get_nc_data_from_url(url, site_id, start, end, attributes, leap_day=True, utc=False):
    '''Retrieve nc data from a URL for a range of times that matches forecast
        and met layouts.  Pieces together multiple lambda calls assuming 500k
        per attribute per month.

    Required Args:
        url - (String) url of flask service
        site_id - (String or int) Wind site id.
        start - (pandas.Timestamp) Timestamp for start of data
        end - (pandas.Timestamp) Timestamp for end of data
        attributes - (List of Strings) List of attributes to retrieve from the
                     nc file.

    Optional Args:
        leap_day - (boolean) Include leap day data or remove it.  Defaults to
                   True, include leap day data
        utc - (boolean) Keep as UTC or convert to local time.  Defaults to local

    Returns:
        Pandas dataframe containing requested data
    '''
    # Chunk attributes, keep attributes together for easy stitching of times
    # Response for lambda maxes at 6MB, one month of one attribute is ~500kB
    # TODO: fcst or met have different sizes
    start_ts = start.value//10**9
    end_ts = end.value//10**9
    # Calculate time / chunk = 6MB/chunk / SPP B/ data point / (num attributes + datetime) data points / time step * time per step
    if url.endswith("fcst"):
        # Forecast is about 33 bytes per data point per attribute (datetime is one)
        #          has one data point per hour
        data_points = (end_ts - start_ts) / 3600
        time_per_step = 3600
        bytes_per_dp = 34
    else:
        # Met is about 25 bytes per data point per attribute (datetime is one)
        #     has one data point per 5 minutes
        time_per_step = 300
        data_points = (end_ts - start_ts) / 300
        bytes_per_dp = 26
    # AWS Lambda limit says 6MB, more like 4MB in real testing
    #chunk_size = 6000000 / bytes_per_dp / (len(attributes) + 1) * time_per_step
    chunk_size = int(4000000 / bytes_per_dp / (len(attributes) + 1) * time_per_step)
    # TODO: Support leap day
    import requests
    #MAX_CHUNK = 12 * (60 * 60 * 24 * 30) # Seconds
    #chunk_size = MAX_CHUNK / len(attributes)
    _logger.info("Breaking into %s requests", (end_ts - start_ts)/chunk_size + 1)
    # Pull data for each chunk into the master json object
    master_data = []
    end_chunk = min(start_ts + chunk_size, end_ts)
    params = {"start":start_ts, "end":end_chunk, "attributes":",".join(attributes), "sites":site_id}
    while True:
        resp = requests.get(url, params=params)
        # TODO: Check for bad reply
        _logger.info("params %s", params)
        #_logger.info("response %s", resp.text)
        resp_json = resp.json()
        if str(site_id) not in resp_json:
            raise Exception(resp.text)
        _logger.info("first entry %s"%resp_json[str(site_id)][0])
        _logger.info("last entry %s"%resp_json[str(site_id)][-1])

        master_data += resp_json[str(site_id)]
        if end_chunk == end_ts:
            break
        params["start"] = end_chunk + 1
        end_chunk = min(end_chunk + chunk_size, end_ts)
        params["end"] = end_chunk
    # Create dataframe from json object
    master_df = pandas.DataFrame(master_data)
    # Convert timestamp and index
    master_df.index = pandas.to_datetime(master_df.pop('datetime')*10**6)
    master_df.index = master_df.index.tz_localize('utc')
    master_df = master_df[attributes]
    #master_df.set_index(pandas.DatetimeIndex(master_df["datetime"]*10**6))
    # Return dataframe
    return master_df

def site_from_cache(site_id, nc_dir):
    '''Retrieve site file from cache, downloading from S3 if needed
    Required Args:
        site_id - (String or int) Wind site id.
        nc_dir - Directory to check for data

    Returns:
        String path for site data file
    '''
    if "PYWTK_CACHE_DIR" not in os.environ:
        raise Exception("Set environment variable PYWTK_CACHE_DIR to utilize the cache")
    site_id = int(site_id)
    import boto3
    from botocore import UNSIGNED
    from botocore.client import Config
    _logger.info("site_from_cache: nc_dir is %s", nc_dir)
    s3 = boto3.client('s3', config=Config(signature_version=UNSIGNED))
    site_file = os.path.join(nc_dir, str(int(site_id/500)), "%s.nc" % site_id)
    site_file_unix = site_file.replace("\\", "/")
    # Check for file in nc_dir
    if not os.path.exists(site_file):
        _logger.warning("Downloading missing file %s"%site_file)
        key = S3_KEYDIR + '/' + site_file_unix[len(os.environ['PYWTK_CACHE_DIR']):].lstrip("/\\")
        site_path = os.path.dirname(site_file)
        if not os.path.exists(site_path):
            _logger.info("Creating missing directory %s"%site_path)
            os.makedirs(site_path)
        # Download if missing to nc_dir
        s3.download_file(Bucket=S3_BUCKET, Key=key, Filename=site_file)
    return site_file
