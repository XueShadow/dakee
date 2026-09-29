from typing import Any, Dict, List

from pydantic import BaseModel, Field, validator


class AnalysisRequest(BaseModel):
    text: str = Field(..., min_length=1)

    @validator('text', allow_reuse=True)
    def validate_text(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError('Please provide movie text before starting the analysis.')
        if len(cleaned) > 15000:
            raise ValueError('The input is too long. Please provide a shorter excerpt.')
        return cleaned


class AnalysisResult(BaseModel):
    summary: str
    themes: List[Dict[str, Any]]
    characters: List[Dict[str, Any]]
    relationships: List[Dict[str, Any]]
    conflicts: List[Dict[str, Any]]
    emotions: List[Dict[str, Any]]
    important_scenes: List[Dict[str, Any]]
    relational_dialectics: List[Dict[str, Any]]
    insights: List[Dict[str, Any]]
