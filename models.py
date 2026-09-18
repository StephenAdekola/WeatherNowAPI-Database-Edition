from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


class City(Base):
    __tablename__ = "cities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    country = Column(String(100), nullable=False)
    current_temp = Column(Float, nullable=False)
    current_code = Column(Integer, nullable=False)
    wind_speed = Column(Float, nullable=False)

    # cascade="all, delete-orphan" means: deleting a city deletes its
    # forecast rows too, instead of leaving orphaned rows behind.
    forecast = relationship(
        "ForecastDay",
        back_populates="city",
        cascade="all, delete-orphan",
        order_by="ForecastDay.day_index",
    )


class ForecastDay(Base):
    __tablename__ = "forecast_days"

    id = Column(Integer, primary_key=True, index=True)
    city_id = Column(Integer, ForeignKey("cities.id"), nullable=False)
    day_index = Column(Integer, nullable=False)  # 0 = today, 1-4 = the following days
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    weathercode = Column(Integer, nullable=False)

    city = relationship("City", back_populates="forecast")
