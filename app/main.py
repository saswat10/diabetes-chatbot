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
            var ws = new WebSocket("ws://localhost:8000/ws");
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

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message sent was:{data}")
        response = chat_session.send_message(data)
        await websocket.send_text(f"Message sent was:{response.text}")


from .models import Message
@app.post("/create_chat", response_model=Message)
async def insert_message(message: Message):
    result = await app.mongodb["chats"].insert_one(message.model_dump())
    inserted_message = await app.mongodb["chats"].find_one({"_id":result.inserted_id})
    return inserted_message