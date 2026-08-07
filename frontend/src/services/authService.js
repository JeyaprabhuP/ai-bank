import api from "./api";

export async function login(username, password) {
  const res = await api.post("/login", { username, password });
  localStorage.setItem("access_token", res.data.access_token);
  localStorage.setItem(
    "user",
    JSON.stringify({
      username: res.data.username,
      role: res.data.role,
      customer_id: res.data.customer_id,
    })
  );
  return res.data;
}

export function logout() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("user");
}

export function getCurrentUser() {
  const raw = localStorage.getItem("user");
  return raw ? JSON.parse(raw) : null;
}

export function isAuthenticated() {
  return !!localStorage.getItem("access_token");
}
