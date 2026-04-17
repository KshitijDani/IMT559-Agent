from datetime import datetime, timedelta, timezone


def login(client, monkeypatch, token_payload=None):
    payload = token_payload or {
        "sub": "google-user-1",
        "email": "user1@example.com",
        "name": "User One",
        "picture": "https://example.com/avatar.png",
    }
    monkeypatch.setattr("app.main.verify_google_token", lambda _: payload)
    response = client.post("/auth/google/login", json={"id_token": "fake-token"})
    assert response.status_code == 200
    return response


def login_as_dev_user(client):
    response = client.post("/auth/dev-login")
    assert response.status_code == 200
    return response


def test_google_login_creates_and_reuses_user(client, monkeypatch):
    first = login(client, monkeypatch)
    second = login(client, monkeypatch)

    assert first.json()["email"] == "user1@example.com"
    assert second.json()["id"] == first.json()["id"]


def test_unauthenticated_requests_are_rejected(client):
    response = client.get("/api/workouts")
    assert response.status_code == 401


def test_dev_login_creates_local_user(client):
    response = client.post("/auth/dev-login")

    assert response.status_code == 200
    body = response.json()
    assert body["email"] == "dev@example.com"
    assert body["full_name"] == "Local Developer"


def test_create_manual_workout(client, monkeypatch):
    login_as_dev_user(client)

    response = client.post(
        "/api/workouts",
        json={
            "workoutType": "run",
            "durationMinutes": 35,
            "workoutAt": datetime.now(timezone.utc).isoformat(),
            "locationName": "Green Lake",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["workout_type"] == "run"
    assert body["location_name"] == "Green Lake"
    assert body["latitude"] is None


def test_custom_workout_requires_name(client, monkeypatch):
    login_as_dev_user(client)

    response = client.post(
        "/api/workouts",
        json={
            "workoutType": "custom",
            "durationMinutes": 20,
            "workoutAt": datetime.now(timezone.utc).isoformat(),
            "locationName": "Home",
        },
    )

    assert response.status_code == 422


def test_gps_location_is_saved(client, monkeypatch):
    login_as_dev_user(client)

    response = client.post(
        "/api/workouts",
        json={
            "workoutType": "walk",
            "durationMinutes": 45,
            "workoutAt": datetime.now(timezone.utc).isoformat(),
            "locationName": "Waterfront",
            "latitude": 47.6062,
            "longitude": -122.3321,
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["latitude"] == 47.6062
    assert body["longitude"] == -122.3321


def test_history_is_sorted_and_isolated(client, monkeypatch):
    login_as_dev_user(client)

    client.post(
        "/api/workouts",
        json={
            "workoutType": "run",
            "durationMinutes": 20,
            "workoutAt": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
            "locationName": "Park",
        },
    )
    client.post(
        "/api/workouts",
        json={
            "workoutType": "bike",
            "durationMinutes": 60,
            "workoutAt": datetime.now(timezone.utc).isoformat(),
            "locationName": "Trail",
        },
    )

    response = client.get("/api/workouts")
    body = response.json()

    assert response.status_code == 200
    assert len(body) == 2
    assert body[0]["workout_type"] == "bike"


def test_dashboard_totals_match_workouts(client, monkeypatch):
    login_as_dev_user(client)
    now = datetime.now(timezone.utc)
    client.post(
        "/api/workouts",
        json={
            "workoutType": "gym",
            "durationMinutes": 50,
            "workoutAt": now.isoformat(),
            "locationName": "Gym",
        },
    )
    client.post(
        "/api/workouts",
        json={
            "workoutType": "yoga",
            "durationMinutes": 30,
            "workoutAt": (now - timedelta(days=10)).isoformat(),
            "locationName": "Studio",
        },
    )

    response = client.get("/api/dashboard")
    body = response.json()

    assert response.status_code == 200
    assert body["total_workouts"] == 2
    assert body["total_minutes"] == 80
    assert body["this_week_workouts"] == 1
    assert body["this_week_minutes"] == 50
    assert len(body["recent_workouts"]) == 2
