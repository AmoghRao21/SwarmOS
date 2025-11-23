from pydantic import BaseModel, ConfigDict
from uuid import UUID
from typing import List, Optional, Dict, Any

# --- INPUT SCHEMAS ---
class WorkflowCreate(BaseModel):
    title: str
    initial_prompt: str

# --- OUTPUT SCHEMAS ---
class TaskResponse(BaseModel):
    id: UUID
    title: str
    status: str
    assigned_agent: str
    
    # 👇 NEW: Allow these fields to be sent to frontend
    input_payload: Optional[Dict[str, Any]] = None
    output_payload: Optional[Dict[str, Any]] = None
    
    # This tells Pydantic to read from SQLAlchemy models
    model_config = ConfigDict(from_attributes=True)

class WorkflowResponse(BaseModel):
    id: UUID
    title: str
    status: str
    tasks: List[TaskResponse] = []
    
    model_config = ConfigDict(from_attributes=True)