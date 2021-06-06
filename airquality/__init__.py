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
steps = ['hour', 'day', 'week']

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
    SELECT s.station_id, g.population,
    {args['measurement']}(m.{args['variable']}) as {args['measurement']}_{args['variable']}
    FROM aasuero.test_airquality_stations s
    JOIN aasuero.test_airquality_measurements m
    ON s.station_id=m.station_id
    JOIN aasuero.esp_grid_1km_demographics g
    ON ST_Contains(g.the_geom, s.the_geom)
    WHERE m.timeinstant >= '{args['from']}'
    AND m.timeinstant < '{args['to']}'
    GROUP BY s.station_id, s.the_geom, g.population
    """
    response = requests.get(
        url=sql_api_url,
        params={
            'q': query
        }
    )
    return response.json()

# Timeseries endpoint
@app.route('/timeseries', methods=['GET'])
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
        ),
        'step': fields.Str(
            required=True,
            validate=validate.OneOf(steps)
        )
    },
    location='query')
def timeseries(args):
    query = f"""
    SELECT s.station_id, g.population,
    {args['measurement']}(m.{args['variable']}) as {args['measurement']}_{args['variable']},
    date_trunc('{args['step']}', timeinstant) as interval_start
    FROM aasuero.test_airquality_stations s
    JOIN aasuero.test_airquality_measurements m
    ON s.station_id=m.station_id
    JOIN aasuero.esp_grid_1km_demographics g
    ON ST_Contains(g.the_geom, s.the_geom)
    WHERE m.timeinstant >= '{args['from']}'
    AND m.timeinstant < '{args['to']}'
    GROUP BY s.station_id, s.the_geom, g.population, interval_start
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
