
from enum import Enum

from pydantic import BaseModel, Field, field_validator


class Sex(str, Enum):
    male = "male"
    female = "female"


class Smoker(str, Enum):
    yes = "yes"
    no = "no"


class Region(str, Enum):
    northeast = "northeast"
    northwest = "northwest"
    southeast = "southeast"
    southwest = "southwest"


class PredictionRequest(BaseModel):
    """Raw, human-readable input coming from the frontend form."""

    age: int = Field(..., ge=0, le=120, description="Age of the primary beneficiary")
    sex: Sex = Field(..., description="Biological sex of the beneficiary")
    bmi: float = Field(..., gt=0, le=80, description="Body mass index")
    children: int = Field(..., ge=0, le=20, description="Number of dependent children")
    smoker: Smoker = Field(..., description="Whether the beneficiary smokes")
    region: Region = Field(..., description="Residential region in the US")

    @field_validator("bmi")
    @classmethod
    def round_bmi(cls, v: float) -> float:
        return round(v, 2)

    model_config = {
        "json_schema_extra": {
            "example": {
                "age": 29,
                "sex": "female",
                "bmi": 27.9,
                "children": 0,
                "smoker": "yes",
                "region": "southwest",
            }
        }
    }


class PredictionResponse(BaseModel):
    predicted_charge: float = Field(..., description="Predicted annual insurance charge in USD")
    currency: str = "USD"
    bmi_category: str = Field(..., description="BMI category derived from the input BMI")
    inputs: PredictionRequest


class HealthResponse(BaseModel):
    model_config = {"protected_namespaces": ()}

    status: str = "ok"
    model_loaded: bool
