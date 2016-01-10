from setuptools import setup

setup(name='pypavlok',
      version='0.3',
      description='Unofficial Bluetooth controller for Pavlok',
      url='http://github.com/flagist0/pypavlok',
      author='Alexander Presnyakov',
      license='MIT',
      packages=['pypavlok'],
      install_requires=['gattlib>=0.20150805'],
      include_package_data=True,
      zip_safe=False)
