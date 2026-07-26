export function StatusBadge({status,label}:{status:"ok"|"warning"|"error"|"neutral";label:string}) {
  return <span className={`badge ${status}`}><span aria-hidden>●</span>{label}</span>;
}
