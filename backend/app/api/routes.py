from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from uuid import UUID

from app.core.database import get_db
from app.models import models
from app.schemas import schemas

router = APIRouter()

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
    db: AsyncSession = Depends(get_db)
):
    # 1. Create Workflow
    workflow = models.Workflow(
        title=workflow_in.title,
        user_id=user_id,
        status="pending"
    )
    db.add(workflow)
    await db.commit()
    await db.refresh(workflow)

    # 2. Create Initial Task
    task = models.Task(
        workflow_id=workflow.id,
        title="Initial Request",
        assigned_agent="Supervisor",
        status="queued",
        input_payload={"prompt": workflow_in.initial_prompt}
    )
    db.add(task)
    await db.commit()
    
    # --- FIX START ---
    # We must re-fetch the workflow with "selectinload" to get the tasks.
    # Otherwise, Pydantic triggers a lazy-load error (MissingGreenlet).
    query = (
        select(models.Workflow)
        .where(models.Workflow.id == workflow.id)
        .options(selectinload(models.Workflow.tasks))
    )
    result = await db.execute(query)
    refreshed_workflow = result.scalars().first()
    # --- FIX END ---
    
    return refreshed_workflow

@router.get("/workflows/{workflow_id}", response_model=schemas.WorkflowResponse)
async def read_workflow(workflow_id: UUID, db: AsyncSession = Depends(get_db)):
    query = (
        select(models.Workflow)
        .where(models.Workflow.id == workflow_id)
        .options(selectinload(models.Workflow.tasks))
    )
    result = await db.execute(query)
    workflow = result.scalars().first()
    
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
        
    return workflow