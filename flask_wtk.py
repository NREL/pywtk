# Flask setup
from flask import Flask, json, request, jsonify
import pandas
import traceback
from wtk_api import get_wind_data

app = Flask(__name__)

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


if __name__ == '__main__':
    app.run(debug=True)
