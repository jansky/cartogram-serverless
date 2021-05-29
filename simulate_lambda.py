import sys
import os

sys.path.append(os.environ['LAMBDA_TASK_ROOT'])

from flask import Flask, request, Response
import lambda_function

app = Flask(__name__)

app.secret_key = "7ND9V0KOzfmfkmU3YYv5UEcqtEw1DZgVKBARXpc0PAzgfSdDgz9hntux1lVDmh56M8QtInJ3bE8Z"
app.config['ENV']

@app.route('/cartogram', methods=['POST'])
def cartogram():

    lambda_event = {'body': request.data }

    response = lambda_function.lambda_handler(lambda_event, {})

    return Response(response['body'], status=response['statusCode'], content_type="application/json")

if __name__ == '__main__':
    app.run(debug=True,host=os.environ['LAMBDA_SIMULATOR_HOST'],port=int(os.environ['LAMBDA_SIMULATOR_PORT']))