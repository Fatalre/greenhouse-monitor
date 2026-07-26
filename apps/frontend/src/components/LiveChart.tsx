import { LineChart, Line, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer, CartesianGrid } from "recharts";
import type { Measurement } from "../types";

export function LiveChart({data,kind}:{data:Measurement[];kind:"thermocouples"|"temperature"|"humidity"|"lux"|"soil"}) {
  const rows = data.map(m => {
    const row: Record<string,string|number|null> = {time:new Date(m.measured_at).toLocaleTimeString()};
    if (kind === "thermocouples") m.thermocouples_c.forEach((v,i) => row[`TC${i+1}`] = v);
    if (kind === "temperature") { row.DHT22=m.dht22.temperature_c; row.BME680=m.bme680.temperature_c; }
    if (kind === "humidity") { row.DHT22=m.dht22.humidity_percent; row.BME680=m.bme680.humidity_percent; }
    if (kind === "lux") row.Lux=m.lux;
    if (kind === "soil") row.Soil=m.soil.moisture_percent;
    return row;
  });
  const keys = kind === "thermocouples"
    ? Array.from({length:18},(_,i)=>`TC${i+1}`)
    : kind === "temperature" || kind === "humidity"
      ? ["DHT22","BME680"] : kind === "lux" ? ["Lux"] : ["Soil"];
  return <div className="chart"><ResponsiveContainer width="100%" height={320}>
    <LineChart data={rows}>
      <CartesianGrid strokeDasharray="3 3"/><XAxis dataKey="time" minTickGap={30}/><YAxis/><Tooltip/><Legend/>
      {keys.map((key,index)=><Line key={key} type="monotone" dataKey={key} dot={false} connectNulls={false} stroke={`hsl(${(index*37)%360} 65% 48%)`}/>)}
    </LineChart>
  </ResponsiveContainer></div>;
}
