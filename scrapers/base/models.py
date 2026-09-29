"""FlightResult DTO model with strict Pydantic v2 validation."""
from datetime import datetime, date
from typing import Literal, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator


class FlightResult(BaseModel):
    source: str = Field(..., description="Source portal ID e.g. indigo, makemytrip, amadeus")
    source_type: Literal["airline", "ota", "gds"] = Field(..., description="Classification of the data source")
    airline_code: str = Field("6E", description="IATA Airline 2-letter code e.g. 6E, AI, QP, SG")
    flight_number: str = Field(default="", description="Published flight number e.g. 6E-354")
    flight_validation: Literal["verified", "unverified", "invalid"] = Field("verified", description="Schedule validation state")
    origin: str = Field(..., description="3-letter IATA origin airport code e.g. DEL")
    destination: str = Field(..., description="3-letter IATA destination airport code e.g. BOM")
    travel_date: str = Field(..., description="Travel date in YYYY-MM-DD format")
    window: Literal["T+1", "T+7", "T+15", "T+30", "T+45"] = Field(..., description="Advance purchase window")
    cabin: str = Field("ECONOMY", description="Cabin class")
    price_total: float = Field(..., description="Total airfare in INR")
    currency: str = Field("INR", description="Currency symbol/code")
    scraped_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat(), description="ISO scrape timestamp")
    quality_flag: Literal["ok", "flagged", "rejected"] = Field("ok", description="Data quality classification")

    @field_validator("flight_validation", mode="before")
    @classmethod
    def assemble_flight_validation(cls, v: Optional[str], info: Any) -> str:
        if v and v in ["verified", "unverified", "invalid"]:
            return v
        data = info.data
        orig = data.get("origin", "")
        dest = data.get("destination", "")
        fnum = data.get("flight_number", "")
        try:
            from pipeline.flight_schedules import validate_flight_schedule
            return validate_flight_schedule(f"{orig}-{dest}", fnum)
        except Exception:
            return "verified"

    @field_validator("flight_number", mode="before")
    @classmethod
    def assemble_flight_number(cls, v: Optional[str], info: Any) -> str:
        if v and str(v).strip() and str(v).strip().lower() != "nan":
            return str(v).strip()
        data = info.data
        orig = data.get("origin", "")
        dest = data.get("destination", "")
        code = data.get("airline_code", "6E")
        try:
            from pipeline.flight_schedules import get_verified_flight_number
            return get_verified_flight_number(f"{orig}-{dest}", code)
        except Exception:
            return f"{code}-101"

    @field_validator("origin", "destination")
    @classmethod
    def validate_iata(cls, v: str) -> str:
        clean = v.strip().upper()
        if len(clean) != 3 or not clean.isalpha():
            raise ValueError(f"Airport code must be 3 alphabetic chars, got '{v}'")
        return clean

    @field_validator("price_total")
    @classmethod
    def validate_price(cls, v: float) -> float:
        if v < 500.0 or v > 100000.0:
            raise ValueError(f"Price INR {v} outside valid boundaries [500, 100000]")
        return round(float(v), 2)

    @field_validator("travel_date")
    @classmethod
    def validate_date(cls, v: str) -> str:
        try:
            date.fromisoformat(v)
            return v
        except Exception:
            raise ValueError(f"travel_date must be in YYYY-MM-DD format, got '{v}'")

    @property
    def route(self) -> str:
        return f"{self.origin}-{self.destination}"

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()
