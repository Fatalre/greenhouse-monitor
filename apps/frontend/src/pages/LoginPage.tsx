import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api/client";

export function LoginPage() {
  const [error,setError] = useState("");
  const navigate = useNavigate();
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    try {
      await api("/auth/login", {
        method:"POST",
        body:JSON.stringify({username:form.get("username"),password:form.get("password")}),
      });
      navigate("/");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ошибка");
    }
  }
  return <div className="login"><form onSubmit={submit}>
    <h1>Greenhouse Monitor</h1>
    <p>Локальная система мониторинга эксперимента</p>
    <label>Логин<input name="username" defaultValue="admin" required/></label>
    <label>Пароль<input name="password" type="password" required/></label>
    {error && <div className="alert error">{error}</div>}
    <button>Войти</button>
  </form></div>;
}
