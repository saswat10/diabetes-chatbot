from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from app.websocket_handler import handle_websocket
from app.db import mongodb
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Disconnect from MongoDB when the app shuts down."""
    await mongodb.connect()
    yield
    await mongodb.disconnect()


app = FastAPI(lifespan=lifespan)


@app.websocket("/chat/{session_id}")
async def chat_endpoint(websocket: WebSocket, session_id: str):
    await handle_websocket(websocket, session_id)
