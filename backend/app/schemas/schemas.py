from pydantic import BaseModel
from uuid import UUID
from typing import List, Optional

# Used when creating a Workflow
class WorkflowCreate(BaseModel):
    title: str
    initial_prompt: str

# Used when sending a Task back to frontend
class TaskResponse(BaseModel):
    id: UUID
    title: str
    status: str
    assigned_agent: str

# Used when sending a Workflow back to frontend
class WorkflowResponse(BaseModel):
    id: UUID
    title: str
    status: str
    tasks: List[TaskResponse] = []