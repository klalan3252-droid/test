"""LangGraph multi-agent content writer: planner -> writer -> editor."""
from typing import Any, TypedDict

from langgraph.graph import END, START, StateGraph


class ContentState(TypedDict, total=False):
    topic: str
    tone: str
    outline: str
    draft: str
    final: str


def _ask(llm: Any, prompt: str) -> str:
    result = llm.invoke(prompt)
    content = getattr(result, "content", result)
    return content if isinstance(content, str) else str(content)


def build_graph(llm: Any):
    def planner(state: ContentState) -> dict[str, str]:
        return {
            "outline": _ask(
                llm,
                f"You are a content planner. Create an outline for an article "
                f"about: {state['topic']}\nPlan it for this tone: {state['tone']}",
            )
        }

    def writer(state: ContentState) -> dict[str, str]:
        return {
            "draft": _ask(
                llm,
                f"You are a content writer. Write an article about "
                f"{state['topic']} in a {state['tone']} tone, following this "
                f"outline:\n{state['outline']}",
            )
        }

    def editor(state: ContentState) -> dict[str, str]:
        return {
            "final": _ask(
                llm,
                f"You are an editor. Polish the draft below, fixing errors and "
                f"making sure it consistently keeps a {state['tone']} tone. "
                f"Return only the final text.\n\nDraft:\n{state['draft']}",
            )
        }

    graph = StateGraph(ContentState)
    graph.add_node("planner", planner)
    graph.add_node("writer", writer)
    graph.add_node("editor", editor)
    graph.add_edge(START, "planner")
    graph.add_edge("planner", "writer")
    graph.add_edge("writer", "editor")
    graph.add_edge("editor", END)
    return graph.compile()


def _default_llm():
    from langchain_anthropic import ChatAnthropic

    return ChatAnthropic(model="claude-sonnet-5-5")


def write_content(topic: str, tone: str, llm: Any = None) -> str:
    if not tone.strip():
        raise ValueError("tone must not be blank")
    if not topic.strip():
        raise ValueError("topic must not be blank")
    graph = build_graph(llm if llm is not None else _default_llm())
    return graph.invoke({"topic": topic, "tone": tone})["final"]
