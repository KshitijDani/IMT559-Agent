const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {})
    },
    ...options
  });

  if (response.status === 204) {
    return null;
  }

  const data = await response.json().catch(() => null);
  if (!response.ok) {
    const detail = data?.detail;
    const message = Array.isArray(detail)
      ? detail.map((item) => item.msg).join(", ")
      : detail || "Something went wrong.";
    throw new Error(message);
  }

  return data;
}

export function fetchCurrentUser() {
  return request("/api/me", { method: "GET" });
}

export function loginWithGoogle(idToken) {
  return request("/auth/google/login", {
    method: "POST",
    body: JSON.stringify({ id_token: idToken })
  });
}

export function loginAsDevUser() {
  return request("/auth/dev-login", {
    method: "POST"
  });
}

export function logout() {
  return request("/auth/logout", { method: "POST" });
}

export function fetchDashboard() {
  return request("/api/dashboard", { method: "GET" });
}

export function fetchWorkouts() {
  return request("/api/workouts", { method: "GET" });
}

export function createWorkout(payload) {
  return request("/api/workouts", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}
