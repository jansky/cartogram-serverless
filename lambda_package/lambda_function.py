import cartwrap
import json
import os
import re
from requests_futures.sessions import FuturesSession

def lambda_handler(event, context):

    session = FuturesSession()

    stdout = ""
    stderr = ""
    order = 0

    map_data_filename = "conventional.json"

    params = json.loads(event['body'])

    # The C code deduces from the map data file extension whether we have GeoJSON or .gen
    world = False
    try:
        conventional_json = json.loads(params["gen_file"])
        if "extent" in conventional_json.keys():
            if conventional_json['extent'] == "world":
                world = True
    except json.JSONDecodeError:
        map_data_filename = "conventional.gen"

    with open("/tmp/{}".format(map_data_filename), "w") as conventional_map_file:
        conventional_map_file.write(params["gen_file"])

    for source, line in cartwrap.generate_cartogram(params["area_data"], "/tmp/{}".format(map_data_filename), "{}/cartogram".format(os.environ['LAMBDA_TASK_ROOT']), world):

        if source == "stdout":
            stdout += line.decode()
        else:

            stderr_line = line.decode()
            stderr += line.decode()

            s = re.search(r'max\. abs\. area error: (.+)', line.decode())

            if s != None:
                current_progress = float(s.groups(1)[0])

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
