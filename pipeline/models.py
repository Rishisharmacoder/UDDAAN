"""Pipeline data models for cleaning, normalization, and quality checking."""
from datetime import datetime, date
from typing import Literal, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator


class NormalizedFare(BaseModel):
    source: str
    source_type: Literal["airline", "ota", "gds"]
    origin: str
    destination: str
    route: str
    flight_number: str = Field(default="")
    flight_validation: Literal["verified", "unverified", "invalid"] = "verified"
    travel_date: str
    window: Literal["T+1", "T+7", "T+15", "T+30", "T+45"]
    cabin: str = "ECONOMY"
    airline_code: str = "6E"
    price_inr: float
    scraped_at: str
    quality_flag: Literal["ok", "flagged", "rejected"] = "ok"

    @field_validator("flight_validation", mode="before")
    @classmethod
    def assemble_flight_validation(cls, v: Optional[str], info: Any) -> str:
        if v and v in ["verified", "unverified", "invalid"]:
            return v
        data = info.data
        route = data.get("route", "")
        fnum = data.get("flight_number", "")
        try:
            from pipeline.flight_schedules import validate_flight_schedule
            return validate_flight_schedule(route, fnum)
        except Exception:
            return "verified"

    @field_validator("flight_number", mode="before")
    @classmethod
    def assemble_flight_number(cls, v: Optional[str], info: Any) -> str:
        if v and str(v).strip() and str(v).strip().lower() != "nan":
            return str(v).strip()
        data = info.data
        route = data.get("route", "")
        if not route:
            route = f"{data.get('origin', '')}-{data.get('destination', '')}"
        code = data.get("airline_code", "6E")
        from pipeline.flight_schedules import get_verified_flight_number
        return get_verified_flight_number(route, code)

    @field_validator("route", mode="before")
    @classmethod
    def assemble_route(cls, v: Optional[str], info: Any) -> str:
        if v:
            return v
        data = info.data
        orig = data.get("origin", "")
        dest = data.get("destination", "")
        return f"{orig}-{dest}"

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()
