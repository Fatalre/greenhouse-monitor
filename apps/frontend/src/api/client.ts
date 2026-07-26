const API = import.meta.env.VITE_API_BASE_URL || "/api/v1";

const ACCESS_TOKEN_KEY = "greenhouse_access_token";

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export function getAccessToken(): string | null {
  return localStorage.getItem(ACCESS_TOKEN_KEY);
}

export function setAccessToken(token: string): void {
  localStorage.setItem(ACCESS_TOKEN_KEY, token);
}

export function clearAccessToken(): void {
  localStorage.removeItem(ACCESS_TOKEN_KEY);
}

export function isAuthenticated(): boolean {
  return Boolean(getAccessToken());
}

export async function api<T>(
  path: string,
  init: RequestInit = {},
): Promise<T> {
  const token = getAccessToken();

  const headers = new Headers(init.headers);

  if (init.body !== undefined && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${API}${path}`, {
    ...init,
    headers,
  });

  if (!response.ok) {
    let message = `HTTP ${response.status}`;

    try {
      const data = await response.json();
      message = data.detail || data.error?.message || message;
    } catch {
      // Ответ может не содержать JSON.
    }

    if (response.status === 401) {
      clearAccessToken();

      if (window.location.pathname !== "/login") {
        window.location.href = "/login";
      }
    }

    throw new Error(message);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

export const downloadUrl = (path: string): string => {
  const token = getAccessToken();

  if (!token) {
    return `${API}${path}`;
  }

  return `${API}${path}?access_token=${encodeURIComponent(token)}`;
};