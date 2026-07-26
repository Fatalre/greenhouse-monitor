import { useEffect, useState } from "react";
import { api } from "../api/client";

export function SystemPage() {
  const [status,setStatus]=useState<any>();
  useEffect(()=>{const load=()=>api("/system/status").then(setStatus);load();const timer=setInterval(load,5000);return()=>clearInterval(timer);},[]);
  if(!status)return <p>Загрузка…</p>;
  const cards=[["Backend",status.backend],["PostgreSQL",status.database],["WebSocket-клиенты",status.websocket_clients],["Измерений",status.measurement_count],["Размер базы",status.database_size_bytes?`${(status.database_size_bytes/1024/1024).toFixed(1)} MB`:"—"],["Версия",status.version]];
  return <><h1>Состояние системы</h1><div className="metrics">{cards.map(([label,value])=><article className="metric-card" key={label}><h3>{label}</h3><div className="metric-value">{value}</div></article>)}</div><h2>Устройства</h2><pre>{JSON.stringify(status.devices,null,2)}</pre></>;
}
