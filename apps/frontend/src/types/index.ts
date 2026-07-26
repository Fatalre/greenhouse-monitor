export type Measurement = {
  id:number; device_id:string; experiment_id:string|null; sample:number;
  measured_at:string; received_at:string; timestamp_source:string;
  uptime_ms:number|null; thermocouples_c:(number|null)[]; lux:number|null;
  dht22:{temperature_c:number|null;humidity_percent:number|null};
  bme680:{temperature_c:number|null;humidity_percent:number|null;pressure_hpa:number|null;gas_resistance_kohm:number|null};
  soil:{raw:number|null;moisture_percent:number|null};
};
export type Device = {
  id:number; device_id:string; name:string; description:string|null;
  is_active:boolean; last_seen_at:string|null; created_at:string; api_key?:string;
};
export type Experiment = {
  id:number; external_id:string; name:string; description:string|null;
  started_at:string|null; finished_at:string|null; is_active:boolean; created_at:string;
};
