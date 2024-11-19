from fastapi import WebSocket, WebSocketException, WebSocketDisconnect
from app.db import mongodb
from app.gemini_handler import generate_response, history
from datetime import datetime

connected_clients = {}

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


async def save_message(session_id: str, sender: str, message: str):
    """Save a chat message to the database with a timestamp."""
    async with mongodb.get_collection("chat_history") as collection:
        # Add a new message to the conversation
        timestamp = datetime.now()
        message_entry = {
            "role": sender,
            "text": message,
            "timestamp": timestamp
        }
        # Update or create the session's document
        await collection.update_one(
            {"session_id": session_id},
            {"$push": {"messages": message_entry}},
            upsert=True
        )

async def get_chat_history(session_id: str):
    """Retrieve chat history for a session."""
    async with mongodb.get_collection("chat_history") as collection:
        session = await collection.find_one({"session_id": session_id})
        if session:
            return session.get("messages", [])
        return []

async def handle_websocket(websocket: WebSocket, session_id: str):
    """Handle WebSocket connection and enable chat continuation."""
    # await websocket.accept()
    await manager.connect(websocket)
    try:
        # Retrieve and send chat history on connection
        chat_history = await get_chat_history(session_id)  # Fetch chat history
        for message in chat_history:
            sender = message["role"]
            text = message["text"]
            timestamp = message["timestamp"]

            # Send each message in the history to the client
            history.append({
                "role":sender,
                "text":text
            })
            await websocket.send_text(f"{sender.capitalize()}: {text} (at {timestamp})")

        while True:
            # Receive user message
            user_message = await websocket.receive_text()  # Receives a string
            await save_message(session_id, "user", user_message)

            # Generate bot response
            bot_response = await generate_response(user_message)  # Ensure this is async
            await save_message(session_id, "model", bot_response)

            # Send bot response to client
            await manager.broadcast(bot_response)
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
        print("WebSocket connection closed.")

