// Small wrapper around fetch for the FastAPI backend.
const BASE = import.meta.env.VITE_API_URL || "";

async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    const detail = Array.isArray(body.detail) ? body.detail[0].msg : body.detail;
    throw new Error(detail || `Request failed (${res.status})`);
  }
  return res.status === 204 ? null : res.json();
}

export const api = {
  listTasks: (params = {}) => {
    const query = new URLSearchParams(Object.entries(params).filter(([, v]) => v));
    return request(`/api/tasks?${query}`);
  },
  stats: () => request("/api/tasks/stats"),
  createTask: (data) => request("/api/tasks", { method: "POST", body: JSON.stringify(data) }),
  updateTask: (id, data) => request(`/api/tasks/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
  deleteTask: (id) => request(`/api/tasks/${id}`, { method: "DELETE" }),
};
