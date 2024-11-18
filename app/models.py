from typing import Optional, List
from pydantic import BaseModel
from enum import Enum
from datetime import datetime

# Enum class for the role
class Role(str, Enum):
    user = "User"
    model = "Model"

class Message(BaseModel):
    text: str
    role: Role

class History(BaseModel):
    created:datetime = datetime.now() 
    history: List[Message]