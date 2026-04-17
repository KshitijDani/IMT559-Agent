from datetime import datetime, timedelta, timezone
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Response, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from .auth import clear_auth_cookie, create_access_token, get_current_user, set_auth_cookie, verify_google_token
from .config import settings
from .db import Base, engine, get_db
from .models import User, Workout
from .schemas import DashboardResponse, GoogleLoginRequest, UserResponse, WorkoutCreate, WorkoutResponse


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.cors_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/health")
def healthcheck() -> dict:
    return {"status": "ok"}


@app.post("/auth/google/login", response_model=UserResponse)
def google_login(payload: GoogleLoginRequest, response: Response, db: Session = Depends(get_db)) -> User:
    token_payload = verify_google_token(payload.id_token)

    google_sub = token_payload["sub"]
    email = token_payload.get("email", "")
    full_name = token_payload.get("name") or email
    avatar_url = token_payload.get("picture")

    user = db.execute(select(User).where(User.google_sub == google_sub)).scalar_one_or_none()
    if user is None:
        user = User(
            google_sub=google_sub,
            email=email,
            full_name=full_name,
            avatar_url=avatar_url,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        user.email = email
        user.full_name = full_name
        user.avatar_url = avatar_url
        db.commit()
        db.refresh(user)

    session_token = create_access_token(str(user.id))
    set_auth_cookie(response, session_token)
    return user


@app.post("/auth/dev-login", response_model=UserResponse)
def dev_login(response: Response, db: Session = Depends(get_db)) -> User:
    if not settings.allow_dev_auth:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dev login is disabled.")

    dev_sub = f"dev:{settings.dev_user_email}"
    user = db.execute(select(User).where(User.google_sub == dev_sub)).scalar_one_or_none()
    if user is None:
        user = User(
            google_sub=dev_sub,
            email=settings.dev_user_email,
            full_name=settings.dev_user_name,
            avatar_url=None,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    session_token = create_access_token(str(user.id))
    set_auth_cookie(response, session_token)
    return user


@app.post("/auth/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response) -> Response:
    clear_auth_cookie(response)
    return response


@app.get("/api/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@app.post("/api/workouts", response_model=WorkoutResponse, status_code=status.HTTP_201_CREATED)
def create_workout(
    workout_in: WorkoutCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Workout:
    workout = Workout(
        user_id=current_user.id,
        workout_type=workout_in.workout_type,
        custom_workout_name=workout_in.custom_workout_name,
        duration_minutes=workout_in.duration_minutes,
        workout_at=workout_in.workout_at,
        location_name=workout_in.location_name,
        latitude=workout_in.latitude,
        longitude=workout_in.longitude,
    )
    db.add(workout)
    db.commit()
    db.refresh(workout)
    return workout


@app.get("/api/workouts", response_model=list[WorkoutResponse])
def list_workouts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Workout]:
    statement = (
        select(Workout)
        .where(Workout.user_id == current_user.id)
        .order_by(desc(Workout.workout_at), desc(Workout.created_at))
    )
    return list(db.execute(statement).scalars().all())


@app.get("/api/dashboard", response_model=DashboardResponse)
def get_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DashboardResponse:
    workouts = list(
        db.execute(
            select(Workout)
            .where(Workout.user_id == current_user.id)
            .order_by(desc(Workout.workout_at), desc(Workout.created_at))
        ).scalars()
    )

    now = datetime.now(timezone.utc)
    week_start = now - timedelta(days=7)
    week_workouts = []
    for workout in workouts:
        workout_at = workout.workout_at
        if workout_at.tzinfo is None:
            workout_at = workout_at.replace(tzinfo=timezone.utc)
        if workout_at >= week_start:
            week_workouts.append(workout)

    return DashboardResponse(
        total_workouts=len(workouts),
        total_minutes=sum(workout.duration_minutes for workout in workouts),
        this_week_workouts=len(week_workouts),
        this_week_minutes=sum(workout.duration_minutes for workout in week_workouts),
        recent_workouts=workouts[:5],
    )
