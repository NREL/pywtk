pywtk on AWS
==============

Use of wtk data with a python interface on AWS

## How to deploy

1. Create a python virtual environment with requirements and code.  Must be done
on a Linux64 AWS VM due to custom compiled libraries.

    * Launch micro instance with AMI linux 64-bit and log in.

        ```bash
ssh -i keyfile.pem ec2-user@ec2-54-183-146-226.us-west-1.compute.amazonaws.com
sudo yum upgrade
sudo yum-config-manager --enable epel
sudo yum install git
sudo yum groupinstall "Development Tools"
sudo yum install geos-devel hdf5-devel zlib-devel libffi-devel openssl-devel
git clone https://github.com/NREL/pywtk.git
git checkout lambda
# Install python 3.6 with virtualenv
# 3.6 is used for pip fixes and is the only python3 environment used by lambda
# It has to be installed from source because there is no AMI package
wget https://www.python.org/ftp/python/3.6.1/Python-3.6.1.tgz
tar zxf Python-3.6.1.tgz
cd Python-3.6.1
./configure --prefix=$HOME/python3.6
make; make install
export PATH=$HOME/python3.6/bin:$PATH
virtualenv pywtk_virtenv
. pywtk_virtenv/bin/activate
pip install -r requirements.txt
# Patch zappa here
mkdir lib
cp /usr/lib64/libgeos-3.4.2.so /usr/lib64/libgeos_c.so.1.8.2.so lib
```

2. Setup AWS access
    * Go to the Amazon Console, select Users, your user, then the security credentials tab.
    * Create access key
    * run `aws configure` and fill in the data from the access key

3. Setup Lambda role
    * Go to the Amazon Console, select Roles, then Create
    * Add AWSLambdaExecute and AmazonS3ReadOnlyAccess Policies
    * Name the role "pywtk-lambda"

4. Create deployment zip and upload code to S3

    ```bash
(cd pywtk_virtenv/lib/python2.7/site-packages
    zip -r ../../../../pywtk_aws.zip dateutil pytz pywtk six.py)
(cd pywtk_virtenv/lib64/python2.7/site-packages
    zip -r ../../../../pywtk_aws.zip h5py netCDF4 numpy pandas shapely)
cp /usr/lib64/libgeos_c.so .
zip -r pywtk_aws.zip libgeos_c.so
aws s3 cp pywtk_aws.zip s3://pywtk-code/
```

5. Create lambda function

    ```bash
aws lambda create-function \
    --region us-west-2 \
    --function-name pywtk-api \
    --code S3Bucket=pywtk-code,S3Key=pywtk_aws.zip \
    --role arn:aws:iam::812847476558:role/pywtk-lambda \
    --handler pywtk.aws_lambda.handler \
    --runtime python2.7 \
    --timeout 10 \
    --environment Variables={DATA_BUCKET=pywtk-data} \
    --memory-size 1024
```

    * Update code

        ```bash
aws lambda update-function-code \
    --function-name pywtk-api \
    --s3-bucket pywtk-code \
    --s3-key pywtk_aws.zip
```

6. Wire lambda into API Gateway and test

    ```json
    {"type": "site",
 "sites": ["1001"]
}
```

## Example notebooks

On peregrine run the start_notebook.sh in the notebooks/ directory.  When accessing the notebook
for the first time, look for the token parameter in the URL that shows the server you have
access.  Otherwise you will be prompted for a password that won't work.

  ```bash
To view the notebook locally, run:
ssh -L 8888:n0290:8888 hpc-login1.hpc.nrel.gov
Then open your browser to http://localhost:8888/
[I 09:47:27.987 NotebookApp] [nb_conda_kernels] enabled, 13 kernels found
[I 09:47:35.463 NotebookApp] [nb_anacondacloud] enabled
[I 09:47:35.506 NotebookApp] [nb_conda] enabled
[I 09:47:36.242 NotebookApp] ✓ nbpresent HTML export ENABLED
[W 09:47:36.242 NotebookApp] ✗ nbpresent PDF export DISABLED: No module named nbbrowserpdf.exporters.pdf
[I 09:47:36.250 NotebookApp] Serving notebooks from local directory: /home/hsorense/projects/wind2plexos
[I 09:47:36.250 NotebookApp] 0 active kernels
[I 09:47:36.250 NotebookApp] The Jupyter Notebook is running at: http://0.0.0.0:8888/?token=c7c42d73e5e7954688873ab27c79207977c335829385b30d
```

## Available data and how to access it
* Wind site metadata

  ```bash
$ python -c "import pywtk.site_lookup; print(pywtk.site_lookup.sites.ix[11222])"
gid                                                                    11223
fraction_of_usable_area                                                    1
power_curve                                                                3
capacity                                                                  16
wind_speed                                                              7.34
capacity_factor                                                        0.411
the_geom                   0101000020E61000009414580053BA59C069FD2D01F857...
city                                                                     NaN
state                                                                  Texas
country                                                        United States
elevation                                                                NaN
point                                          POINT (-102.911316 32.687256)
Name: 11222, dtype: object
```
* Wind site timezones

  ```bash
$ python -c "import pywtk.site_lookup; print(pywtk.site_lookup.timezones.ix[11222])"
abbreviation                    CDT
countryCode                      US
nextAbbreviation                CST
timestamp                1470316655
dst                               1
dstStart                 1457856000
countryName           United States
gmtOffset                    -18000
dstEnd                   1478415600
zoneName            America/Chicago
Name: 11222, dtype: object
```
* Available met data attributes

  ```bash
$ python -c "import pywtk.wtk_api; print pywtk.wtk_api.MET_ATTRS"
['density', 'power', 'pressure', 'temperature', 'wind_direction', 'wind_speed']
```
* Available forecast data attributes

  ```bash
$ python -c "import pywtk.wtk_api; print pywtk.wtk_api.FORECAST_ATTRS"
['day_ahead_power', 'hour_ahead_power', '4_hour_ahead_power', '6_hour_ahead_power', 'day_ahead_power_p90', 'hour_ahead_power_p90', '4_hour_ahead_power_p90', '6_hour_ahead_power_p90', 'day_ahead_power_p10', 'hour_ahead_power_p10', '4_hour_ahead_power_p10', '6_hour_ahead_power_p10']
```
* Lookup sites within a Well Known Text rectangle descriptor

  ```bash
$ python -c "import pywtk.site_lookup; in_sites = pywtk.site_lookup.get_3tiersites_from_wkt('POLYGON((-120.82 34.4,-119.19 34.4,-119.19 33.92,-120.82 33.92,-120.82 34.4))'); print in_sites.index.values"
[29375 29733 29872 30019 30190 30539 30712 30713 30874 31032 31033 31189
 31192 31320 31321 31322 31323 31324 31563 32060 32834 33203 30873 31034
 31190 31191]
```
* Lookup the three nearest sites to a Well Known Text point

  ```bash
python -c "import pywtk.site_lookup; sorted_sites = pywtk.site_lookup.get_3tiersites_from_wkt('POINT(-103.12 40.24)'); print sorted_sites.index.values[:3]"
[53252 52873 54322]
```
* Retrieval of met data for multiple sites for a Well Known Text descriptor for specified attributes and year

  ```python
import pandas
import pywtk.wtk_api
wkt = 'POLYGON((-120.82 34.4,-119.19 34.4,-119.19 33.92,-120.82 33.92,-120.82 34.4))'
years = ['2008']
attributes = ['power', 'wind_speed']
wind_data = pywtk.wtk_api.get_wind_data_by_wkt(wkt, years, attributes=attributes)
print(wind_data.keys())
print(wind_data[31563].info())
```
  ```text
[30539, 31320, 30873, 30874, 29733, 29872, 33203, 31032, 31033, 31034, 32060, 29375, 32834, 30019, 31563, 31189, 31190, 31191, 31192, 31321, 31322, 31323, 31324, 30190, 30712, 30713]
<class 'pandas.core.frame.DataFrame'>
DatetimeIndex: 105120 entries, 2008-01-01 00:00:00-08:00 to 2008-12-31 23:55:00-08:00
Data columns (total 2 columns):
power         105120 non-null float64
wind_speed    105120 non-null float64
dtypes: float64(2)
memory usage: 1.6 MB
None
```
* Retrieval of met data for a single site for specified attributes and timespan

  ```python
import pandas
import pywtk.wtk_api
start = pandas.Timestamp('2007-08-01', tz='utc')
end = pandas.Timestamp('2007-08-15', tz='utc')
attributes = ['power', 'wind_speed']
wind_data = pywtk.wtk_api.get_wind_data(102445, start, end, attributes=attributes)
print(wind_data.info())
```
  ```text
<class 'pandas.core.frame.DataFrame'>
DatetimeIndex: 4033 entries, 2007-07-31 20:00:00-04:00 to 2007-08-14 20:00:00-04:00
Data columns (total 2 columns):
power         4033 non-null float64
wind_speed    4033 non-null float64
dtypes: float64(2)
memory usage: 94.5 KB
None
```
* Retrieval of forecast data for multiple sites for a Well Known Text descriptor for specified attributes and years

  ```python
import pandas
import pywtk.wtk_api
wkt = 'POLYGON((-120.82 34.4,-119.19 34.4,-119.19 33.92,-120.82 33.92,-120.82 34.4))'
years = ['2008']
attributes = ['hour_ahead_power', 'day_ahead_power']
wind_data = pywtk.wtk_api.get_wind_data_by_wkt(wkt, years, attributes=attributes, dataset="forecast", utc=True)
print(wind_data.keys())
print(wind_data[31563].info())
```
  ```text
[30539, 31320, 30873, 30874, 29733, 29872, 33203, 31032, 31033, 31034, 32060, 29375, 32834, 30019, 31563, 31189, 31190, 31191, 31192, 31321, 31322, 31323, 31324, 30190, 30712, 30713]
<class 'pandas.core.frame.DataFrame'>
DatetimeIndex: 8784 entries, 2008-01-01 00:00:00+00:00 to 2008-12-31 23:00:00+00:00
Data columns (total 2 columns):
hour_ahead_power    8784 non-null float32
day_ahead_power     8784 non-null float32
dtypes: float32(2)
memory usage: 137.2 KB
None
```

* Retrieval of forecast data for a single site for specified attributes and timespan

  ```python
import pandas
import pywtk.wtk_api
start = pandas.Timestamp('2007-08-01', tz='utc')
end = pandas.Timestamp('2007-08-15', tz='utc')
attributes = ['hour_ahead_power', 'day_ahead_power']
wind_data = pywtk.wtk_api.get_forecast_data(102445, start, end, attributes=attributes)
print(wind_data.info())
```
  ```text
<class 'pandas.core.frame.DataFrame'>
DatetimeIndex: 337 entries, 2007-07-31 20:00:00-04:00 to 2007-08-14 20:00:00-04:00
Data columns (total 2 columns):
hour_ahead_power    337 non-null float32
day_ahead_power     337 non-null float32
dtypes: float32(2)
memory usage: 5.3 KB
None
```

## Well Known Text descriptors
The WKT descriptor should follow the [SQL spec](http://www.opengeospatial.org/standards/sfs).  The following are examples
of a polygon and point definitions:
#### Polygon

  ```python
min_lng = -120.82
max_lng = -119.19
min_lat = 33.92
max_lat = 34.4
wkt = "POLYGON(({0} {3},{1} {3},{1} {2},{0} {2},{0} {3}))".format(min_lng, max_lng, min_lat, max_lat)
```
#### Point

  ```python
pt_lng = -103.12
pt_lat = 40.24
wkt = "POINT({0} {1})".format(pt_lng, pt_lat)
```
