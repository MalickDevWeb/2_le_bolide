from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, ConfigDict, Field
from typing import Dict
import asyncio
import logging
import random
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Le Bolide", description="Microservice IoT Asynchrone")

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]

    async def broadcast(self, message: dict):
        tasks = [connection.send_json(message) for connection in self.active_connections.values()]
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

manager = ConnectionManager()

# Background Task to simulate High-Frequency IoT incoming data
async def generate_iot_data():
    while True:
        await asyncio.sleep(0.5) # Send data every 500ms
        payload = {
            "sensor_id": "SENSOR-PRO-A1",
            "value": round(random.uniform(20.0, 85.0), 2),
            "timestamp": int(time.time()),
            "status": "processed"
        }
        await manager.broadcast(payload)

@app.on_event("startup")
async def startup_event():
    # Start the IoT generator loop in background
    asyncio.create_task(generate_iot_data())

@app.get("/")
async def get_dashboard():
    with open("templates/index.html", "r") as f:
        html = f.read()
    return HTMLResponse(html)

@app.websocket("/ws/stream/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(client_id)
