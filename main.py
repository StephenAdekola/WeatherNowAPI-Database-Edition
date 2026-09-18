"""
Weather Now API — Project 3
Same Weather Now API from Project 2, now backed by a real Postgres
database (via Neon) instead of an in-memory dictionary, with the full
set of CRUD operations: Create (POST), Read (GET), Update (PUT),
Delete (DELETE).

Run it with:
    uvicorn main:app --reload

Then open http://127.0.0.1:8000/docs for interactive API docs.
"""

from typing import List
import copy

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import Base, engine, get_db
from models import City, ForecastDay
import schemas
from seed_data import SEED_CITIES

app = FastAPI(
    title="Weather Now API",
    description="Backend for Weather Now, backed by a Postgres database (Project 3).",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    """Create tables if they don't exist yet, and seed data if the table is empty."""
    Base.metadata.create_all(bind=engine)

    db = next(get_db())
    try:
        if db.query(City).count() == 0:
            for city_data in copy.deepcopy(SEED_CITIES):
                forecast_items = city_data.pop("forecast")
                city = City(**city_data)
                city.forecast = [
                    ForecastDay(day_index=i, **day) for i, day in enumerate(forecast_items)
                ]
                db.add(city)
            db.commit()
    finally:
        db.close()


def get_city_or_404(db: Session, name: str) -> City:
    city = (
        db.query(City)
        .filter(func.lower(City.name) == name.strip().lower())
        .first()
    )
    if not city:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No weather data found for '{name}'.",
        )
    return city


# Routes

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Weather Now API (database-backed) is running. Visit /docs to explore it."}


@app.get("/weather", response_model=List[str], tags=["Weather"])
def list_cities(db: Session = Depends(get_db)):
    """List every city currently in the database."""
    return [c.name for c in db.query(City).all()]


@app.get("/weather/{city}", response_model=schemas.CityOut, tags=["Weather"])
def get_weather(city: str, db: Session = Depends(get_db)):
    """Get current conditions + 5-day forecast for one city."""
    return get_city_or_404(db, city)


@app.post("/weather", response_model=schemas.CityOut, status_code=status.HTTP_201_CREATED, tags=["Weather"])
def create_city(payload: schemas.CityCreate, db: Session = Depends(get_db)):
    """Add a new city. Rejects duplicates and forecasts that aren't exactly 5 days."""
    existing = (
        db.query(City)
        .filter(func.lower(City.name) == payload.name.strip().lower())
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"'{payload.name}' already exists. Use PUT to update it instead.",
        )

    if len(payload.forecast) != 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="forecast must contain exactly 5 days.",
        )

    data = payload.model_dump()
    forecast_items = data.pop("forecast")
    city = City(**data)
    city.forecast = [ForecastDay(day_index=i, **day) for i, day in enumerate(forecast_items)]

    db.add(city)
    db.commit()
    db.refresh(city)
    return city


@app.put("/weather/{city}", response_model=schemas.CityOut, tags=["Weather"])
def update_city(city: str, payload: schemas.CityUpdate, db: Session = Depends(get_db)):
    """Replace an existing city's data entirely (current conditions + full 5-day forecast)."""
    existing = get_city_or_404(db, city)

    if len(payload.forecast) != 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="forecast must contain exactly 5 days.",
        )

    data = payload.model_dump()
    forecast_items = data.pop("forecast")

    for key, value in data.items():
        setattr(existing, key, value)

    # Replace the forecast rows entirely rather than trying to patch them individually.
    existing.forecast.clear()
    existing.forecast = [ForecastDay(day_index=i, **day) for i, day in enumerate(forecast_items)]

    db.commit()
    db.refresh(existing)
    return existing


@app.delete("/weather/{city}", status_code=status.HTTP_204_NO_CONTENT, tags=["Weather"])
def delete_city(city: str, db: Session = Depends(get_db)):
    """Delete a city and its forecast data."""
    existing = get_city_or_404(db, city)
    db.delete(existing)
    db.commit()
    return None
