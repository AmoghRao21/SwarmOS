from langgraph.graph import StateGraph, END
from app.agents.state import AgentState
from app.agents.nodes import supervisor_node, researcher_node, coder_node

workflow = StateGraph(AgentState)

workflow.add_node("Supervisor", supervisor_node)
workflow.add_node("Researcher", researcher_node)
workflow.add_node("Coder", coder_node)

workflow.set_entry_point("Supervisor")

workflow.add_conditional_edges(
    "Supervisor",
    lambda x: x['next'],
    {
        "Researcher": "Researcher",
        "Coder": "Coder",
        "FINISH": END
    }
)

workflow.add_edge("Researcher", "Supervisor")
workflow.add_edge("Coder", "Supervisor")

app = workflow.compile()