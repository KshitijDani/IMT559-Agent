import { GoogleLogin } from "@react-oauth/google";
import { useEffect, useState } from "react";
import { NavLink, Route, Routes, useNavigate } from "react-router-dom";
import {
  createWorkout,
  fetchCurrentUser,
  fetchDashboard,
  fetchWorkouts,
  loginAsDevUser,
  loginWithGoogle,
  logout
} from "./api";

const workoutOptions = [
  { value: "run", label: "Run" },
  { value: "walk", label: "Walk" },
  { value: "bike", label: "Bike" },
  { value: "gym", label: "Gym" },
  { value: "yoga", label: "Yoga" },
  { value: "swim", label: "Swim" },
  { value: "hike", label: "Hike" },
  { value: "sport", label: "Sport" },
  { value: "custom", label: "Custom" }
];

function formatWorkoutName(workout) {
  if (workout.workout_type === "custom") {
    return workout.custom_workout_name;
  }
  const option = workoutOptions.find((item) => item.value === workout.workout_type);
  return option ? option.label : workout.workout_type;
}

function formatDate(value) {
  return new Date(value).toLocaleString([], {
    dateStyle: "medium",
    timeStyle: "short"
  });
}

function DashboardPage({ dashboard, loading, onRefresh }) {
  if (loading) {
    return <section className="panel">Loading dashboard...</section>;
  }

  if (!dashboard) {
    return <section className="panel">No dashboard data yet.</section>;
  }

  return (
    <div className="stack">
      <section className="hero">
        <div>
          <p className="eyebrow">Exercise tracker</p>
          <h1>Your progress at a glance</h1>
          <p>Track sessions, stay consistent, and keep your recent activity in one place.</p>
        </div>
      </section>
      <section className="stats-grid">
        <article className="stat-card">
          <span>Total workouts</span>
          <strong>{dashboard.total_workouts}</strong>
        </article>
        <article className="stat-card">
          <span>Total minutes</span>
          <strong>{dashboard.total_minutes}</strong>
        </article>
        <article className="stat-card">
          <span>This week</span>
          <strong>{dashboard.this_week_workouts}</strong>
        </article>
        <article className="stat-card">
          <span>This week minutes</span>
          <strong>{dashboard.this_week_minutes}</strong>
        </article>
      </section>
      <section className="panel">
        <div className="section-header">
          <h2>Recent workouts</h2>
          <button className="ghost-button" onClick={onRefresh}>Refresh</button>
        </div>
        {dashboard.recent_workouts.length === 0 ? (
          <p className="empty-state">No workouts logged yet. Head to Log Workout to add your first session.</p>
        ) : (
          <div className="list">
            {dashboard.recent_workouts.map((workout) => (
              <article key={workout.id} className="list-item">
                <div>
                  <h3>{formatWorkoutName(workout)}</h3>
                  <p>{workout.location_name}</p>
                </div>
                <div className="list-meta">
                  <strong>{workout.duration_minutes} min</strong>
                  <span>{formatDate(workout.workout_at)}</span>
                </div>
              </article>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

function HistoryPage({ workouts, loading, onRefresh }) {
  return (
    <section className="panel">
      <div className="section-header">
        <h1>Workout history</h1>
        <button className="ghost-button" onClick={onRefresh}>Refresh</button>
      </div>
      {loading ? (
        <p>Loading workouts...</p>
      ) : workouts.length === 0 ? (
        <p className="empty-state">No workouts yet. Once you log a session, it will show up here.</p>
      ) : (
        <div className="list">
          {workouts.map((workout) => (
            <article key={workout.id} className="list-item">
              <div>
                <h3>{formatWorkoutName(workout)}</h3>
                <p>{workout.location_name}</p>
              </div>
              <div className="list-meta">
                <strong>{workout.duration_minutes} min</strong>
                <span>{formatDate(workout.workout_at)}</span>
              </div>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}

function WorkoutFormPage({ onWorkoutSaved }) {
  const [form, setForm] = useState({
    workoutType: "run",
    customWorkoutName: "",
    durationMinutes: "",
    workoutAt: new Date().toISOString().slice(0, 16),
    locationName: "",
    latitude: null,
    longitude: null
  });
  const [status, setStatus] = useState("");
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);
  const [locating, setLocating] = useState(false);
  const navigate = useNavigate();

  function updateField(field, value) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  async function detectLocation() {
    if (!navigator.geolocation) {
      setStatus("Geolocation is not supported in this browser. Please type a location instead.");
      return;
    }

    setLocating(true);
    setStatus("Detecting your location...");
    setError("");

    navigator.geolocation.getCurrentPosition(
      (position) => {
        setForm((current) => ({
          ...current,
          locationName: current.locationName || "Current location",
          latitude: position.coords.latitude,
          longitude: position.coords.longitude
        }));
        setStatus("Location captured. You can keep the label or edit it.");
        setLocating(false);
      },
      () => {
        setStatus("Location access was unavailable. You can enter the workout location manually.");
        setLocating(false);
      },
      { enableHighAccuracy: true, timeout: 8000 }
    );
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setSaving(true);
    setError("");
    setStatus("");

    try {
      await createWorkout({
        workoutType: form.workoutType,
        customWorkoutName: form.workoutType === "custom" ? form.customWorkoutName : null,
        durationMinutes: Number(form.durationMinutes),
        workoutAt: new Date(form.workoutAt).toISOString(),
        locationName: form.locationName,
        latitude: form.latitude,
        longitude: form.longitude
      });
      setStatus("Workout saved.");
      setForm({
        workoutType: "run",
        customWorkoutName: "",
        durationMinutes: "",
        workoutAt: new Date().toISOString().slice(0, 16),
        locationName: "",
        latitude: null,
        longitude: null
      });
      onWorkoutSaved();
      navigate("/history");
    } catch (submitError) {
      setError(submitError.message);
    } finally {
      setSaving(false);
    }
  }

  useEffect(() => {
    detectLocation();
  }, []);

  return (
    <section className="panel">
      <div className="section-header">
        <h1>Log a workout</h1>
        <button className="ghost-button" onClick={detectLocation} disabled={locating}>
          {locating ? "Locating..." : "Use current location"}
        </button>
      </div>
      <form className="workout-form" onSubmit={handleSubmit}>
        <label>
          Workout type
          <select
            value={form.workoutType}
            onChange={(event) => updateField("workoutType", event.target.value)}
          >
            {workoutOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </label>

        {form.workoutType === "custom" && (
          <label>
            Custom workout name
            <input
              type="text"
              value={form.customWorkoutName}
              onChange={(event) => updateField("customWorkoutName", event.target.value)}
              placeholder="Upper body circuit"
              required
            />
          </label>
        )}

        <label>
          Duration (minutes)
          <input
            type="number"
            min="1"
            max="1440"
            value={form.durationMinutes}
            onChange={(event) => updateField("durationMinutes", event.target.value)}
            required
          />
        </label>

        <label>
          Workout date and time
          <input
            type="datetime-local"
            value={form.workoutAt}
            onChange={(event) => updateField("workoutAt", event.target.value)}
            required
          />
        </label>

        <label>
          Location
          <input
            type="text"
            value={form.locationName}
            onChange={(event) => updateField("locationName", event.target.value)}
            placeholder="Green Lake"
            required
          />
        </label>

        {form.latitude !== null && form.longitude !== null ? (
          <p className="hint">
            GPS captured: {form.latitude.toFixed(4)}, {form.longitude.toFixed(4)}
          </p>
        ) : (
          <p className="hint">No GPS coordinates yet. Manual location entry still works.</p>
        )}

        {status ? <p className="status">{status}</p> : null}
        {error ? <p className="error">{error}</p> : null}

        <button className="primary-button" type="submit" disabled={saving}>
          {saving ? "Saving..." : "Save workout"}
        </button>
      </form>
    </section>
  );
}

function LoginPage({
  authBusy,
  authError,
  googleClientIdConfigured,
  onDevLogin,
  onGoogleLogin
}) {
  const bypassGoogleAuth = import.meta.env.ALLOW_DEV_AUTH === "true";

  return (
    <main className="login-shell">
      <section className="login-card">
        <p className="eyebrow">Exercise tracker</p>
        <h1>Keep your workouts in one clean log</h1>
        <p>
          Track sessions, capture where you worked out, and review your recent progress in one place.
        </p>
        {authError ? <p className="error">{authError}</p> : null}
        {bypassGoogleAuth ? (
          <button className="primary-button" onClick={onDevLogin} disabled={authBusy}>
            {authBusy ? "Entering app..." : "Enter app as dev user"}
          </button>
        ) : googleClientIdConfigured ? (
          <div className="login-actions">
            <GoogleLogin
              onSuccess={(credentialResponse) => {
                if (credentialResponse.credential) {
                  onGoogleLogin(credentialResponse.credential);
                }
              }}
              onError={() => onGoogleLogin("")}
              useOneTap
            />
          </div>
        ) : (
          <p className="hint">
            Google auth is not configured yet. Add <code>GOOGLE_CLIENT_ID</code> in the root{" "}
            <code>.env</code>, or enable the dev bypass flag.
          </p>
        )}
      </section>
    </main>
  );
}

export default function App() {
  const bypassGoogleAuth = import.meta.env.ALLOW_DEV_AUTH === "true";
  const googleClientIdConfigured = Boolean(import.meta.env.VITE_GOOGLE_CLIENT_ID);
  const [user, setUser] = useState(null);
  const [loadingUser, setLoadingUser] = useState(true);
  const [authBusy, setAuthBusy] = useState(false);
  const [authError, setAuthError] = useState("");
  const [dashboard, setDashboard] = useState(null);
  const [workouts, setWorkouts] = useState([]);
  const [dashboardLoading, setDashboardLoading] = useState(false);
  const [workoutsLoading, setWorkoutsLoading] = useState(false);
  const navigate = useNavigate();

  async function loadCurrentUser() {
    try {
      const currentUser = await fetchCurrentUser();
      setUser(currentUser);
      setAuthError("");
      return currentUser;
    } catch {
      setUser(null);
      return null;
    } finally {
      setLoadingUser(false);
    }
  }

  async function loadDashboard() {
    if (!user) {
      return;
    }
    setDashboardLoading(true);
    try {
      const data = await fetchDashboard();
      setDashboard(data);
    } finally {
      setDashboardLoading(false);
    }
  }

  async function loadWorkouts() {
    if (!user) {
      return;
    }
    setWorkoutsLoading(true);
    try {
      const data = await fetchWorkouts();
      setWorkouts(data);
    } finally {
      setWorkoutsLoading(false);
    }
  }

  async function handleLogout() {
    await logout();
    setAuthError("");
    setUser(null);
    setDashboard(null);
    setWorkouts([]);
    navigate("/dashboard");
  }

  async function handleDevLogin() {
    setAuthBusy(true);
    setAuthError("");
    try {
      const currentUser = await loginAsDevUser();
      setUser(currentUser);
    } catch (error) {
      setAuthError(error.message);
    } finally {
      setAuthBusy(false);
      setLoadingUser(false);
    }
  }

  async function handleGoogleLogin(credential) {
    if (!credential) {
      setAuthError("Google sign-in did not return a credential. Please try again.");
      return;
    }

    setAuthBusy(true);
    setAuthError("");
    try {
      const currentUser = await loginWithGoogle(credential);
      setUser(currentUser);
    } catch (error) {
      setAuthError(error.message);
    } finally {
      setAuthBusy(false);
      setLoadingUser(false);
    }
  }

  async function refreshAll() {
    await Promise.all([loadDashboard(), loadWorkouts()]);
  }

  useEffect(() => {
    async function initializeSession() {
      const currentUser = await loadCurrentUser();
      if (!currentUser && bypassGoogleAuth) {
        await handleDevLogin();
      }
    }

    initializeSession();
  }, []);

  useEffect(() => {
    if (user) {
      refreshAll();
    }
  }, [user]);

  if (loadingUser) {
    return <main className="login-shell"><section className="login-card">Loading...</section></main>;
  }

  if (!user) {
    return (
      <LoginPage
        authBusy={authBusy}
        authError={authError}
        googleClientIdConfigured={googleClientIdConfigured}
        onDevLogin={handleDevLogin}
        onGoogleLogin={handleGoogleLogin}
      />
    );
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div>
          <p className="eyebrow">Signed in</p>
          <h2>{user.full_name}</h2>
          <p>{user.email}</p>
        </div>
        <nav className="nav">
          <NavLink to="/dashboard">Dashboard</NavLink>
          <NavLink to="/log-workout">Log Workout</NavLink>
          <NavLink to="/history">History</NavLink>
        </nav>
        <button className="ghost-button" onClick={handleLogout}>Sign out</button>
      </aside>

      <main className="content">
        <Routes>
          <Route
            path="/"
            element={<DashboardPage dashboard={dashboard} loading={dashboardLoading} onRefresh={loadDashboard} />}
          />
          <Route
            path="/dashboard"
            element={<DashboardPage dashboard={dashboard} loading={dashboardLoading} onRefresh={loadDashboard} />}
          />
          <Route path="/log-workout" element={<WorkoutFormPage onWorkoutSaved={refreshAll} />} />
          <Route
            path="/history"
            element={<HistoryPage workouts={workouts} loading={workoutsLoading} onRefresh={loadWorkouts} />}
          />
        </Routes>
      </main>
    </div>
  );
}
