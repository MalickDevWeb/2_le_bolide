from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request
from fastapi.responses import ORJSONResponse
from fastapi.middleware.gzip import GZipMiddleware
from pydantic import BaseModel, ConfigDict, Field
from typing import List, Dict
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Utilisation de ORJSONResponse pour des performances de sérialisation extrêmes
app = FastAPI(title="Le Bolide", description="Microservice IoT Asynchrone", default_response_class=ORJSONResponse)

# Middleware de compression pour minimiser la bande passante (Green IT)
app.add_middleware(GZipMiddleware, minimum_size=1000)

class SensorPayload(BaseModel):
    sensor_id: str = Field(..., min_length=3, max_length=50)
    value: float = Field(..., ge=-273.15, description="Température absolue minimum")
    timestamp: int
    
    # Rejet strict des champs non déclarés pour éviter la surcharge mémoire
    model_config = ConfigDict(extra="forbid", strict=True)

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"Client {client_id} connecté. Total: {len(self.active_connections)}")

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info(f"Client {client_id} déconnecté.")

    async def broadcast(self, message: dict):
        # Utilisation de asyncio.gather pour streamer en parallèle absolu
        tasks = [connection.send_json(message) for connection in self.active_connections.values()]
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

manager = ConnectionManager()

@app.websocket("/ws/stream/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_json()
            # Validation Pydantic "à la volée" et stricte
            payload = SensorPayload(**data)
            await manager.broadcast({"status": "processed", "data": payload.model_dump()})
    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        logger.error(f"Erreur WebSocket: {e}")
        await websocket.close(code=1008)
