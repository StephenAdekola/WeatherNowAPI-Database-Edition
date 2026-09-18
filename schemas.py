from typing import List
from pydantic import BaseModel, Field, ConfigDict


class ForecastDayBase(BaseModel):
    high: float
    low: float
    weathercode: int = Field(..., ge=0, description="WMO weather code")


class ForecastDayOut(ForecastDayBase):
    model_config = ConfigDict(from_attributes=True)  # allows reading straight from an ORM object
    id: int


class CityBase(BaseModel):
    name: str = Field(..., min_length=1, description="City name")
    country: str = Field(..., min_length=1)
    current_temp: float
    current_code: int = Field(..., ge=0)
    wind_speed: float = Field(..., ge=0)


class CityCreate(CityBase):
    """Shape required for POST — creating a new city."""
    forecast: List[ForecastDayBase]


class CityUpdate(CityBase):
    """Shape required for PUT — replacing an existing city's data."""
    forecast: List[ForecastDayBase]


class CityOut(CityBase):
    """Shape returned in responses."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    forecast: List[ForecastDayOut]
