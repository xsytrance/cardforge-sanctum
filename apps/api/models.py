from pydantic import BaseModel, Field
from typing import Any, Dict, Optional


class CardCreate(BaseModel):
    type: str
    title: str
    subtitle: str = ""
    description: str = ""
    fields: Dict[str, Any] = Field(default_factory=dict)
    source: Dict[str, Any] = Field(default_factory=dict)


class CardPatch(BaseModel):
    type: Optional[str] = None
    title: Optional[str] = None
    subtitle: Optional[str] = None
    description: Optional[str] = None
    fields: Optional[Dict[str, Any]] = None
    source: Optional[Dict[str, Any]] = None


class IngestFolderRequest(BaseModel):
    path: str
