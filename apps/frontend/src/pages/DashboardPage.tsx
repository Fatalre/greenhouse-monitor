import { useCallback, useEffect, useState } from "react";
import { api } from "../api/client";
import { MetricCard } from "../components/MetricCard";
import { LiveChart } from "../components/LiveChart";
import { StatusBadge } from "../components/StatusBadge";
import { useMeasurementsSocket } from "../hooks/useWebSocket";
import type { Measurement } from "../types";

export function DashboardPage() {
  const [data,setData] = useState<Measurement[]>([]);
  const [count,setCount] = useState(0);
  const load = useCallback(async()=>{
    try {
      const latest = await api<Measurement>("/measurements/latest");
      setData(current => current.length ? [...current.slice(-999),latest] : [latest]);
      const status = await api<{measurement_count:number}>("/system/status");
      setCount(status.measurement_count);
    } catch {}
  },[]);
  useEffect(()=>{load();const timer=setInterval(load,10000);return()=>clearInterval(timer);},[load]);
  const socket = useMeasurementsSocket(useCallback((m:Measurement)=>{
    setData(current=>current.some(v=>v.id===m.id)?current:[...current.slice(-999),m]);
    setCount(current=>current+1);
  },[]));
  const last=data.at(-1);
  const tc=last?.thermocouples_c.filter((x):x is number=>x!=null)||[];
  const online=!!last && Date.now()-new Date(last.received_at).getTime()<15000;
  return <>
    <div className="page-title">
      <div><h1>Панель эксперимента</h1><p>{last?.experiment_id||"Активный эксперимент не указан"}</p></div>
      <div className="status-row">
        <StatusBadge status={online?"ok":"error"} label={online?"Устройство online":"Устройство offline"}/>
        <StatusBadge status={socket==="connected"?"ok":socket==="connecting"?"warning":"error"} label={`WebSocket: ${socket}`}/>
      </div>
    </div>
    <div className="summary">
      <span>Всего измерений <b>{count}</b></span>
      <span>Последний пакет <b>{last?new Date(last.received_at).toLocaleString():"—"}</b></span>
    </div>
    <div className="metrics">
      <MetricCard title="DHT22 температура" value={last?.dht22.temperature_c} unit="°C" updated={last?.received_at}/>
      <MetricCard title="DHT22 влажность" value={last?.dht22.humidity_percent} unit="%"/>
      <MetricCard title="BME680 температура" value={last?.bme680.temperature_c} unit="°C"/>
      <MetricCard title="BME680 давление" value={last?.bme680.pressure_hpa} unit="hPa"/>
      <MetricCard title="Освещённость" value={last?.lux} unit="lx"/>
      <MetricCard title="Влажность почвы" value={last?.soil.moisture_percent} unit="%"/>
      <MetricCard title="Мин. термопара" value={tc.length?Math.min(...tc):null} unit="°C"/>
      <MetricCard title="Макс. термопара" value={tc.length?Math.max(...tc):null} unit="°C"/>
      <MetricCard title="Средняя термопар" value={tc.length?tc.reduce((a,b)=>a+b,0)/tc.length:null} unit="°C"/>
      <MetricCard title="Ошибки термопар" value={last?18-tc.length:null} unit="шт." status={last&&tc.length<18?"warning":"ok"}/>
    </div>
    <h2>Термопары TC1–TC18</h2><LiveChart data={data} kind="thermocouples"/>
    <div className="two-col">
      <div><h2>Температура воздуха</h2><LiveChart data={data} kind="temperature"/></div>
      <div><h2>Влажность воздуха</h2><LiveChart data={data} kind="humidity"/></div>
      <div><h2>Освещённость</h2><LiveChart data={data} kind="lux"/></div>
      <div><h2>Влажность почвы</h2><LiveChart data={data} kind="soil"/></div>
    </div>
  </>;
}
