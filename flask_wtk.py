# Flask setup
from flask import Flask, json, request, jsonify
import pandas
#from pywtk.site_lookup import get_3tiersites_from_wkt, timezones, sites
import pywtk.site_lookup
from pywtk.wtk_api import get_nc_data, FORECAST_ATTRS, MET_ATTRS

MET_LOC = "s3://pywtk-data/met_data"
FCST_LOC = "s3://pywtk-data/fcst_data"

app = Flask(__name__)

@app.route("/")
def heartbeat():
    return ""

def get_sites_from_request(request):
    '''Return sites from a list of site_ids or within a WKT definition.

    Required parameters one of:
        site_id - list of site_ids
        wkt - Well known text

    Optional parameters:
        max_point_return - Maximum number of closest sites to a POINT wkt, defaults
            to 1.  Will be ignored for all other cases.

    Returns:
        pandas dataframe of sites
    '''
    if "wkt" in request.args and "site_id" not in request.args:
        wkt = request.args["wkt"]
        if 'POINT' in wkt:
            max_point_return = request.args.get("max_point_return", 1, type=int)
            wkt_indexes = pywtk.site_lookup.get_3tiersites_from_wkt(wkt).index[:max_point_return]
        else:
            wkt_indexes = pywtk.site_lookup.get_3tiersites_from_wkt(wkt).index
        return pywtk.site_lookup.sites.loc[wkt_indexes].reset_index().drop('point', axis=1)
    elif "wkt" not in request.args and "site_id" in request.args:
        site_list = request.args.getlist('site_id', type=int)
        return pywtk.site_lookup.sites.loc[site_list].copy().reset_index().drop('point', axis=1)
    else:
        raise Exception("Must define either wkt containing sites or a list of sites")

def boolean_type(in_str):
    '''Return True or False based on string input
    '''
    return in_str.lower() in ['true', 'y', '1', 'yes', 't']

@app.route("/sites")
def sites_request():
    '''Return sites from a list of site_ids or within a WKT definition.

    Required parameters one of:
        site_id - list of site_ids
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
    try:
        sites = get_sites_from_request(request)
    except Exception as e:
        jsonify({"success": False, "message": str(e)}), 400
    orient = request.args.get("orient", "records")
    if orient not in ["split", "records", "index", "columns", "values"]:
        return jsonify({"success": False, "message": "Orient must be one of split, records, index, columns or values"}), 400
    return sites.to_json(orient=orient)

@app.route("/met")
def met_data():
    '''Return met data from the nc files as to_json representation of pandas
    dataframe.

    Required parameters:
        site_id | wkt - list of site_ids or Well known text geometry
        start - unix timestamp of start time
        end - unix timestamp of end time

    Optional parameters:
        orient - Pandas dataframe to_json orientation, defaults to records:
            split, records, index, columns or values
            See Pandas documentation for more info
        max_point_return - Maximum number of closest sites to a POINT wkt, defaults
            to 1.  Will be ignored for all other cases.
        attributes - List of string attributes to return, will fail if attribute
            is not valid for the data set
        leap_day - Bool to include leap day.  Defaults to True
        utc - Bool to use UTC rather than site local time.  Defaults to True

    Returns:
        dict of site id to json representation of dataframes
    '''
    #sites = request.args.getlist('site_id')
    try:
        sites = get_sites_from_request(request)
        #print "start is %s"%request.args['start']
        start = pandas.Timestamp(request.args.get('start', type=int), unit="s", tz='utc')
        end = pandas.Timestamp(request.args.get('end', type=int), unit="s", tz='utc')
        #print "end is %s"%end
        orient = request.args.get("orient", "records")
        if orient not in ["split", "records", "index", "columns", "values"]:
            return jsonify({"success": False, "message": "Orient must be one of split, records, index, columns or values"}), 400
        attributes = request.args.getlist("attributes")
        if len(attributes) == 0:
            attributes = MET_ATTRS
        if not set(attributes) <= set(MET_ATTRS):
            return jsonify({"success": False, "message": "Attributes must be a set of %s"%MET_ATTRS}), 400
        ret_dict = {}
        for site_id in sites['site_id']:
            #ret_dict[site_id] = get_wind_data(site_id, start, end).to_json()
            ret_dict[site_id] = json.loads(get_nc_data(site_id, start, end, attributes=attributes, leap_day=True, utc=False, nc_dir=MET_LOC).reset_index().to_json(orient=orient))
        return jsonify(ret_dict)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400

@app.route("/fcst")
def fcst_data():
    '''Return forecast data from the nc files as to_json representation of pandas
    dataframe.

    Required parameters:
        site_id | wkt - list of site_ids or Well known text geometry
        start - unix timestamp of start time
        end - unix timestamp of end time

    Optional parameters:
        orient - Pandas dataframe to_json orientation, defaults to records:
            split, records, index, columns or values
            See Pandas documentation for more info
        max_point_return - Maximum number of closest sites to a POINT wkt, defaults
            to 1.  Will be ignored for all other cases.

    Returns:
        dict of site id to json representation of dataframes
    '''
    #sites = request.args.getlist('site_id')
    try:
        sites = get_sites_from_request(request)
        start = pandas.Timestamp(request.args.get('start', type=int), unit="s", tz='utc')
        end = pandas.Timestamp(request.args.get('end', type=int), unit="s", tz='utc')
        orient = request.args.get("orient", "records")
        if orient not in ["split", "records", "index", "columns", "values"]:
            return jsonify({"success": False, "message": "Orient must be one of split, records, index, columns or values"}), 400
        ret_dict = {}
        for site_id in sites['site_id']:
            #ret_dict[site_id] = get_nc_data(site_id, start, end).to_json()
            ret_dict[site_id] = json.loads(get_nc_data(site_id, start, end, attributes=FORECAST_ATTRS, leap_day=True, utc=False, nc_dir=FCST_LOC).reset_index().to_json(orient=orient))
        return jsonify(ret_dict)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400



if __name__ == '__main__':
    app.run(debug=True)
