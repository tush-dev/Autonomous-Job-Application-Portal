type MessageHandler = (data: any) => void;

class WebSocketClient {
  private ws: WebSocket | null = null;
  private handlers = new Map<string, Set<MessageHandler>>();
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private url = "";
  private isConnected = false;

  connect() {
    const token = localStorage.getItem("access_token");
    if (!token) return;

    this.url = `ws://localhost:8000/ws?token=${token}`;

    try {
      this.ws = new WebSocket(this.url);
    } catch {
      return;
    }

    this.ws.onopen = () => {
      this.isConnected = true;
      this.emit("connected", null);
    };

    this.ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        this.emit(message.type, message.data);
        this.emit("*", message);
      } catch {
        // ignore
      }
    };

    this.ws.onclose = () => {
      this.isConnected = false;
      this.ws = null;
      this.emit("disconnected", null);
      this.reconnectTimer = setTimeout(() => this.connect(), 5000);
    };

    this.ws.onerror = () => {
      this.ws?.close();
    };
  }

  disconnect() {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    this.isConnected = false;
    this.ws?.close();
    this.ws = null;
  }

  on(event: string, handler: MessageHandler) {
    if (!this.handlers.has(event)) {
      this.handlers.set(event, new Set());
    }
    this.handlers.get(event)!.add(handler);
    return () => this.handlers.get(event)?.delete(handler);
  }

  private emit(event: string, data: any) {
    this.handlers.get(event)?.forEach((handler) => handler(data));
    if (event !== "*") {
      this.handlers.get("*")?.forEach((handler) => handler({ type: event, data }));
    }
  }
}

export const wsClient = new WebSocketClient();

export function useWebSocket() {
  return wsClient;
}
