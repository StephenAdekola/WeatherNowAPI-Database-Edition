# Weather Now API - Database Edition
The Weather Now backend, now backed by a real **PostgreSQL database** (hosted free on [Neon](https://neon.com)) instead of an in-memory dictionary. Built as Project 3 for the DecodeLabs Full Stack Development internship (3rd September - 3rd October, Cohort 2026): database integration, schema design, and full CRUD.

## Live demo
[View the Live Demo](https://weathernow-api-database-edition.vercel.app/docs)

## What's new since Project 2
- Data is now stored in a real Postgres database instead of resetting on every restart
- A proper two-table schema with a real relationship, instead of one flat structure
- Full CRUD: `PUT` (update) and `DELETE` are new; `GET` and `POST` now read/write the database instead of a dictionary

## Schema
Two tables with a one-to-many relationship — one city has many forecast days:

```
cities                          forecast_days
├── id (PK)                     ├── id (PK)
├── name (unique)               ├── city_id (FK → cities.id)
├── country                     ├── day_index (0–4)
├── current_temp                ├── high
├── current_code                ├── low
└── wind_speed                  └── weathercode
```

## Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/weather` | List every city name |
| GET | `/weather/{city}` | One city's current conditions + 5-day forecast |
| POST | `/weather` | Create a new city |
| PUT | `/weather/{city}` | Replace an existing city's data |
| DELETE | `/weather/{city}` | Delete a city |

Interactive docs (try every endpoint directly) are auto-generated at `/docs`.

## Tech stack
- FastAPI
- SQLAlchemy (ORM — writes parameterized queries automatically, which is what actually prevents SQL injection, rather than string-building SQL by hand)
- PostgreSQL, hosted free on [Neon](https://neon.com)
- Pydantic (request/response validation, separate from the database models)

## Project structure
```
├── main.py            # App, routes, startup seeding
├── database.py         # Engine/session setup, reads DATABASE_URL
├── models.py           # SQLAlchemy schema (City, ForecastDay)
├── schemas.py           # Pydantic request/response shapes
├── seed_data.py         # Initial cities, loaded once if the DB is empty
├── requirements.txt
├── .env.example         # Template — copy to .env and fill in your own values
└── README.md
```

## Getting started

### Run locally
```bash
# Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Add your database connection
cp .env.example .env
# then paste your Neon connection string into .env

# Run the server
uvicorn main:app --reload
```

Visit `http://127.0.0.1:8000/docs`. On first run, the app creates the tables and seeds them with 8 starter cities automatically.

## Example requests
**Get a city:**
```bash
curl http://127.0.0.1:8000/weather/lagos
```

**Create a city:**
```bash
curl -X POST http://127.0.0.1:8000/weather \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Accra", "country": "Ghana",
    "current_temp": 28, "current_code": 2, "wind_speed": 10,
    "forecast": [
      {"high": 30, "low": 22, "weathercode": 2},
      {"high": 29, "low": 22, "weathercode": 1},
      {"high": 31, "low": 23, "weathercode": 0},
      {"high": 28, "low": 21, "weathercode": 61},
      {"high": 30, "low": 22, "weathercode": 2}
    ]
  }'
```

**Update a city:**
```bash
curl -X PUT http://127.0.0.1:8000/weather/accra \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Accra", "country": "Ghana",
    "current_temp": 31, "current_code": 0, "wind_speed": 8,
    "forecast": [
      {"high": 32, "low": 23, "weathercode": 0},
      {"high": 31, "low": 23, "weathercode": 1},
      {"high": 33, "low": 24, "weathercode": 0},
      {"high": 30, "low": 22, "weathercode": 2},
      {"high": 32, "low": 23, "weathercode": 0}
    ]
  }'
```

**Delete a city:**
```bash
curl -X DELETE http://127.0.0.1:8000/weather/accra
```

## License
Free to use and adapt.
