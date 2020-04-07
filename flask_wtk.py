# Flask setup
from flask import Flask, json, request, jsonify, send_from_directory
import os
import pandas
#from pywtk.site_lookup import get_3tiersites_from_wkt, timezones, sites
import pywtk.site_lookup
from pywtk.wtk_api import get_nc_data, FORECAST_ATTRS, MET_ATTRS

DATA_BUCKET = os.environ["DATA_BUCKET"]
MET_LOC = "s3://%s/met_data" % (DATA_BUCKET)
FCST_LOC = "s3://%s/fcst_data" % (DATA_BUCKET)

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False


@app.route("/")
def heartbeat():
    return send_from_directory('static', 'index.html')


def get_sites_from_request(request):
    '''Return sites from a list of site_ids or within a WKT definition.

    Required parameters one of:
        sites - String list of site_ids separated by commas
        wkt - Well known text

    Optional parameters:
        max_point_return - Maximum number of closest sites to a POINT wkt, defaults
            to 1.  Will be ignored for all other cases.

    Returns:
        pandas dataframe of sites
    '''
    if "wkt" in request.args and "sites" not in request.args:
        wkt = request.args["wkt"]
        if 'POINT' in wkt:
            max_point_return = request.args.get("max_point_return", 1, type=int)
            wkt_indexes = pywtk.site_lookup.get_3tiersites_from_wkt(wkt).index[:max_point_return]
        else:
            wkt_indexes = pywtk.site_lookup.get_3tiersites_from_wkt(wkt).index
        return pywtk.site_lookup.sites.loc[wkt_indexes].reset_index().drop('point', axis=1)
    elif "wkt" not in request.args and "sites" in request.args:
        site_list = map(int, request.args.get('sites', "").split(","))
        return pywtk.site_lookup.sites.loc[site_list].copy().reset_index().drop('point', axis=1)
    else:
        raise Exception("Must define either wkt containing sites or a list of sites")


def boolean_type(in_str):
    '''Return True or False based on string input
    '''
    return in_str.lower() in ['true', 'y', '1', 'yes', 't']


@app.route("/sites")
def sites_request():
    '''Return sites from a list of sites or within a WKT definition.

    Required parameters one of:
        sites - string of site_ids separated by commas
        wkt - Well known text

    Optional parameters:
        orient - Pandas dataframe to_json orientation, defaults to records:
            split, records, index, columns or values
            See Pandas documentation for more info
        max_point_return - Maximum number of closest sites to a POINT wkt, defaults
            to 1.  Will be ignored for all other cases.

    Returns:
        json string representation of sites
    '''
    if len(request.args) == 0:
        return send_from_directory('static', 'sites.html')
    try:
        sites = get_sites_from_request(request)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400
    orient = request.args.get("orient", "records")
    if orient not in ["split", "records", "index", "columns", "values"]:
        return jsonify({"success": False, "message": "Orient must be one of split, records, index, columns or values"}), 400
    return sites.to_json(orient=orient)


@app.route("/met")
def met_data():
    '''Return met data from the nc files as to_json representation of pandas
    dataframe.

    Required parameters:
        sites | wkt - string of comma-separated site_ids or Well known text geometry
        start - unix timestamp of start time
        end - unix timestamp of end time

    Optional parameters:
        orient - Pandas dataframe to_json orientation, defaults to records:
            split, records, index, columns or values
            See Pandas documentation for more info
        max_point_return - Maximum number of closest sites to a POINT wkt, defaults
            to 1.  Will be ignored for all other cases.
        attributes - string attributes separated by commas to return, will fail
                     if attribute is not valid for the data set
        leap_day - Bool to include leap day.  Defaults to True
        utc - Bool to use UTC rather than site local time.  Defaults to True

    Returns:
        dict of site id to json representation of dataframes
    '''
    if len(request.args) == 0:
        return send_from_directory('static', 'met.html')
    try:
        sites = get_sites_from_request(request)
        start = pandas.Timestamp(request.args.get('start', type=int), unit="s", tz='utc')
        end = pandas.Timestamp(request.args.get('end', type=int), unit="s", tz='utc')
        orient = request.args.get("orient", "records")
        if orient not in ["split", "records", "index", "columns", "values"]:
            return jsonify({"success": False, "message": "Orient must be one of split, records, index, columns or values"}), 400
        if "attributes" in request.args:
            attributes = request.args.get("attributes", "").split(",")
            if not set(attributes) <= set(MET_ATTRS):
                return jsonify({"success": False, "message": "Attributes must be a subset of %s"%MET_ATTRS}), 400
        else:
            attributes = MET_ATTRS
        ret_dict = {}
        for site_id in sites['site_id']:
            #ret_dict[site_id] = get_wind_data(site_id, start, end).to_json()
            ret_dict[str(site_id)] = json.loads(get_nc_data(site_id, start, end, attributes=attributes, leap_day=True, utc=False, nc_dir=MET_LOC).reset_index().to_json(orient=orient))
        return jsonify(ret_dict)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400


@app.route("/fcst")
def fcst_data():
    '''Return forecast data from the nc files as to_json representation of pandas
    dataframe.

    Required parameters:
        sites | wkt - string of comma-separated site_ids or Well known text geometry
        start - unix timestamp of start time
        end - unix timestamp of end time

    Optional parameters:
        orient - Pandas dataframe to_json orientation, defaults to records:
            split, records, index, columns or values
            See Pandas documentation for more info
        max_point_return - Maximum number of closest sites to a POINT wkt, defaults
            to 1.  Will be ignored for all other cases.
        attributes - String of comma-separated attributes to return, will fail if attribute
            is not valid for the data set

    Returns:
        dict of site id to json representation of dataframes
    '''
    if len(request.args) == 0:
        return send_from_directory('static', 'fcst.html')
    try:
        sites = get_sites_from_request(request)
        start = pandas.Timestamp(request.args.get('start', type=int), unit="s", tz='utc')
        end = pandas.Timestamp(request.args.get('end', type=int), unit="s", tz='utc')
        orient = request.args.get("orient", "records")
        if orient not in ["split", "records", "index", "columns", "values"]:
            return jsonify({"success": False, "message": "Orient must be one of split, records, index, columns or values"}), 400
        if "attributes" in request.args:
            attributes = request.args.get("attributes", "").split(",")
            if not set(attributes) <= set(FORECAST_ATTRS):
                return jsonify({"success": False, "message": "Attributes must be a subset of %s"%FORECAST_ATTRS}), 400
        else:
            attributes = FORECAST_ATTRS
        ret_dict = {}
        for site_id in sites['site_id']:
            #ret_dict[site_id] = get_nc_data(site_id, start, end).to_json()
            ret_dict[str(site_id)] = json.loads(get_nc_data(site_id, start, end, attributes=attributes, leap_day=True, utc=False, nc_dir=FCST_LOC).reset_index().to_json(orient=orient))
        return jsonify(ret_dict)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400


if __name__ == '__main__':
    app.run(debug=True)
