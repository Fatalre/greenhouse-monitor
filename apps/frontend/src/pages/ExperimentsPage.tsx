import { FormEvent, useEffect, useState } from "react";
import { api } from "../api/client";
import type { Experiment } from "../types";

export function ExperimentsPage() {
  const [items,setItems]=useState<Experiment[]>([]);
  const load=()=>api<Experiment[]>("/experiments").then(setItems);
  useEffect(load,[]);
  async function create(event:FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form=new FormData(event.currentTarget);
    await api("/experiments",{method:"POST",body:JSON.stringify({
      external_id:form.get("external_id"),name:form.get("name"),description:form.get("description"),
    })});
    event.currentTarget.reset();load();
  }
  return <><h1>Эксперименты</h1>
    <form className="inline-form" onSubmit={create}>
      <input name="external_id" placeholder="experiment-002" required/>
      <input name="name" placeholder="Название" required/>
      <input name="description" placeholder="Описание"/><button>Создать</button>
    </form>
    <div className="cards">{items.map(x=><article className="record" key={x.id}>
      <div><h3>{x.name}</h3><p>{x.external_id} · {x.description||"Без описания"}</p>
      <small>{x.started_at?new Date(x.started_at).toLocaleString():"Не начат"} — {x.finished_at?new Date(x.finished_at).toLocaleString():x.is_active?"идёт":"—"}</small></div>
      <div className="actions">
        {!x.is_active&&<button onClick={async()=>{if(items.some(i=>i.is_active)&&!confirm("Другой эксперимент активен. Завершить его и начать новый?"))return;await api(`/experiments/${x.id}/start`,{method:"POST"});load();}}>Начать</button>}
        {x.is_active&&<button className="danger" onClick={async()=>{await api(`/experiments/${x.id}/finish`,{method:"POST"});load();}}>Завершить</button>}
      </div>
    </article>)}</div>
  </>;
}
