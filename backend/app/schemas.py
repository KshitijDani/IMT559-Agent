from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


PRESET_WORKOUT_TYPES = [
    "run",
    "walk",
    "bike",
    "gym",
    "yoga",
    "swim",
    "hike",
    "sport",
    "custom",
]


def to_camel(value: str) -> str:
    head, *tail = value.split("_")
    return head + "".join(part.capitalize() for part in tail)


class GoogleLoginRequest(BaseModel):
    id_token: str = Field(min_length=1)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    full_name: str
    avatar_url: str | None


class WorkoutCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    workout_type: str
    custom_workout_name: str | None = None
    duration_minutes: int = Field(gt=0, le=1440)
    workout_at: datetime
    location_name: str = Field(min_length=1, max_length=255)
    latitude: float | None = None
    longitude: float | None = None

    @field_validator("workout_type")
    @classmethod
    def validate_workout_type(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized not in PRESET_WORKOUT_TYPES:
            raise ValueError("Unsupported workout type.")
        return normalized

    @field_validator("custom_workout_name")
    @classmethod
    def normalize_custom_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None

    @field_validator("location_name")
    @classmethod
    def normalize_location_name(cls, value: str) -> str:
        return value.strip()

    @field_validator("workout_at")
    @classmethod
    def ensure_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value

    @model_validator(mode="after")
    def validate_custom_name_requirement(self) -> "WorkoutCreate":
        if self.workout_type == "custom" and not self.custom_workout_name:
            raise ValueError("Custom workout name is required when workout type is custom.")
        return self


class WorkoutResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    workout_type: str
    custom_workout_name: str | None
    duration_minutes: int
    workout_at: datetime
    location_name: str
    latitude: float | None
    longitude: float | None
    created_at: datetime


class DashboardResponse(BaseModel):
    total_workouts: int
    total_minutes: int
    this_week_workouts: int
    this_week_minutes: int
    recent_workouts: list[WorkoutResponse]
