import os
from fastapi.responses import HTMLResponse
import google.generativeai as genai
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import google.generativeai as genai
from contextlib import asynccontextmanager

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

app = FastAPI()

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