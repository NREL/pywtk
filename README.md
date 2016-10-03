wtk-python-api
==============

Use of wtk data with a python interface

## How to use
Place the path to the cloned repository in the PYTHONPATH variable
```bash
export PYTHONPATH=<path_to_wtk-python-api>:$PYTHONPATH
```

## How to access
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
* Retrieval of met data for multiple sites for a Well Known Text descriptor for specified attributes and timespan
* Retrieval of met data for a single site for specified attributes and timespan
* Retrieval of forecast data for multiple sites for a Well Known Text descriptor for specified attributes and timespan
* Retrieval of forecast data for a single site for specified attributes and timespan

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
