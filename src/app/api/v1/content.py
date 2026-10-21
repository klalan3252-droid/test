from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.agents.content_writer import write_content

router = APIRouter(prefix="/content", tags=["content"])


class ContentRequest(BaseModel):
    topic: str = Field(min_length=1)
    tone: str = Field(min_length=1)


class ContentResponse(BaseModel):
    topic: str
    tone: str
    content: str


@router.post("", response_model=ContentResponse)
def create_content(body: ContentRequest) -> ContentResponse:
    try:
        text = write_content(body.topic, body.tone)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return ContentResponse(topic=body.topic, tone=body.tone, content=text)
