import { FormEvent, useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";
import {
  api,
  isAuthenticated,
  LoginResponse,
  setAccessToken,
} from "../api/client";

export function LoginPage() {
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const navigate = useNavigate();

  if (isAuthenticated()) {
    return <Navigate to="/" replace />;
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setIsSubmitting(true);

    const form = new FormData(event.currentTarget);

    try {
      const result = await api<LoginResponse>("/auth/login", {
        method: "POST",
        body: JSON.stringify({
          username: String(form.get("username") || ""),
          password: String(form.get("password") || ""),
        }),
      });

      setAccessToken(result.access_token);
      navigate("/", { replace: true });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ошибка входа");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="login">
      <form onSubmit={submit}>
        <h1>Greenhouse Monitor</h1>
        <p>Локальная система мониторинга эксперимента</p>

        <label>
          Логин
          <input name="username" defaultValue="admin" required />
        </label>

        <label>
          Пароль
          <input name="password" type="password" required />
        </label>

        {error && <div className="alert error">{error}</div>}

        <button disabled={isSubmitting}>
          {isSubmitting ? "Вход..." : "Войти"}
        </button>
      </form>
    </div>
  );
}