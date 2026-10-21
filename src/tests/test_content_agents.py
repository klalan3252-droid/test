"""Tests for the LangGraph multi-agent content writing system.

Expected interface (app/agents/content_writer.py):
  build_graph(llm) -> compiled LangGraph graph; state in: topic, tone;
      state out: outline, draft, final (str)
  write_content(topic, tone, llm=None) -> str
  `llm` is any object with `invoke(prompt: str) -> str | message-with-.content`.
Agents (nodes): planner -> writer -> editor. Each prompt must carry the tone.
"""
import pytest


class FakeLLM:
    def __init__(self):
        self.prompts = []

    def invoke(self, prompt):
        self.prompts.append(str(prompt))
        return f"out{len(self.prompts)}"


def test_graph_runs_planner_writer_editor_in_order():
    from app.agents.content_writer import build_graph

    llm = FakeLLM()
    result = build_graph(llm).invoke({"topic": "solar power", "tone": "pirate"})
    assert len(llm.prompts) == 3
    assert result["outline"] == "out1"
    assert result["draft"] == "out2"
    assert result["final"] == "out3"


def test_custom_tone_and_topic_reach_every_agent():
    from app.agents.content_writer import build_graph

    llm = FakeLLM()
    build_graph(llm).invoke({"topic": "solar power", "tone": "sarcastic pirate"})
    for p in llm.prompts:
        assert "sarcastic pirate" in p
    assert "solar power" in llm.prompts[0]


def test_each_agent_receives_previous_output():
    from app.agents.content_writer import build_graph

    llm = FakeLLM()
    build_graph(llm).invoke({"topic": "t", "tone": "formal"})
    assert "out1" in llm.prompts[1]
    assert "out2" in llm.prompts[2]


def test_write_content_returns_final_text():
    from app.agents.content_writer import write_content

    assert write_content("cats", "witty", llm=FakeLLM()) == "out3"


def test_message_objects_with_content_supported():
    from app.agents.content_writer import write_content

    class Msg:
        def __init__(self, c):
            self.content = c

    class L:
        def invoke(self, prompt):
            return Msg("hello")

    assert write_content("a", "b", llm=L()) == "hello"


def test_blank_tone_rejected():
    from app.agents.content_writer import write_content

    with pytest.raises(ValueError):
        write_content("cats", "  ", llm=FakeLLM())


def test_api_endpoint_writes_content_in_tone(monkeypatch):
    pytest.importorskip("httpx")
    from fastapi.testclient import TestClient

    from app.api.v1 import content
    from app.main import create_app

    seen = {}

    def fake(topic, tone, llm=None):
        seen.update(topic=topic, tone=tone)
        return "article"

    monkeypatch.setattr(content, "write_content", fake)
    with TestClient(create_app()) as c:
        r = c.post("/api/v1/content", json={"topic": "x", "tone": "gothic"})
    assert r.status_code == 200
    assert r.json() == {"topic": "x", "tone": "gothic", "content": "article"}
    assert seen == {"topic": "x", "tone": "gothic"}


def test_api_validates_payload():
    pytest.importorskip("httpx")
    from fastapi.testclient import TestClient

    from app.main import create_app

    with TestClient(create_app()) as c:
        assert c.post("/api/v1/content", json={"tone": "x"}).status_code == 422


def test_langgraph_declared_as_dependency():
    import pathlib

    text = pathlib.Path("pyproject.toml").read_text()
    assert "langgraph" in text
