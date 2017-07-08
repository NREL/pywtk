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
(cd pywtk_virtenv/lib/python2.7/site-packages; patch -p1 < $HOME/pywtk/zappa.patch)
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
zappa update dev


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

When accessing the notebook for the first time, look for the token parameter in
the URL that shows the server you have access.  Otherwise you will be prompted
for a password that won't work.

* aws_example.pynb - Shows how to use requests to pull data from the met and
fcst lambda services, as well as converting data into pandas dataframes for
plotting.

## Available APIs

* /sites - Wind site metadata
```
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
```

* /met - Metrology data

```
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
```

* /fcst - Forecast data

```
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
```
