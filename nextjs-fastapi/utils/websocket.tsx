
// create a websocket class that has a websocket attribute with a connect and disconnect method,
// and a method to send text through the websocket. it should be globally accessible across the 
// app.


import { useEffect, useState } from 'react';

class WebSocketClient {
  websocket: WebSocket | null;
  constructor() {
    this.websocket = null;
  }

  async connect(url: string, parseMessage: (message: string) => void) {
    console.log('websocket connecting...')
    this.websocket = new WebSocket(url);

    this.websocket.onmessage = (event) => {
        console.log("websocket message received: ", event.data);
        parseMessage(event.data);
    }

    return new Promise((resolve, reject) => {
        this.websocket?.addEventListener('open', () => {
            console.log("websocket connected.")
            resolve(true);
        });
        this.websocket?.addEventListener('error', () => {
            console.log("ERROR: websocket failed to connect.")
            resolve(false);
        });
    });
  }

  disconnect() {
    console.log("websocket disconnecting.")
    this.websocket?.close();
  }

  sendText(text: string) {
    console.log("sending text through websocket: ", text);
    this.websocket?.send(text);
  }
}

const useWebSocket = () => {
  const [websocket, setWebsocket] = useState<WebSocketClient | null>(null);

  useEffect(() => {
    const ws = new WebSocketClient();
    setWebsocket(ws);
  }, []);

  return websocket;
};

export default useWebSocket;
