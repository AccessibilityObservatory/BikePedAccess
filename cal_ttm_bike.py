import sys
import os
import pandas as pd
import geopandas as gpd
import datetime
import time
import json

# Java path and verbose have to be set before importing r5py in order for it to work
print('Read config parameters...')
config_file = sys.argv[1]

with open(config_file, "r") as jsonfile:
    config = json.load(jsonfile) # Reading the file

print('Set Java path...')
java_home_path = config["java_path"]
r5_path = config["r5_path"]

# Set the JAVA_HOME environment variable
os.environ["JAVA_HOME"] = java_home_path
print(f"    JAVA_HOME is set to: {os.environ['JAVA_HOME']}")


sys.argv.append("--verbose")
sys.argv.extend([
    "--r5-classpath",
    r5_path
])
import r5py


#build a multimodal transport network given street network
def build_transportnetwork(data_path, osm_filename):
    osm_pbf = f"{data_path}/{osm_filename}"

    try:
        #create a routable transport network, that is stored in the transport_network variable.
        transport_network = r5py.TransportNetwork(osm_pbf)
        print("    Network built success")
        return transport_network
    except Exception as e:
        print("    Error building transport network, aborting: {}".format( e))

#build a multimodal transport network given street network
def cal_bike_ttm(transport_network, origin_gdf, destination_gdf, max_lts, max_trip_duration, walk_speed, bike_speed):

    travel_time_matrix_computer = r5py.TravelTimeMatrixComputer(
        transport_network,
        origins=origins_gdf,
        destinations=destinations_gdf,
        transport_modes=[r5py.TransportMode.BICYCLE],
        max_time = max_trip_duration,
        speed_walking = walk_speed,
        speed_cycling = bike_speed,
        max_bicycle_traffic_stress = max_lts
    )
    travel_time_matrix = travel_time_matrix_computer.compute_travel_times()
    return travel_time_matrix


if __name__ == "__main__":

    #set data path to directory containing the OSM network data
    data_path = config["data_path"]
    osm_filename = config["osm_filename"]

    #routing inputs
    origin_filename = config["origin_filename"]
    destination_filename = config["destination_filename"]
    max_lts = config["max_lts"]
    max_trip_duration = datetime.timedelta(minutes=config.get("max_trip_duration")) #in minutes
    bike_speed = config["bike_speed"] #in km/h
    walk_speed = config["walk_speed"] #in km/h
    output_path = config["outputpath"]

    # read input data
    origins_gdf = gpd.read_file(f"{data_path}/{origin_filename}")
    destinations_gdf = gpd.read_file(f"{data_path}/{destination_filename}")

    #build a transport network given street network
    startTime = time.time()
    print("Building a transport network given street network...")
    transport_network = build_transportnetwork(data_path, osm_filename)

    print("Calculating travel time matrix...")
    #calculate travel time matrixs
    ttm = cal_bike_ttm(transport_network, origins_gdf, destinations_gdf, max_lts, max_trip_duration, walk_speed, bike_speed)

    print('    Calculated travel time matrix using approximately', f'{int(time.time() - startTime)}', 'seconds')

    #save output as a csv file
    ttm_df = ttm.sort_values('from_id').dropna()
    output_path = config.get("outputpath")
    ttm_df.to_csv(output_path, index=False)
    print(f'    Output results were saved in {output_path}')
