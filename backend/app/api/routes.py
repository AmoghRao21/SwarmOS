from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from uuid import UUID
from langchain_core.messages import HumanMessage

from app.core.database import get_db
from app.models import models
from app.schemas import schemas
from app.agents.graph import app as agent_graph
from app.core.socket import manager

router = APIRouter()

# --- WEBSOCKET HANDLER ---
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except Exception:
        manager.disconnect(websocket)

# --- THE CORE AI LOGIC ---
async def run_agent_workflow(task_id: UUID, db_session_factory):
    async with db_session_factory() as db:
        # 1. Get the Trigger Task (User Request)
        result = await db.execute(select(models.Task).where(models.Task.id == task_id))
        initial_task = result.scalars().first()
        if not initial_task: return

        workflow_id = initial_task.workflow_id
        
        # Mark User Request as "Running" then "Completed" immediately 
        # (Because the user is done asking)
        initial_task.status = "completed"
        await db.commit()
        
        # Broadcast User Node Completion
        await manager.broadcast({
            "type": "task_update",
            "task_id": str(initial_task.id),
            "status": "completed",
            "agent": "User",
            "workflow_id": str(workflow_id)
        })

        # 2. Helper to Create Dynamic Nodes
        async def create_node(agent_name, content, status="completed"):
            if not content: return
            
            new_task = models.Task(
                workflow_id=workflow_id,
                title=f"{agent_name} Action",
                assigned_agent=agent_name,
                status=status,
                output_payload={"result": content}
            )
            db.add(new_task)
            await db.commit()
            await db.refresh(new_task)
            
            await manager.broadcast({
                "type": "task_update",
                "task_id": str(new_task.id),
                "status": status,
                "agent": agent_name,
                "result": content,
                "workflow_id": str(workflow_id)
            })

        # 3. Run the Graph Loop
        initial_state = {
            "messages": [HumanMessage(content=initial_task.input_payload.get("prompt", ""))],
            "task_id": str(task_id),
            "next": "Supervisor"
        }

        try:
            # 'astream' gives us the output of each node as it finishes
            async for output in agent_graph.astream(initial_state):
                for agent_name, value in output.items():
                    content = ""
                    
                    # Extract content based on node type
                    if "messages" in value and len(value["messages"]) > 0:
                        content = value["messages"][-1].content
                    elif agent_name == "Supervisor":
                        content = f"Routing to: {value.get('next', 'Unknown')}"
                    
                    # Create the visual node
                    await create_node(agent_name, content)

        except Exception as e:
            await create_node("System", f"CRITICAL ERROR: {str(e)}", "failed")

        # 4. Mark Workflow as Done
        wf_result = await db.execute(select(models.Workflow).where(models.Workflow.id == workflow_id))
        workflow = wf_result.scalars().first()
        if workflow:
            workflow.status = "completed"
        await db.commit()

# --- STANDARD ENDPOINTS ---

@router.post("/users/", response_model=dict)
async def create_user(email: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.User).where(models.User.email == email))
    existing_user = result.scalars().first()
    if existing_user: return {"id": existing_user.id, "status": "exists"}
    
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
        title="User Request",
        assigned_agent="User",
        status="queued",
        input_payload={"prompt": workflow_in.initial_prompt}
    )
    db.add(task)
    await db.commit()
    
    from app.core.database import AsyncSessionLocal
    background_tasks.add_task(run_agent_workflow, task.id, AsyncSessionLocal)
    
    query = select(models.Workflow).where(models.Workflow.id == workflow.id).options(selectinload(models.Workflow.tasks))
    result = await db.execute(query)
    return result.scalars().first()

@router.get("/workflows/{workflow_id}", response_model=schemas.WorkflowResponse)
async def read_workflow(workflow_id: UUID, db: AsyncSession = Depends(get_db)):
    query = select(models.Workflow).where(models.Workflow.id == workflow_id).options(selectinload(models.Workflow.tasks))
    result = await db.execute(query)
    workflow = result.scalars().first()
    if not workflow: raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow