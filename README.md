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
* Wind site timezones
* Available met data attributes
* Available forecast data attributes
* Lookup sites within a Well Known Text shape descriptor
* Lookup site nearest a Well Known Text point
* Retrieval of met data for multiple sites within a Well Known Text shape descriptor for specified attributes and timespan
* Retrieval of met data for a single site for specified attributes and timespan
* Retrieval of forecast data for a single site for specified attributes and timespan

## Well Known Text descriptors
The WKT descriptor should follow the [SQL spec](http://www.opengeospatial.org/standards/sfs).  The following are examples
of a polygon and line definitions:

```python
min_lng = -120.82
max_lng = -119.19
min_lat = 33.92
max_lat = 34.4
wkt = "POLYGON(({0} {3},{1} {3},{1} {2},{0} {2},{0} {3}))".format(min_lng, max_lng, min_lat, max_lat)
```
