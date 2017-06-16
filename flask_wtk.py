# Flask setup
from flask import Flask, json, request, jsonify
import pandas
from pywtk.site_lookup import get_3tiersites_from_wkt, timezones, sites
from pywtk.wtk_api import get_wind_data, get_nc_data

app = Flask(__name__)

@app.route("/")
def heartbeat():
    return ""

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
    #sites = request.args.getlist('site_id')
    orient = request.args.get("orient", "records")
    if orient not in ["split", "records", "index", "columns", "values"]:
        return jsonify({"success": False, "message": "Orient must be one of split, records, index, columns or values"}), 400
    if request.args.has_key("wkt") and not request.args.has_key("site_id"):
        wkt = request.args["wkt"]
        if 'POINT' in wkt:
            max_point_return = int(request.args.get("max_point_return", 1))
            wkt_indexes = get_3tiersites_from_wkt(wkt).index[:max_point_return]
        else:
            wkt_indexes = get_3tiersites_from_wkt(wkt).index
        # The return DF is already a copy, no need to recopy
        return sites.loc[wkt_indexes].reset_index().drop('point', axis=1).to_json(orient=orient)
    elif request.args.has_key("site_id") and not request.args.has_key("wkt"):
        site_list = [int(x) for x in request.args.getlist('site_id')]
        return sites.loc[site_list].copy().reset_index().drop('point', axis=1).to_json(orient=orient)
    else:
        return jsonify({"success": False, "message": "Must define either wkt containing sites or a list of sites"}), 400

@app.route("/met")
def met_data():
    '''Return met data from the hdf files
    Kind of ugly that each of the sites data returns as a single string, but it's
    how pandas encodes the json data that makes it hard to use anything else to
    decode it.

    Required parameters:
        site_id - list of site_ids
        start - unix timestamp of start time
        end - unix timestamp of end time

    Returns:
        dict of site id to json representation of dataframes
    '''
    sites = request.args.getlist('site_id')
    #print "start is %s"%request.args['start']
    start = pandas.Timestamp(int(request.args['start']), unit="s", tz='utc')
    end = pandas.Timestamp(int(request.args['end']), unit="s", tz='utc')
    #print "end is %s"%end
    ret_dict = {}
    try:
        for site_id in sites:
            ret_dict[site_id] = get_wind_data(site_id, start, end).to_json()
        return jsonify(ret_dict)
        '''
    ret_json = "{"
    try:
        for idx, site_id in enumerate(sites, start=1):
            print site_id
            ret_json += '"%s": '%site_id
            ret_json += get_wind_data(site_id, start, end).to_json()
            if idx < len(sites):
                ret_json += ", "
        #print ret_json
        ret_json += "}"
        return ret_json
    '''
    except:
        traceback.print_exc()
        raise

@app.route("/fcst")
def fcst_data():
    '''Return forecast data from the nc files
    Kind of ugly that each of the sites data returns as a single string, but it's
    how pandas encodes the json data that makes it hard to use anything else to
    decode it.

    Required parameters:
        site_id - list of site_ids
        start - unix timestamp of start time
        end - unix timestamp of end time

    Returns:
        dict of site id to json representation of dataframes
    '''
    sites = request.args.getlist('site_id')
    start = pandas.Timestamp(int(request.args['start']), unit="s", tz='utc')
    end = pandas.Timestamp(int(request.args['end']), unit="s", tz='utc')
    ret_dict = {}
    try:
        for site_id in sites:
            ret_dict[site_id] = get_nc_data(site_id, start, end).to_json()
        return jsonify(ret_dict)
    except:
        traceback.print_exc()
        raise



if __name__ == '__main__':
    app.run(debug=True)
