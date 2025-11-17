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

# Set the JAVA_HOME environment variable
os.environ["JAVA_HOME"] = java_home_path
print(f"    JAVA_HOME is set to: {os.environ['JAVA_HOME']}")

sys.argv.append("--verbose")
import r5py_ao

#build a multimodal transport network given street network
def build_transportnetwork(data_path, osm_filename, barrier_filename=None):
    osm_path = f"{data_path}/{osm_filename}"
    if barrier_filename:
        barrier_path = f"{data_path}/{barrier_filename}"
    else:
        barrier_path = None

    try:
        #create a routable transport network, that is stored in the transport_network variable.
        transport_network = r5py_ao.TransportNetwork(
            osm_pbf=osm_path,
            barriers=barrier_path)
        print("    Network built success")
        return transport_network
    except Exception as e:
        print("    Error building transport network, aborting: {}".format( e))

def resolve_modes(modes):
    r5_modes = []
    for m in modes:
        match m:
            case "walk":
                r5.modes.append(r5py_ao.TransportMode.WALK)
            case "bike":
                r5.modes.append(r5py_ao.TransportMode.BICYCLE)
            case _:
                raise ValueError(f"Unrecognized mode '{m}'")
    return r5_modes

#build a multimodal transport network given street network
def cal_ttm(transport_network, origin_gdf, destination_gdf, modes, max_lts, max_plts, max_trip_duration, walk_speed, bike_speed):

    travel_time_matrix_computer = r5py_ao.TravelTimeMatrixComputer(
        transport_network,
        origins=origins_gdf,
        destinations=destinations_gdf,
        transport_modes=resolve_modes(modes),
        max_time = max_trip_duration,
        speed_walking = walk_speed,
        speed_cycling = bike_speed,
        max_bicycle_traffic_stress = max_lts,
        max_pedestrian_traffic_stress = max_plts
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
    try:
        barrier_filename = config["barrier_filename"]
    except KeyError:
        barrier_filename = None
    max_lts = config["max_lts"]
    max_plts = config["max_plts"]
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
    transport_network = build_transportnetwork(data_path, osm_filename, barrier_filename)

    print("Calculating travel time matrix...")
    #calculate travel time matrixs
    ttm = cal_ttm(transport_network, origins_gdf, destinations_gdf, max_lts, max_plts, max_trip_duration, walk_speed, bike_speed)

    print('    Calculated travel time matrix using approximately', f'{int(time.time() - startTime)}', 'seconds')

    #save output as a csv file
    ttm_df = ttm.sort_values('from_id').dropna()
    output_path = config.get("outputpath")
    ttm_df.to_csv(output_path, index=False)
    print(f'    Output results were saved in {output_path}')
