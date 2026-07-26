import {FormEvent, useEffect, useState} from "react";
import {api} from "../api/client";
import type {Device} from "../types";

export function DevicesPage() {
    const [items, setItems] = useState<Device[]>([]);
    const [key, setKey] = useState("");

    const load = () => api<Device[]>("/devices").then(setItems);

    useEffect(() => {
        void load();
    }, []);

    async function create(event: FormEvent<HTMLFormElement>) {
        event.preventDefault();

        const form = new FormData(event.currentTarget);
        const device = await api<Device>("/devices", {
            method: "POST",
            body: JSON.stringify({
                device_id: form.get("device_id"),
                name: form.get("name"),
                description: form.get("description"),
            }),
        });

        setKey(device.api_key || "");
        event.currentTarget.reset();
        void load();
    }

    return <><h1>Устройства</h1>
        {key && <div className="alert warning"><b>Сохраните API-ключ сейчас:</b><code>{key}</code>
            <button onClick={() => navigator.clipboard.writeText(key)}>Копировать</button>
        </div>}
        <form className="inline-form" onSubmit={create}>
            <input name="device_id" placeholder="greenhouse-mega-02" required/>
            <input name="name" placeholder="Название" required/>
            <input name="description" placeholder="Описание"/>
            <button>Создать</button>
        </form>
        <div className="cards">{items.map(x => {
            const online = !!x.last_seen_at && Date.now() - new Date(x.last_seen_at).getTime() < 15000;
            return <article className="record" key={x.id}>
                <div><h3>{x.name}</h3><p>{x.device_id}</p>
                    <small>{online ? "Online" : "Offline"} · {x.last_seen_at ? new Date(x.last_seen_at).toLocaleString() : "данных ещё нет"}</small>
                </div>
                <button className="secondary" onClick={async () => {
                    if (!confirm("Старый ключ перестанет работать. Продолжить?")) return;
                    const device = await api<Device>(`/devices/${x.id}/rotate-key`, {method: "POST"});
                    setKey(device.api_key || "");
                }}>Новый API-ключ
                </button>
            </article>;
        })}</div>
    </>;
}
