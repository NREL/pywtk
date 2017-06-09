from pywtk.site_lookup import get_3tiersites_from_wkt, timezones, sites

MAX_RETURN_SIZE = 10 # Restrict to 10 MB

def handler(event, context):
    '''Expose API thru Lambda.  Restrict returns to MAX_RETURN_SIZE.  An estimate
    on return size is made and if it exceeds the limit data will not be pulled in.

    Required event parameters:
        type - "site", "forecast", "metrology"

    Must have only one of the following event parameters:
        wkt - Well Known Text string of area to return site data
        sites - list of site ids

    Optional event parameters, some required for certain data types:
        wkt - Well Known Text string of area to return site data
        sites - list of site ids
        date_from - Unix timestamp of start date
        date_to - Unix timestamp of end date

    Returns:
        {"success": true, "data": data} for success
        {"success": false, "message": reason} for failure
    '''
    required_params = set(["type"])
    missing_params = required_params - set(event.keys())
    if len(missing_params) > 0:
        return {"success": False, "message": "Missing event parameters: %s"%list(missing_params)}
    dtype = event["type"]
    valid_dtypes = ["site", "forecast", "metrology"]
    if dtype not in valid_dtypes:
        return {"success": False, "message": "Invalid data type, must be one of %s"%valid_dtypes}
    if "wkt" in event.keys() and "sites" not in event.keys():
        site_list = get_3tiersites_from_wkt(event["wkt"])
    elif "sites" in event.keys() and "wkt" not in event.keys():
        site_list = site.loc(event["sites"]).copy()
    else:
        return {"success": False, "message": "Must define either wkt containing sites or a list of sites"}
    if dtype == "site":
        ret_data = site_list
    retsize = df_size(ret_data)
    if retsize > MAX_RETURN_SIZE:
        return {"success": False, "data": "Return data too large at %.2f MB, limit is %s MB"%(retsize, MAX_RETURN_SIZE)}
    return {"success": True, "data": ret_data.to_json()}


def df_size(df):
    '''Get size of dataframe in megabytes
    '''
    r = 0.0
    for col in df:
        r += df[col].nbytes
    return r/1024/1024
