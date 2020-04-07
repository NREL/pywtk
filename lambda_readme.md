## Setting up pywtk on an AWS lambda

These instructions are for setting up the code on an AWS lambda.  An example on
how to use the pywtk lambda resides in [notebooks/3_data_retrieval_lambda.ipynb]

1. Set up virtualenv
```bash
virtualenv dev_virtualenv
. dev_virtualenv/bin/activate
pip install -r requirements.txt
```

2. Deploy using zappa.  Note this creates a lot of AWS items, and changes to the
aws platform sometimes leaves lambdas in a state where an update will corrupt
some of the settings.  For example:  An update after three years left the API
gateway hitting a star wars API and no amount of changes in the GUI would fix it.
Ended up having to delete and redeploy.
```bash
zappa deploy dev
```

3. Linking lambda to domain.  TBD, cyber has yet to do this.
