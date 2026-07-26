import { useEffect, useState } from "react";
import { api, downloadUrl } from "../api/client";
import type { Measurement } from "../types";

export function MeasurementsPage() {
  const [items,setItems]=useState<Measurement[]>([]);
  const [page,setPage]=useState(1);
  const [total,setTotal]=useState(0);
  const [from,setFrom]=useState("");
  const [to,setTo]=useState("");
  const [showTC,setShowTC]=useState(()=>localStorage.showTC!=="false");
  const query=`?page=${page}&page_size=50${from?`&date_from=${new Date(from).toISOString()}`:""}${to?`&date_to=${new Date(to).toISOString()}`:""}`;
  useEffect(()=>{api<{items:Measurement[];total:number}>(`/measurements${query}`).then(x=>{setItems(x.items);setTotal(x.total);});},[query]);
  useEffect(()=>{localStorage.showTC=String(showTC);},[showTC]);
  return <>
    <div className="page-title">
      <div><h1>История измерений</h1><p>{total} записей</p></div>
      <div className="actions">
        <a className="button secondary" href={downloadUrl(`/measurements/export.csv${query}`)}>CSV</a>
        <a className="button secondary" href={downloadUrl(`/measurements/export.json${query}`)}>JSON</a>
      </div>
    </div>
    <div className="filters">
      <label>С<input type="datetime-local" value={from} onChange={e=>{setFrom(e.target.value);setPage(1);}}/></label>
      <label>По<input type="datetime-local" value={to} onChange={e=>{setTo(e.target.value);setPage(1);}}/></label>
      <label className="check"><input type="checkbox" checked={showTC} onChange={e=>setShowTC(e.target.checked)}/>Показывать TC1–TC18</label>
    </div>
    <div className="table-wrap"><table><thead><tr>
      <th>Дата/время</th><th>Устройство</th><th>Эксперимент</th><th>Образец</th>
      {showTC&&Array.from({length:18},(_,i)=><th key={i}>TC{i+1}</th>)}
      <th>Lux</th><th>DHT T</th><th>DHT RH</th><th>BME T</th><th>BME RH</th><th>Давление</th><th>Газ</th><th>Soil</th>
    </tr></thead><tbody>{items.map(m=><tr key={m.id}>
      <td>{new Date(m.measured_at).toLocaleString()}</td><td>{m.device_id}</td><td>{m.experiment_id||"—"}</td><td>{m.sample}</td>
      {showTC&&m.thermocouples_c.map((v,i)=><td className={v==null?"null":""} key={i}>{v??"Нет данных"}</td>)}
      <td>{m.lux??"—"}</td><td>{m.dht22.temperature_c??"—"}</td><td>{m.dht22.humidity_percent??"—"}</td>
      <td>{m.bme680.temperature_c??"—"}</td><td>{m.bme680.humidity_percent??"—"}</td><td>{m.bme680.pressure_hpa??"—"}</td>
      <td>{m.bme680.gas_resistance_kohm??"—"}</td><td>{m.soil.moisture_percent??"—"}</td>
    </tr>)}</tbody></table></div>
    <div className="pagination"><button disabled={page===1} onClick={()=>setPage(x=>x-1)}>Назад</button><span>Страница {page}</span><button disabled={page*50>=total} onClick={()=>setPage(x=>x+1)}>Далее</button></div>
  </>;
}
