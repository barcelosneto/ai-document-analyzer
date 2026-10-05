from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

class AnalysisRequest(BaseModel):
    text: str = Field(min_length=20, max_length=20000, pattern=r".*\S.*")

class Analysis(BaseModel):
    model_config = ConfigDict(extra="forbid")
    category: Literal["financial", "technical", "general"]
    summary: str = Field(min_length=1, max_length=1000)
    keywords: list[str] = Field(max_length=20)
    dates: list[str] = Field(max_length=20)
    warnings: list[str] = Field(max_length=20)

class AnalysisResponse(BaseModel):
    provider: Literal["mock", "llm"]
    analysis: Analysis
