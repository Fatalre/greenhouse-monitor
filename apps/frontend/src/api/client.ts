const API = import.meta.env.VITE_API_BASE_URL || "/api/v1";

export async function api<T>(path: string, init: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API}${path}`, {
    credentials: "include",
    headers: {"Content-Type":"application/json", ...(init.headers || {})},
    ...init,
  });
  if (!response.ok) {
    let message = `HTTP ${response.status}`;
    try {
      const data = await response.json();
      message = data.detail || data.error?.message || message;
    } catch {}
    throw new Error(message);
  }
  if (response.status === 204) return undefined as T;
  return response.json();
}

export const downloadUrl = (path: string) => `${API}${path}`;
