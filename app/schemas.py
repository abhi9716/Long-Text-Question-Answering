from typing import List, Optional, Dict
from pydantic import BaseModel, validator


class PredictRequest(BaseModel):
    data: List[str]

    @validator('data')
    def length(cls, v):
        if len(v) == 2:
            return v
        else:
            raise ValueError('Length of incoming list must be 2.')

class PredictResponse(BaseModel):
    data: str

class Response(BaseModel):
    text: str