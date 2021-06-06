import pytest
import airquality
import json

@pytest.fixture
def client():
    with airquality.app.test_client() as client:
        yield client

def test_many_responses(client):
    """A valid request should return a rows object"""
    params = {
        'variable': 'so2',
        'measurement': 'avg',
        'from': '2017-06-01T00:00:00',
        'to': '2017-07-01T00:00:00'
    }
    response = client.get('/measurements', query_string=params)
    body = json.loads(response.data)
    assert response.status_code == 200
    assert 'rows' in body
    assert 'population' in body['rows'][0]

def test_future_date(client):
    """A request for date in the future should return no rows"""
    params = {
        'variable': 'so2',
        'measurement': 'avg',
        'from': '2050-06-01T00:00:00',
        'to': '2050-07-01T00:00:00'
    }
    response = client.get('/measurements', query_string=params)
    body = json.loads(response.data)
    assert response.status_code == 200
    assert 'rows' in body
    assert body['total_rows'] == 0

def test_invalid_variable(client):
    """A request with an invalid variable value should return an error for that parameter"""
    params = {
        'variable': 'invalid',
        'measurement': 'avg',
        'from': '2017-06-01T00:00:00',
        'to': '2017-07-01T00:00:00'
    }
    response = client.get('/measurements', query_string=params)
    body = json.loads(response.data)
    assert response.status_code == 422
    assert 'variable' in body['errors']['query']

def test_missing_variable(client):
    """A request without variable value should return an error for that parameter"""
    params = {
        'measurement': 'avg',
        'from': '2017-06-01T00:00:00',
        'to': '2017-07-01T00:00:00'
    }
    response = client.get('/measurements', query_string=params)
    body = json.loads(response.data)
    assert response.status_code == 422
    assert 'variable' in body['errors']['query']

def test_invalid_measurement(client):
    """A request with an invalid measurement value should return an error for that parameter"""
    params = {
        'variable': 'so2',
        'measurement': 'invalid',
        'from': '2017-06-01T00:00:00',
        'to': '2017-07-01T00:00:00'
    }
    response = client.get('/measurements', query_string=params)
    body = json.loads(response.data)
    assert response.status_code == 422
    assert 'measurement' in body['errors']['query']

def test_missing_measurement(client):
    """A request without measurement value should return an error for that parameter"""
    params = {
        'variable': 'so2',
        'from': '2017-06-01T00:00:00',
        'to': '2017-07-01T00:00:00'
    }
    response = client.get('/measurements', query_string=params)
    body = json.loads(response.data)
    assert response.status_code == 422
    assert 'measurement' in body['errors']['query']

def test_invalid_from(client):
    """A request with an invalid from value should return an error for that parameter"""
    params = {
        'variable': 'so2',
        'measurement': 'avg',
        'from': 'invalid',
        'to': '2017-07-01T00:00:00'
    }
    response = client.get('/measurements', query_string=params)
    body = json.loads(response.data)
    assert response.status_code == 422
    assert 'from' in body['errors']['query']

def test_missing_from(client):
    """A request without from value should return an error for that parameter"""
    params = {
        'variable': 'so2',
        'measurement': 'avg',
        'to': '2017-07-01T00:00:00'
    }
    response = client.get('/measurements', query_string=params)
    body = json.loads(response.data)
    assert response.status_code == 422
    assert 'from' in body['errors']['query']

def test_invalid_to(client):
    """A request with an invalid to value should return an error for that parameter"""
    params = {
        'variable': 'so2',
        'measurement': 'avg',
        'from': '2017-06-01T00:00:00',
        'to': 'invalid'
    }
    response = client.get('/measurements', query_string=params)
    body = json.loads(response.data)
    assert response.status_code == 422
    assert 'to' in body['errors']['query']

def test_missing_to(client):
    """A request without to value should return an error for that parameter"""
    params = {
        'variable': 'so2',
        'measurement': 'avg',
        'from': '2017-06-01T00:00:00'
    }
    response = client.get('/measurements', query_string=params)
    body = json.loads(response.data)
    assert response.status_code == 422
    assert 'to' in body['errors']['query']
