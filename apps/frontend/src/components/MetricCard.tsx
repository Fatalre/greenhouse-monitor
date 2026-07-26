import { StatusBadge } from "./StatusBadge";
export function MetricCard({title,value,unit,status="ok",updated}:{title:string;value:number|null|undefined;unit:string;status?:"ok"|"warning"|"error"|"neutral";updated?:string}) {
  return <article className="metric-card">
    <div className="metric-head">
      <h3>{title}</h3>
      <StatusBadge status={value == null ? "neutral" : status} label={value == null ? "Нет данных" : status === "ok" ? "OK" : status === "warning" ? "Внимание" : "Ошибка"}/>
    </div>
    <div className="metric-value">{value == null ? "—" : value.toFixed(2)} <span>{unit}</span></div>
    {updated && <small>Обновлено {new Date(updated).toLocaleTimeString()}</small>}
  </article>;
}
