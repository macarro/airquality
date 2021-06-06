from flask import Flask, jsonify
from flask import request
from webargs import fields, validate
from webargs.flaskparser import use_args
import requests

app = Flask(__name__)

# Constants
sql_api_url = 'https://aasuero.carto.com:443/api/v2/sql'
measurement_variables = ['so2', 'no2', 'co', 'o3', 'pm10', 'pm2_5']
statistical_measurements = ['avg', 'max', 'min', 'sum', 'count']

# Measurements endpoint
@app.route('/measurements', methods=['GET'])
@use_args(
    {
        'variable': fields.Str(
            required=True,
            validate=validate.OneOf(measurement_variables)
        ),
        'measurement': fields.Str(
            required=True,
            validate=validate.OneOf(statistical_measurements)
        ),
        'from': fields.DateTime(
            required=True
        ),
        'to': fields.DateTime(
            required=True
        )
    },
    location='query')
def measurements(args):
    query = f"""
    SELECT station_id, {args['measurement']}({args['variable']})
    FROM aasuero.test_airquality_measurements
    WHERE timeinstant >= \'{args['from']}\'
    AND timeinstant < '{args['to']}'
    GROUP BY station_id
    """
    response = requests.get(
        url=sql_api_url,
        params={
            'q': query
        }
    )
    return response.json()

# Return validation errors as JSON
@app.errorhandler(422)
@app.errorhandler(400)
def handle_error(err):
    headers = err.data.get('headers', None)
    messages = err.data.get('messages', ['Invalid request.'])
    if headers:
        return jsonify({'errors': messages}), err.code, headers
    else:
        return jsonify({'errors': messages}), err.code
