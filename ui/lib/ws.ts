import { Frame, normalizeFrame } from "./frame";

export class UltraWSClient {
  private ws: WebSocket | null = null;

  constructor(
    private readonly url: string,
    private readonly onFrame: (frame: Frame) => void,
  ) {}

  connect(): void {
    this.ws = new WebSocket(this.url);
    this.ws.onmessage = (event) => {
      try {
        const parsed = JSON.parse(event.data) as Record<string, unknown>;
        this.onFrame(normalizeFrame(parsed));
      } catch {
        // Ignore malformed frames.
      }
    };
  }

  close(): void {
    this.ws?.close();
    this.ws = null;
  }
}
