from fastapi.testclient import TestClient
import json
import pytest

from src import __version__
from src.main import app

client = TestClient(app)

mimetype = 'application/json'
headers = {'Content-Type':mimetype}
predict_url = '/predict'

# Test App version
def test_app_version():
    assert __version__ == '0.1.0'

# Test positive case for prediction with all features single sample
def test_positive_get_prediction():
    data = {"samples":[{"HouseAge":"41","MedInc":"8.32","AveRooms":"6.98","AveBedrms":"1.02",
    "Population":"322","AveOccup":"2.5","Latitude":"37.88","Longitude":"-122.21"}]}
    response = client.post(predict_url, data = json.dumps(data), headers = headers)
    assert isinstance(response.json()['predicted_val'], list)
    assert all(isinstance(val, float) for val in response.json()['predicted_val'])
    assert len(response.json()['predicted_val']) == len(data['samples'])
    assert response.status_code == 200


# Test positive case for prediction with 1 extra feature single sample
def test_positive_extra_feature():
    data = {"samples":[{"HouseAge":"41","MedInc":"8.32","AveRooms":"6.98","AveBedrms":"1.02",
    "Population":"322","AveOccup":"2.5","Latitude":"37.88","Longitude":"-122.21","Zone":"A"}]}
    response = client.post(predict_url, data = json.dumps(data), headers = headers)
    assert isinstance(response.json()['predicted_val'], list)
    assert all(isinstance(val, float) for val in  response.json()['predicted_val'])
    assert len(response.json()['predicted_val']) == len(data['samples'])
    assert response.status_code == 200

# Test positive case for prediction with features out of order single sample
def test_positive_feature_order():
    data = {"samples":[{"Longitude":"-122.21","MedInc":"8.32","AveRooms":"6.98","AveBedrms":"1.02", \
    "Population":"322","AveOccup":"2.5","Latitude":"37.88","HouseAge":"41"}]}
    outoforder_data = {"samples":[{"HouseAge":"41","MedInc":"8.32","AveRooms":"6.98","AveBedrms":"1.02",
    "Population":"322","AveOccup":"2.5","Latitude":"37.88","Longitude":"-122.21"}]}
    response_d = client.post(predict_url, data = json.dumps(data), headers = headers)
    response_ood = client.post(predict_url, data = json.dumps(outoforder_data), headers = headers)
    assert response_d.json()['predicted_val'] == response_ood.json()['predicted_val']
  

# Test positive case for prediction with a duplicate feature single sample
def test_positive_duplicate_feature():
    data = {"samples":[{"HouseAge":"40","Longitude":"-122.21","MedInc":"8.32","AveRooms":"6.98","AveBedrms":"1.02", \
    "Population":"322","AveOccup":"2.5","Latitude":"37.88","HouseAge":"41"}]}
    response = client.post(predict_url, data = json.dumps(data), headers = headers)
    assert isinstance(response.json()['predicted_val'], list)
    assert all(isinstance(val, float) for val in  response.json()['predicted_val'])
    assert len(response.json()['predicted_val']) == len(data['samples'])
    assert response.status_code == 200

# Test negative case for prediction with a missing feature single sample
def test_negative_missing_feature():
    data = {"samples":[{"HouseAge":"40","Longitude":"-122.21","MedInc":"8.32","AveRooms":"6.98","AveBedrms":"1.02", \
    "Population":"322","AveOccup":"2.5"}]}
    response = client.post(predict_url, data = json.dumps(data), headers = headers)
    assert response.status_code == 422

# Test negative case for prediction with empty sample list
def test_negative_empty_list():
    data = {"samples":[]}
    response = client.post(predict_url, data = json.dumps(data), headers = headers)
    assert response.status_code == 422
    assert response.json() == {'detail': [{'ctx': {'limit_value': 1},
   'loc': ['body', 'samples'],'msg': 'ensure this value has at least 1 items',
   'type': 'value_error.list.min_items'}]}

# Test negative case for prediction with empty request
def test_negative_empty_request():
    data = {}
    response = client.post(predict_url, data = json.dumps(data), headers = headers)
    assert response.status_code == 422
    assert response.json() == {'detail': [{'loc': ['body', 'samples'], 'msg': 'field required', 'type': 'value_error.missing'}]}

# Test negative case for prediction with feature type error
def test_negative_feature_typeerror():
    data = {"samples":[{"HouseAge":"new","MedInc":"8.32","AveRooms":"6.98","AveBedrms":"1.02", \
    "Population":"322","AveOccup":"2.5","Latitude":"37.88","Longitude":"-122.21"}]}
    response = client.post(predict_url, data = json.dumps(data), headers = headers)
    assert response.status_code == 422

# Test negative case for invalid latitude value
def test_negative_latitude_value():
    data = {"samples":[{"HouseAge":"41","MedInc":"8.32","AveRooms":"6.98","AveBedrms":"1.02", \
    "Population":"322","AveOccup":"2.5","Latitude":"337.88","Longitude":"-122.21"}]}
    response = client.post(predict_url, data = json.dumps(data), headers = headers)
    assert response.status_code == 422
    assert response.json() == {"detail":"Invalid latitude"}

# Test negative case for invalid longitude value
def test_negative_longitude_value():
    data = {"samples":[{"HouseAge":"new","MedInc":"8.32","AveRooms":"6.98","AveBedrms":"1.02", \
    "Population":"322","AveOccup":"2.5","Latitude":"37.88","Longitude":"-1122.21"}]}
    response = client.post(predict_url, data = json.dumps(data), headers = headers)
    assert response.status_code == 422
    assert response.json() == {"detail":"Invalid longitude"}

# Test positive case for prediction with all features multiple samples
def test_positive_get_prediction_multiple():
    data = {"samples":[{"HouseAge":"41","MedInc":"8.32","AveRooms":"6.98","AveBedrms":"1.02",
    "Population":"322","AveOccup":"2.5","Latitude":"37.88","Longitude":"-122.21"}, 
    {"HouseAge":"1","MedInc":"8.32","AveRooms":"6.98","AveBedrms":"1.02",
    "Population":"322","AveOccup":"12.5","Latitude":"37.00","Longitude":"-122.21"},
    {"HouseAge":"4","MedInc":"8.32","AveRooms":"6.98","AveBedrms":"1.02",
    "Population":"32","AveOccup":"2","Latitude":"37.88","Longitude":"-111.21"}]}
    response = client.post(predict_url, data = json.dumps(data), headers = headers)
    assert isinstance(response.json()['predicted_val'], list)
    assert all(isinstance(val, float) for val in response.json()['predicted_val'])
    assert len(response.json()['predicted_val']) == len(data['samples'])
    assert response.status_code == 200

# Test positive case for prediction with extra features multiple samples
def test_positive_extra_feature_multiple():
    data = {"samples":[{"HouseAge":"41","MedInc":"8.32","AveRooms":"6.98","AveBedrms":"1.02",
    "Population":"322","AveOccup":"2.5","Latitude":"37.88","Longitude":"-122.21"}, 
    {"HouseAge":"1","MedInc":"8.32","AveRooms":"6.98","AveBedrms":"1.02",
    "Population":"322","AveOccup":"12.5","Latitude":"37.00","Longitude":"-122.21"},
    {"HouseAge":"4","MedInc":"8.32","AveRooms":"6.98","AveBedrms":"1.02",
    "Population":"32","AveOccup":"2","Latitude":"37.88","Longitude":"-111.21","Zone":"A"}]}
    response = client.post(predict_url, data = json.dumps(data), headers = headers)
    assert isinstance(response.json()['predicted_val'], list)
    assert all(isinstance(val, float) for val in response.json()['predicted_val'])
    assert len(response.json()['predicted_val']) == len(data['samples'])
    assert response.status_code == 200

# Test positive case for prediction with float and coersed str type features multiple samples
def test_positive_mixed_type_features_multiple():
    data = {"samples":[{"HouseAge":41,"MedInc":8.32,"AveRooms":6.98,"AveBedrms":1.02,
    "Population":"322","AveOccup":2.5,"Latitude":"37.88","Longitude":"-122.21"}, 
    {"HouseAge":"1","MedInc":"8.32","AveRooms":"6.98","AveBedrms":"1.02",
    "Population":"322","AveOccup":"12.5","Latitude":37.00,"Longitude":"-122.21"},
    {"HouseAge":"4","MedInc":"8.32","AveRooms":"6.98","AveBedrms":"1.02",
    "Population":"32","AveOccup":"2","Latitude":"37.88","Longitude":"-111.21","Zone":"A"}]}
    response = client.post(predict_url, data = json.dumps(data), headers = headers)
    assert isinstance(response.json()['predicted_val'], list)
    assert all(isinstance(val, float) for val in response.json()['predicted_val'])
    assert len(response.json()['predicted_val']) == len(data['samples'])
    assert response.status_code == 200

# Test negative case for prediction with extra features and missing feature multiple samples
def test_negative_extra_missing_feature_multiple():
    data = {"samples":[{"HouseAge":"41","MedInc":"8.32","AveRooms":"6.98","AveBedrms":"1.02",
    "Population":"322","AveOccup":"2.5","Latitude":"37.88","Longitude":"-122.21"}, 
    {"HouseAge":"1","MedInc":"8.32","AveRooms":"6.98","AveBedrms":"1.02",
    "Population":"322","AveOccup":"12.5","Latitude":"37.00","Longitude":"-122.21"},
    {"HouseAge":"4","MedInc":"8.32","AveRooms":"6.98","AveBedrms":"1.02",
    "Population":"32","AveOccup":"2","Latitude":"37.88","Zone":"A"}]}
    response = client.post(predict_url, data = json.dumps(data), headers = headers)
    assert response.status_code == 422
    assert response.json() == {'detail': [{'loc': ['body', 'samples', 2, 'Longitude'], 
    'msg': 'field required', 'type': 'value_error.missing'}]}

# Test positive case, check predicted values are in same order of the input list
def test_positive_predicted_order_input_order():
    data1 = {"HouseAge":"41","MedInc":"8.32","AveRooms":"6.98","AveBedrms":"1.02",
    "Population":"322","AveOccup":"2.5","Latitude":"37.88","Longitude":"-122.21"}
    data2 = {"HouseAge":"1","MedInc":"8.32","AveRooms":"6.98","AveBedrms":"1.02",
    "Population":"322","AveOccup":"12.5","Latitude":"37.00","Longitude":"-122.21"}
    data3 = {"HouseAge":"4","MedInc":"8.32","AveRooms":"6.98","AveBedrms":"1.02",
    "Population":"32","AveOccup":"2","Latitude":"37.88","Longitude":"-122.21"}
    sample1, sample2, sample3 = {"samples":[data1]}, {"samples":[data2]}, {"samples":[data3]}
    sample4 = {"samples":[data2,data3,data1]}
    response1 = client.post(predict_url, data = json.dumps(sample1), headers = headers)
    response2 = client.post(predict_url, data = json.dumps(sample2), headers = headers)
    response3 = client.post(predict_url, data = json.dumps(sample3), headers = headers)
    response4 = client.post(predict_url, data = json.dumps(sample4), headers = headers)
    assert response4.json()['predicted_val'] == [response2.json()['predicted_val'][0], \
                                                     response3.json()['predicted_val'][0], \
                                                     response1.json()['predicted_val'][0]]