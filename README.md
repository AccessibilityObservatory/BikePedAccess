# BikePedAccess

## Overview
BikePedAccess computes LTS-informed travel time metrics for bicycle and pedestrian networks. Built on a customized R5 routing engine, BikePedAccess integrates Bicycle Level of Traffic Stress (BLTS) and Pedestrian Level of Traffic Stress (PLTS) methodologies with barrier-aware routing capabilities.

## Install software dependencies
### Install Java version 11
To interface with R5, r5py requires JDK 11 to function, if not already done, install JDK 11 following the [Java Installation Guide](https://docs.oracle.com/en/java/javase/11/install/overview-jdk-installation.html#GUID-8677A77F-231A-40F7-98B9-1FD0B48C346A).

### Install Python
Download and intall Python this workflow is tested using Python 3.10 version. visit [Python download](https://www.python.org/downloads/) for more information.

### Install Python packages
Now python is installed, next is to install required python packages:

1. [R5py_ao](https://github.com/AccessibilityObservatory/r5py-ao/tree/AO-release-v.0.3.1) is a Python wrapper for the R5 routing analysis engine. It is a modified version of r5py to enable PLTS- and Barrier-informed routing access calculation.
2. [pandas](https://pandas.pydata.org/) is a software library written for the Python programming language for data manipulation and analysis.  
3. [geopandas](https://geopandas.org/en/stable/) is an open source project to make working with geospatial data in python. (Note: Geopandas relies on several other dependencies, when using pip to install GeoPandas, you need to make sure that all dependencies are installed correctly. see https://geopandas.org/en/stable/getting_started/install.html for more information)  

Check the `requirements.txt` for all the required software dependencies. One could install the above packages individually via pip, or install at once with the `requirements.txt`:    

`pip install -r requirements.txt`  


## Prepare input datasets
Street network, destinations and origins are required as input datasets to perform travel time calculation. These input datasets should be prepared in specific formats:    
1. An OpenStreetMap network in `.pbf`  format  
2. The spatial data of origin/destination pairs in ESRI shapefile format, which can be used as origin/destination pairs in a travel time matrix calculation. The spatial input data must contain a **unique** 'id' and **single point** 'geometry' columns, e.g.

|column | description |
|---- | --- | 
|id | Unique string or integer identifier e.g. geoid |
|geometry | Point y-coord in decimal degrees (WGS84 CRS) |
|... | ... (other fields will be ignored) |


## Calculate travel time
The tool contains a Python module and one configuration file:
- `cal_ttm.py` is the analysis script that one would run for producing travel time access results. Running this analysis script requires an additional parameter, a configuration file `ttm_config.json`.  
- `ttm_config.json` is the configuration file that supports the `cal_ttm.py`, it contains basic parameters for calculating bicycle travel time matrix.  

Run analysis scripts:  
`python cal_ttm.py ttm_config.json`

Example configuration:  
```
{
    "java_path" : "/Library/Java/JavaVirtualMachines/openjdk-11.jdk",
    "data_path" : "data",
    "osm_filename" : "cook_county_LTS_2022.osm.pbf",
    "origin_filename" : "CookCountyCensusBlockCentroids2020_WithLatLong_V02_PD_updated.shp",
    "barrier_filename" : "barriers.shp",
    "destination_filename" : "TrailAccessPoints_WithLatLong_V06_PD_updated.shp",
    "modes": ["walk"],
    "max_lts" : 2,
    "max_plts": 4,
    "max_trip_duration" : 30,
    "bike_speed" : 18.0,
    "walk_speed" : 5.0,
    "outputpath" : "blocks_to_trail_access_points_lts2.csv"
}
```
Configuration parameters:    
- `java_path` - A string character. The Java path. To know the Java path, run **/usr/libexec/java_home** if using Mac Terminal; or **echo %JAVA_HOME%** if using Windows Command Prompt.
- `data_path`  - A string character. Location of the input datasets. Default to `./data` in the parent directory
- `osm_filename` - A string character. Name of the OpenStreetMap file.
- `origin_filename` - A string character. Filename of the data that contains points to be used as origins. The file should be either a POINT sf object with WGS84 CRS, or a data.frame containing the columns id, lon and lat.
- `barrier_filename` - A string character. Filename of the data that contains network barrier features. This is optional.
- `destination_filename` - A string character. Filename of the data that contains points to be used as destinations. The file should be either a POINT sf object with WGS84 CRS, or a data.frame containing the columns id, lon and lat.  
- `modes`: - A list. The transport modes allowed for access, ['walk'] or ['bike']
- `max_lts` - An integer between 1 and 4. The maximum level of traffic stress that cyclists will tolerate. A value of 1 means cyclists will only travel through the quietest streets, while a value of 4 indicates cyclists can travel through any road.
- `max_plts` - An integer between 1 and 4. The maximum level of traffic stress that pedestrian will tolerate. A value of 1 means pedestrian will only travel through the lowest-stress streets, while a value of 4 indicates pedestrian can travel through any road.
- `max_trip_duration` - An integer. The maximum trip duration in minutes.   
- `bike_speed` - A numeric. Average cycling speed in km/h.  
- `walk_speed` - A numeric. Average walk speed in km/h.
- `ouputpath` - A string character. File location where the analysis results will be written to.
