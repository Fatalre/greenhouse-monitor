import { useEffect, useRef, useState } from "react";
import type { Measurement } from "../types";

export function useMeasurementsSocket(onData: (m: Measurement) => void) {
  const [status, setStatus] = useState<"connecting"|"connected"|"disconnected">("connecting");
  const callback = useRef(onData);
  callback.current = onData;

  useEffect(() => {
    let socket: WebSocket | undefined;
    let timer = 0;
    let stopped = false;
    let attempt = 0;

    const connect = () => {
      setStatus("connecting");
      const configured = import.meta.env.VITE_WS_URL || "/api/v1/ws/measurements";
      const url = configured.startsWith("ws")
        ? configured
        : `${location.protocol === "https:" ? "wss" : "ws"}://${location.host}${configured}`;
      socket = new WebSocket(url);
      socket.onopen = () => {
        attempt = 0;
        setStatus("connected");
        socket?.send("hello");
      };
      socket.onmessage = event => {
        const message = JSON.parse(event.data);
        if (message.type === "measurement.created") callback.current(message.data);
      };
      socket.onclose = () => {
        setStatus("disconnected");
        if (!stopped) {
          timer = window.setTimeout(connect, Math.min(30000, 1000 * 2 ** attempt++));
        }
      };
      socket.onerror = () => socket?.close();
    };

    connect();
    return () => {
      stopped = true;
      clearTimeout(timer);
      socket?.close();
    };
  }, []);

  return status;
}
