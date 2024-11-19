import os
from fastapi.responses import HTMLResponse
import google.generativeai as genai
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import google.generativeai as genai


from motor.motor_asyncio import AsyncIOMotorClient  
from contextlib import asynccontextmanager


async def startup_db_client(app):
    app.mongodb_client = AsyncIOMotorClient(os.environ["MONGO_DB"])
    app.mongodb = app.mongodb_client.get_database("chat")
    print("MongoDB connected.")

# method to close the database connection
async def shutdown_db_client(app):
    app.mongodb_client.close()
    print("Database disconnected.")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # start the database connection
    await startup_db_client(app)
    yield
    await shutdown_db_client(app)


load_dotenv()

API_KEY = os.getenv("API_KEY")




html="""
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket(`ws://localhost:8000/ws/1`);
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""


genai.configure(api_key="AIzaSyDS7EqjsqDbitDOgi5aueKHG0rDjxrouR8")
model = genai.GenerativeModel("tunedModels/diabetes-2024-11-16")
chat_session = model.start_chat(
    history=[]
)

app = FastAPI(lifespan= lifespan)

@app.get("/")
def read_root():
    return HTMLResponse(html)



class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
    
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

from  .models import History, Role
import datetime

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    message_history = []
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"Message Sent was: {data}", websocket)
            message_history.append({"text":data, "role": "User"})
            result = await chat_session.send_message_async(data)
            message_history.append(Message(result.text))
            await manager.broadcast(f"{client_id} said {result.text} ")
            print(message_history)
    except WebSocketDisconnect:
        manager.disconnect(websocket) 
        result = await app.mongodb["history"].insert_one({"history":message_history, "created_at": datetime.datetime.now()})
        await manager.broadcast(f"Connections Closed")


from .models import Message
@app.post("/create_chat", response_model=Message)
async def insert_message(message: Message):
    result = await app.mongodb["chats"].insert_one(message.model_dump())
    inserted_message = await app.mongodb["chats"].find_one({"_id":result.inserted_id})
    return inserted_message