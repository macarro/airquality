# airquality

[![Build Status](https://travis-ci.com/macarro/airquality.svg?branch=main)](https://travis-ci.com/macarro/airquality)
[![Coverage Status](https://coveralls.io/repos/github/macarro/airquality/badge.svg?branch=main)](https://coveralls.io/github/macarro/airquality?branch=main)

This is an api on top of the CARTO SQL API that returns aggregated measurements for air quality stations.

Note: For comments on the implementation, as well as my solutions to the warm up exercises, see [notes.md](notes.md).

## Installation

(1) Clone the repository and open a console at the project root directory.

(2) Create a new virtual environment:

```shell
python3 -m venv env
```

(3) Activate the environment:

```shell
source env/bin/activate
```

(4) Install the application:

```shell
pip install .
```

## Running the API locally

(1) Activate the environment (if it is not already active):

```shell
source env/bin/activate
```

(2) Start the application:

```shell
export FLASK_APP=airquality.py
export FLASK_ENV=development
flask run
```

You can now access it at the address indicated in the console.

(3) To stop the application, press Ctrl+C inside the console from (2).

(4) To deactivate the virtual environment, execute

```shell
deactivate
```

## Running tests locally

(1) Activate the environment (if it is not already active):

```shell
source env/bin/activate
```

(2) Install pytest:

```shell
pip install pytest
```

(3) Install airquality itself:

```shell
pip install .
```

(4) To run the tests, execute:

```shell
pytest
```

(5) To run the tests with coverage, `pip install coverage`, then execute:

```shell
coverage run --source=./airquality -m pytest
```

## Deployment

The application is deployed on heroku. If authenticated correctly in the heroku CLI, make a git push like this: `git push heroku main`.

## API documentation

The API only offers two GET endpoints: `/measurements` and `/timeseries`.

**(1) /measurements**

`/measurements`  returns the requested statistical measurement for a given variable for each station. It accepts 6 GET parameters:

* `variable`: Mandatory. String. Must be one of {so2, no2, co, o3, pm10, pm2_5}.
* `measurement`: Mandatory. String. Must be one of {avg, max, min, sum, count}.
* `from`: Mandatory. DateTime. Beginning (inclusive) of the time range in ISO8601 format, for example `2017-06-01T00:00:00`.
* `to`: Mandatory. DateTime. End (exclusive) of the time range in ISO8601 format, for example `2017-06-01T00:00:00`.
* `stations`: Optional. List of stations to filter by, separated by comma. Must be valid station_ids from the data set. Example: `aq_jaen,aq_salvia`.
* `geom`: Optional. Only those stations that intersect with the provided geometry will be shown. Must be valid GeoJSON. Example:

```
{"type":"Polygon","coordinates":[[[-3.63289587199688,40.56439731247202],[-3.661734983325005,40.55618117044514],[-3.66310827434063,40.53583209794804],[-3.6378740519285206,40.52421992151271],[-3.6148714274168015,40.5239589506112],[-3.60543005168438,40.547181381686634],[-3.63289587199688,40.56439731247202]]]}
```

**(2) /timeseries**

`/timeseries` does the same as `/measurements`, but divides the result into intervals. It has the same 6 parameters as `/measurements`, plus:

* `step`: Mandatory. Length of each interval. Must be one of {hour, week day}.

## Use examples

**(1) Obtain measurements for all stations**

```
GET /measurements?variable=so2&measurement=max&from=2017-06-01T00:00:00&to=2017-07-01T00:00:00
```

See the [response on heroku](https://miguel-airquality.herokuapp.com/measurements?variable=so2&measurement=max&from=2017-06-01T00:00:00&to=2017-07-01T00:00:00).

**(2) Obtain timeseries for some stations**

```
GET /timeseries?variable=pm10&measurement=min&from=2017-06-01T00:00:00&to=2017-07-01T00:00:00&step=week&stations=aq_jaen,aq_salvia
```

See the [response on heroku](https://miguel-airquality.herokuapp.com/timeseries?variable=pm10&measurement=min&from=2017-06-01T00:00:00&to=2017-07-01T00:00:00&step=week&stations=aq_jaen,aq_salvia).

**(3) Obtain measurements, filter by both a list of stations, and a geographic perimeter**

```
GET /measurements?variable=so2&measurement=max&from=2017-06-01T00:00:00&to=2017-07-01T00:00:00&stations=aq_jaen,aq_salvia,aq_uam&geom={"type":"Polygon","coordinates":[[[-3.63289587199688,40.56439731247202],[-3.661734983325005,40.55618117044514],[-3.66310827434063,40.53583209794804],[-3.6378740519285206,40.52421992151271],[-3.6148714274168015,40.5239589506112],[-3.60543005168438,40.547181381686634],[-3.63289587199688,40.56439731247202]]]}
```

In this example, I filter by an explicit list of stations {aq_jaen, aq_salvia, aq_uam}, as well as by a polygon, which includes the stations {aq_jaen, aq_salvia, aq_nevero}. The result only contains those stations that pass both filters: {aq_jaen, aq_salvia}.

See the [response on heroku](https://miguel-airquality.herokuapp.com/measurements?variable=so2&measurement=max&from=2017-06-01T00:00:00&to=2017-07-01T00:00:00&stations=aq_jaen,aq_salvia,aq_uam&geom={"type":"Polygon","coordinates":[[[-3.63289587199688,40.56439731247202],[-3.661734983325005,40.55618117044514],[-3.66310827434063,40.53583209794804],[-3.6378740519285206,40.52421992151271],[-3.6148714274168015,40.5239589506112],[-3.60543005168438,40.547181381686634],[-3.63289587199688,40.56439731247202]]]}).

**(4) Missing parameters**

```
GET /measurements
```

This endpoint has 4 mandatory parameters, therefore an error message is shown.

See the [response on heroku](https://miguel-airquality.herokuapp.com/measurements).

**(5) Invalid parameters**

```
GET /measurements?variable=fake&measurement=max&from=2017-06-01T00:00:00&to=2017-07-01T00:00:00&stations=aq_jaen,aq_salvia,aq_uam,fake&geom={"type":"fake","coordinates":[[[-3.63289587199688,40.56439731247202],[-3.661734983325005,40.55618117044514],[-3.66310827434063,40.53583209794804],[-3.6378740519285206,40.52421992151271],[-3.6148714274168015,40.5239589506112],[-3.60543005168438,40.547181381686634],[-3.63289587199688,40.56439731247202]]]}
```

There are 3 problems with this query:

* The value `fake` for the parameter `variable` is invalid.
* The value `fake` for the parameter `stations` is invalid.
* The value `fake` for the type inside the GeoJSON definition of the parameter `geom` is invalid.

An error message is therefore shown.

See the [response on heroku](https://miguel-airquality.herokuapp.com/measurements?variable=fake&measurement=max&from=2017-06-01T00:00:00&to=2017-07-01T00:00:00&stations=aq_jaen,aq_salvia,aq_uam,fake&geom={"type":"fake","coordinates":[[[-3.63289587199688,40.56439731247202],[-3.661734983325005,40.55618117044514],[-3.66310827434063,40.53583209794804],[-3.6378740519285206,40.52421992151271],[-3.6148714274168015,40.5239589506112],[-3.60543005168438,40.547181381686634],[-3.63289587199688,40.56439731247202]]]}).
