
from setuptools import setup

setup(
    name='pyhwtherm',
    version='2.0',
    license='MIT',
    author='Dan Yeakley',
    author_email='ddyeakley@gmail.com',
    url='https://github.com/ddyeakley/pyhwtherm',
    long_description="README.md",
    packages=['pyhwtherm'],
    include_package_data=False,
    description="Library to connect to the Honeywell Website to query status and update the wifi thermostat",
)
