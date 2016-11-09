from distutils.core import setup

setup(name='pywtk',
      version='1.0',
      description='Python API for Wind Toolkit data',
      author='Harry Sorensen',
      author_email='harry.sorensen@nrel.gov',
      packages=['pywtk'],
      package_data={'pywtk': ['*.csv']}
    )
