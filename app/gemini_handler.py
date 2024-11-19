import google.generativeai as genai

# Set your OpenAI API key
genai.configure(api_key="AIzaSyDS7EqjsqDbitDOgi5aueKHG0rDjxrouR8")


model = genai.GenerativeModel(model_name="tunedModels/diabetes-2024-11-16")
history=[]
chat_session = model.start_chat(history=history)

async def generate_response(prompt: str) -> str:
    """Generate a response using Gemini AI's ChatCompletion."""
    try:
        response = chat_session.send_message(prompt)
        print(chat_session.history)
        return response.text
    except Exception as e:
        return f"Error: {e}"
