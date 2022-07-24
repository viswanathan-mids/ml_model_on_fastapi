from fastapi import FastAPI, Response, HTTPException
from pydantic import BaseModel, root_validator, validator, conlist
from fastapi_redis_cache import FastApiRedisCache, cache
from http import HTTPStatus
from typing import List
from datetime import timedelta

import joblib
import os
import numpy as np

LOCAL_REDIS_URL = "redis://redis-service:6379/0"
#LOCAL_REDIS_URL = "redis://default:redispw@localhost:55000"

app = FastAPI(title="ML predict API App")

@app.on_event("startup")
def startup():
    redis_cache = FastApiRedisCache()
    redis_cache.init(
        host_url=os.environ.get("REDIS_URL", LOCAL_REDIS_URL),
       prefix="myapi"
    )


# Load model
dir_name = os.path.dirname(__file__)
model = joblib.load(dir_name + "/../model_pipeline.pkl")

class predict_input(BaseModel):
    """ Schema for prediction input"""
    MedInc: float
    HouseAge: float
    AveRooms: float
    AveBedrms: float
    Population: float
    AveOccup: float
    Latitude: float
    Longitude: float

    # Custome check for a special case (empty request) to alert users
    @root_validator(pre=True)
    def request_empty(cls, values):
        if not values:
            raise ValueError("Request is empty")
        return values

    # Latitude validity check
    @validator('Latitude')
    def lat_valid(cls,v):
        if v < -90 or v > 90:
            raise HTTPException(status_code=422,detail="Invalid latitude")
        return v

    # Longitude validity check
    @validator('Longitude')
    def long_valid(cls,v):
        if v < -180 or v > 180:
            raise HTTPException(status_code=422,detail="Invalid longitude")
        return v

class predict_list(BaseModel):
    """Input samples list schema"""
    samples: conlist(predict_input, min_items=1)

class predict_output(BaseModel):
    """response model schema"""
    predicted_val: list[float]

    class Config:
        validate_assignment = True

# health endpoint to check API
@app.get("/health")
async def app_health():
    return {"app_status": "healthy"}


# endpoint /hello implementation
@app.get("/hello")
async def name_validation(name: str):
    result = "hello " + name
    return {"result":result}

# Predict endpoint implementation
@app.post("/predict")
@cache(expire=timedelta(minutes=5))
async def predict_val(input: predict_list):

    # Convert all input samples to an array 
    inp_list = [list(dict(sample).values()) for sample in dict(input)['samples']]
    inp_arr = np.array(inp_list)
    
    # Predict and check output model on assignment
    output_model = predict_output(predicted_val=list(model.predict(inp_arr)))

    return {"predicted_val":output_model.predicted_val}

