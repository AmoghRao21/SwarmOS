from langchain_community.chat_models import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from app.core.config import get_settings
from app.agents.state import AgentState

settings = get_settings()

# Switch to Ollama (DeepSeek)
llm = ChatOllama(
    base_url=settings.OLLAMA_BASE_URL,
    model=settings.OLLAMA_MODEL,
    temperature=0
)

async def supervisor_node(state: AgentState):
    messages = state['messages']
    
    system_prompt = (
        "You are the Supervisor. Your team is: [Researcher, Coder]. "
        "Based on the user's request, decide who should act next. "
        "Return ONLY the name of the next agent: 'Researcher', 'Coder', or 'FINISH' if done."
    )
    
    # Invoking DeepSeek
    response = await llm.ainvoke([SystemMessage(content=system_prompt)] + messages)
    next_agent = response.content.strip()
    
    # Clean up potential extra text from local models (they can be chatty)
    if "Researcher" in next_agent:
        next_agent = "Researcher"
    elif "Coder" in next_agent:
        next_agent = "Coder"
    else:
        next_agent = "FINISH"
        
    return {"next": next_agent}

async def researcher_node(state: AgentState):
    # We can also use the LLM to simulate research if we don't have a search API yet
    response = await llm.ainvoke([SystemMessage(content="You are a researcher. Analyze the request.")] + state['messages'])
    return {
        "messages": [AIMessage(content=f"Researcher: {response.content}", name="Researcher")]
    }

async def coder_node(state: AgentState):
    response = await llm.ainvoke([SystemMessage(content="You are a Coder. Write the code for the request.")] + state['messages'])
    return {
        "messages": [AIMessage(content=f"Coder: {response.content}", name="Coder")]
    }