import cartwrap
import json
import os
import re
from math import ceil, log
from requests_futures.sessions import FuturesSession

def lambda_handler(event, context):

    session = FuturesSession()

    stdout = ""
    stderr = ""
    order = 0

    # We run C++ executable for most maps and old C excutable (named "cartogram_c") only for Ethiopia and World Map
    cartogram_exec = "cartogram"

    map_data_filename = "conventional.json"

    params = json.loads(event['body'])

    # The C code deduces from the map data file extension whether we have GeoJSON or .gen
    world = False
    try:
        conventional_json = json.loads(params["gen_file"])
        if "NAME_0" in conventional_json['features'][0]["properties"].keys():
            if conventional_json['features'][0]["properties"]["NAME_0"] == "Ethiopia":
                cartogram_exec = "cartogram_c"
        if "extent" in conventional_json.keys():
            if conventional_json['extent'] == "world":
                world = True
                cartogram_exec = "cartogram_c"
    except json.JSONDecodeError:
        map_data_filename = "conventional.gen"

    with open("/tmp/{}".format(map_data_filename), "w") as conventional_map_file:
        conventional_map_file.write(params["gen_file"])

    if cartogram_exec == "cartogram":
        with open("/tmp/areas.csv", "w") as areas_file:
            areas_file.write(params["area_data"])
        area_data_path = "/tmp/areas.csv"
    else:
        area_data_path = params["area_data"]

    for source, line in cartwrap.generate_cartogram(area_data_path, "/tmp/{}".format(map_data_filename), "{}/{}".format(os.environ['LAMBDA_TASK_ROOT'], cartogram_exec), world):

        if source == "stdout":
            stdout += line.decode()
        else:

            stderr_line = line.decode()
            stderr += line.decode()

            # From C++ executable, we directly get cartogram generation progress in percentage; whereas, for C executable
            # we get maximum absolute area error which we translate into progress percentage.
            
            s = re.search(r'Progress: (.+)', line.decode())

            if cartogram_exec == "cartogram_c":
                s = re.search(r'max\. abs\. area error: (.+)', line.decode())

            if s != None:
                current_progress = float(s.groups(1)[0])

                if cartogram_exec == "cartogram_c":
                    current_progress = 1 / max(1 , log((current_progress/0.01), 5))
                
                # Prevents the progress bar from getting stuck at 100%
                if current_progress == 1.0:
                    current_progress = 0.95
                    
                session.post(os.environ['CARTOGRAM_PROGRESS_URL'], json={
                    'secret': os.environ['CARTOGRAM_PROGRESS_SECRET'],
                    'key': params['key'],
                    'progress': current_progress,
                    'stderr': stderr,
                    'order': order
                })

                order += 1

    return {
        "statusCode": 200,
        "body": json.dumps({"stderr": stderr, "stdout": stdout})
    }