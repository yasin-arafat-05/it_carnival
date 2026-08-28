from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class InputMessage(BaseModel):
    message: Optional[str] = Field(default=None, description="User question or input prompt")
    checkpoint_id: str = Field(default="", description="LangGraph thread checkpoint ID for conversation history")
    workflow_type: str = Field(default="demo_workflow", description="Workflow type to execute")
    resume_data: Optional[Dict[str, Any]] = Field(default=None, description="Data passed when resuming a paused graph (HITL)")
