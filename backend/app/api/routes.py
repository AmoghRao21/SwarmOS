from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from uuid import UUID
from langchain_core.messages import HumanMessage

from app.core.database import get_db
from app.models import models
from app.schemas import schemas
from app.agents.graph import app as agent_graph

router = APIRouter()

async def run_agent_workflow(task_id: UUID, db_session_factory):
    async with db_session_factory() as db:
        result = await db.execute(select(models.Task).where(models.Task.id == task_id))
        task = result.scalars().first()
        if not task:
            return

        task.status = "running"
        await db.commit()

        initial_state = {
            "messages": [HumanMessage(content=task.input_payload.get("prompt", ""))],
            "task_id": str(task_id),
            "next": "Supervisor"
        }
        
        final_state = await agent_graph.ainvoke(initial_state)
        
        last_message = final_state["messages"][-1].content
        task.output_payload = {"result": last_message}
        task.status = "completed"
        await db.commit()

@router.post("/users/", response_model=dict)
async def create_user(email: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.User).where(models.User.email == email))
    existing_user = result.scalars().first()
    if existing_user:
        return {"id": existing_user.id, "status": "exists"}
    
    new_user = models.User(email=email)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return {"id": new_user.id, "status": "created"}

@router.post("/workflows/", response_model=schemas.WorkflowResponse)
async def create_workflow(
    workflow_in: schemas.WorkflowCreate, 
    user_id: UUID, 
    background_tasks: BackgroundTasks, 
    db: AsyncSession = Depends(get_db),
):
    workflow = models.Workflow(title=workflow_in.title, user_id=user_id, status="pending")
    db.add(workflow)
    await db.commit()
    await db.refresh(workflow)

    task = models.Task(
        workflow_id=workflow.id,
        title="Initial Request",
        assigned_agent="Supervisor",
        status="queued",
        input_payload={"prompt": workflow_in.initial_prompt}
    )
    db.add(task)
    await db.commit()
    
    from app.core.database import AsyncSessionLocal
    background_tasks.add_task(run_agent_workflow, task.id, AsyncSessionLocal)
    
    query = select(models.Workflow).where(models.Workflow.id == workflow.id).options(selectinload(models.Workflow.tasks))
    result = await db.execute(query)
    refreshed_workflow = result.scalars().first()
    
    return refreshed_workflow

@router.get("/workflows/{workflow_id}", response_model=schemas.WorkflowResponse)
async def read_workflow(workflow_id: UUID, db: AsyncSession = Depends(get_db)):
    query = select(models.Workflow).where(models.Workflow.id == workflow_id).options(selectinload(models.Workflow.tasks))
    result = await db.execute(query)
    workflow = result.scalars().first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow