from fastapi.testclient import TestClient
import json

from src import __version__
from src.main import app

client = TestClient(app)

mimetype = 'application/json'
headers = {'Content-Type':mimetype}

# Test App version
def test_app_version():
    assert __version__ == '0.1.0'

# Test positive case with name query parameter
def test_name_param_positive():
    response = client.get("/hello?name=bob")
    assert response.status_code == 200
    assert response.json() == {"result":"hello bob"}

# Test negative case of no root implementation
# Checking for the status code "404" not found error provided by the framework
def test_root_error_negative():
    response = client.get("/")
    assert response.status_code == 404

# Test negative case of incorrect query parameter
# Checking for the status code "422" unprocessable entity error provided by the framework
# 422 error because the framework is not able  process an uknown query parameter 
def test_name_param_negative():
    response = client.get("/hello?nam=bob")
    assert response.status_code == 422

# Test negative case of no query parameter
# Checking for the status code "404" not found error provided by the framework
def test_name_no_param_negative():
    response = client.get("/hello=bob")
    assert response.status_code == 404

# Test positive case of no name value
# Checking for the status code "200" and "hello "
def test_name_no_name_positive():
    response = client.get("/hello?name=")
    assert response.status_code == 200
    assert response.json() == {"result":"hello "}

# Test positive case of special char name value
# Checking for the status code "200" and "hello  ?"
def test_name_special_name_positive():
    response = client.get("/hello?name= ?")
    assert response.status_code == 200
    assert response.json() == {"result":"hello  ?"}

# Test positive case of openapi.json
def test_openapi_positive():
    response = client.get("/openapi.json")
    assert response.status_code == 200

# Test positive case of docs
def test_docs_positive():
    response = client.get("/docs")
    assert response.status_code == 200

