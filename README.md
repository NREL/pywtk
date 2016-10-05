wtk-python-api
==============

Use of wtk data with a python interface

## How to install
Place the path to the cloned repository in the PYTHONPATH variable
```bash
export PYTHONPATH=<path_to_wtk-python-api>:$PYTHONPATH
```

## Available data and how to access it
* Wind site metadata

  ```bash
$ python -c "import site_lookup, pprint; pprint.pprint(site_lookup.sites['11222'])"
{'capacity': '16.0',
 'capacity_factor': '0.411',
 'city': '',
 'country': 'United States',
 'elevation': '',
 'fraction_of_usable_area': '1.0',
 'gid': '11223',
 'point': <shapely.geometry.point.Point object at 0x107dfc910>,
 'power_curve': '3',
 'site_id': '11222',
 'state': 'Texas',
 'the_geom': '0101000020E61000009414580053BA59C069FD2D01F8574040',
 'wind_speed': '7.34'}
```
* Wind site timezones

  ```bash
$ python -c "import site_lookup, pprint; pprint.pprint(site_lookup.timezones['11222'])"
{'abbreviation': 'CDT',
 'countryCode': 'US',
 'countryName': 'United States',
 'dst': '1',
 'dstEnd': '1478415600',
 'dstStart': '1457856000',
 'gmtOffset': '-18000',
 'nextAbbreviation': 'CST',
 'site_id': '11222',
 'timestamp': '1470316655',
 'zoneName': 'America/Chicago'}
```
* Available met data attributes

  ```bash
$ python -c "import wtk_api; print wtk_api.MET_ATTRS"
['density', 'power', 'pressure', 'temperature', 'wind_direction', 'wind_speed']
```
* Available forecast data attributes

  ```bash
$ python -c "import wtk_api; print wtk_api.FORECAST_ATTRS"
['day_ahead_power', 'hour_ahead_power', '4_hour_ahead_power', '6_hour_ahead_power', 'day_ahead_power_p90', 'hour_ahead_power_p90', '4_hour_ahead_power_p90', '6_hour_ahead_power_p90', 'day_ahead_power_p10', 'hour_ahead_power_p10', '4_hour_ahead_power_p10', '6_hour_ahead_power_p10']
```
* Lookup sites within a Well Known Text rectangle descriptor

  ```bash
$ python -c "import site_lookup; print site_lookup.get_3tiersites_from_wkt('POLYGON((-120.82 34.4,-119.19 34.4,-119.19 33.92,-120.82 33.92,-120.82 34.4))')"
['29375', '31034', '31032', '31033', '30019', '30190', '33203', '32060', '31189', '31192', '31191', '31190', '29733', '30539', '32834', '31324', '31320', '31322', '31323', '31563', '30712', '30713', '31321', '30874', '30873', '29872']
```
* Lookup site nearest a Well Known Text point

  ```bash
$ python -c "import site_lookup; print site_lookup.get_3tiersites_from_wkt('POINT(-103.12 40.24)')"
['53252']
```
* Retrieval of met data for multiple sites for a Well Known Text descriptor for specified attributes and year

  ```python
import pandas
import wtk_api
wkt = 'POLYGON((-120.82 34.4,-119.19 34.4,-119.19 33.92,-120.82 33.92,-120.82 34.4))'
years = ['2008']
attributes = ['power', 'wind_speed']
wind_data = wtk_api.get_wind_data_by_wkt(wkt, years, attributes=attributes)
print(wind_data.keys())
print(wind_data['31563'].info())
```
  ```text
['31563', '31324', '30713', '33203', '30874', '31320', '31321', '31322', '31323', '31192', '31191', '31190', '29375', '30712', '32834', '30190', '30019', '31033', '29872', '31189', '30873', '32060', '29733', '31034', '31032', '30539']
<class 'pandas.core.frame.DataFrame'>
DatetimeIndex: 105120 entries, 2008-01-01 00:00:00-08:00 to 2008-12-31 23:55:00-08:00
Data columns (total 2 columns):
power         105120 non-null float64
wind_speed    105120 non-null float64
dtypes: float64(2)
memory usage: 2.4 MB
None
```
* Retrieval of met data for a single site for specified attributes and timespan

  ```python
import pandas
import wtk_api
start = pandas.Timestamp('2007-08-01', tz='utc')
end = pandas.Timestamp('2007-08-15', tz='utc')
attributes = ['power', 'wind_speed']
wind_data = wtk_api.get_wind_data("102445", start, end, attributes=attributes)
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
* Retrieval of forecast data for multiple sites for a Well Known Text descriptor for specified attributes and timespan

  ```python
import pandas
import wtk_api
wkt = 'POLYGON((-120.82 34.4,-119.19 34.4,-119.19 33.92,-120.82 33.92,-120.82 34.4))'
years = ['2008']
attributes = ['hour_ahead_power', 'day_ahead_power']
wind_data = wtk_api.get_wind_data_by_wkt(wkt, years, attributes=attributes, dataset="forecast", utc=True)
print(wind_data.keys())
print(wind_data['31563'].info())
```
  ```text
['31563', '31324', '30713', '33203', '30874', '31320', '31321', '31322', '31323', '31192', '31191', '31190', '29375', '30712', '32834', '30190', '30019', '31033', '29872', '31189', '30873', '32060', '29733', '31034', '31032', '30539']
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
import wtk_api
start = pandas.Timestamp('2007-08-01', tz='utc')
end = pandas.Timestamp('2007-08-15', tz='utc')
attributes = ['hour_ahead_power', 'day_ahead_power']
wind_data = wtk_api.get_forecast_data("102445", start, end, attributes=attributes)
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
