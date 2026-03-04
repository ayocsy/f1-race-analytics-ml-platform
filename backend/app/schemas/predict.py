
from pydantic import BaseModel, Field

class PredictRequest(BaseModel):
    season: int = Field(ge=1950)
    round: int = Field(ge=1)
    driver_a: str = Field(min_length=1)
    driver_b: str = Field(min_length=1)

class PredictResponse(BaseModel):
    probability_win: float
    prediction: int
    features_used: dict


class ManualPredictRequest(BaseModel):
    season: int = Field(ge=1950)
    round: int = Field(ge=1)
    driver_a: str = Field(min_length=1)
    driver_b: str = Field(min_length=1)
    quali_pos_a: int = Field(ge=1)
    quali_pos_b: int = Field(ge=1)
