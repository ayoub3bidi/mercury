from typing import TypedDict

from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from tenacity import retry, stop_after_attempt, wait_exponential

from constants.settings import settings


class AgentState(TypedDict):
    prompt: str
    token_budget: int
    result: str


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.25, max=2))
def _complete(prompt: str, token_budget: int) -> str:
    model = ChatOpenAI(
        model="gpt-4o-mini",
        base_url=settings.LLM_BASE_URL,
        api_key=settings.LLM_API_KEY.get_secret_value(),
        timeout=settings.RUN_TIMEOUT_SECONDS,
        max_tokens=token_budget,
        max_retries=0,
    )
    return str(model.invoke(prompt).content)


def run_agent(state: AgentState) -> AgentState:
    return {**state, "result": _complete(state["prompt"], state["token_budget"])}


builder = StateGraph(AgentState)
builder.add_node("complete", run_agent)
builder.add_edge(START, "complete")
builder.add_edge("complete", END)
agent_graph = builder.compile()
