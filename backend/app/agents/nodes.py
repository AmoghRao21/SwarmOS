from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from app.core.config import get_settings
from app.agents.state import AgentState

settings = get_settings()

print(f"🚀 Loading Cloud Brain: Groq ({settings.GROQ_MODEL})")

# Initialize the Brain
llm = ChatGroq(
    api_key=settings.GROQ_API_KEY,
    model_name=settings.GROQ_MODEL,
    temperature=0
)

async def supervisor_node(state: AgentState):
    messages = state['messages']
    
    # The Supervisor's only job is to route.
    system_prompt = (
        "You are the Supervisor of a software development swarm. "
        "Your goal is to manage the workflow. "
        "If the request needs analysis, route to 'Researcher'. "
        "If the request needs code, route to 'Coder'. "
        "If the task is complete, route to 'FINISH'. "
        "Return ONLY the name of the next agent."
    )
    
    try:
        response = await llm.ainvoke([SystemMessage(content=system_prompt)] + messages)
        next_agent = response.content.strip()
        print(f"🤖 Supervisor Decision: {next_agent}")
    except Exception as e:
        print(f"❌ Supervisor Error: {e}")
        return {"next": "FINISH"}
    
    # Routing Safety Logic
    if "Researcher" in next_agent: return {"next": "Researcher"}
    if "Coder" in next_agent: return {"next": "Coder"}
    return {"next": "FINISH"}

async def researcher_node(state: AgentState):
    print("🔍 Researcher is thinking...")
    response = await llm.ainvoke([
        SystemMessage(content="You are a Senior Researcher. Analyze the user request and provide a technical plan."),
        *state['messages']
    ])
    return {"messages": [AIMessage(content=f"Researcher: {response.content}", name="Researcher")]}

async def coder_node(state: AgentState):
    print("💻 Coder is thinking...")
    response = await llm.ainvoke([
        SystemMessage(content="You are a Senior Engineer. Write the Python code for the request. Wrap code in ```python blocks."),
        *state['messages']
    ])
    return {"messages": [AIMessage(content=f"Coder: {response.content}", name="Coder")]}