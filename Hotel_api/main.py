from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Dict
from services.hotel_service import HotelService

app = FastAPI(title="Hotel Finder API")

hotel_service = HotelService()

# ----------------------------
# Request Body Models
# ----------------------------
class Location(BaseModel):
    lat: float = Field(..., example=7.1807)
    long: float = Field(..., example=79.8841)

class HotelRequest(BaseModel):
    num_people: int = Field(..., example=2)
    daily_locations: Dict[str, Location] = Field(
        ...,
        example={
            "day1": {"lat": 7.1807, "long": 79.8841},
            "day2": {"lat": 6.9344, "long": 79.8428}
        }
    )


@app.get("/")
def home():
    return {"message": "Welcome to the Hotel Finder API"}


@app.post("/nearest-hotels")
def nearest_hotels(request: HotelRequest):
    num_people = request.num_people
    daily_locations = {day: loc.dict() for day, loc in request.daily_locations.items()}

    result = hotel_service.find_hotels_for_days(num_people, daily_locations)
    return {"status": "success", "data": result}
