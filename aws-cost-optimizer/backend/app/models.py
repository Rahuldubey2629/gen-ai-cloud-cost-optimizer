from pydantic import BaseModel
from typing import List, Optional

class QueryRequest(BaseModel):
    prompt: str
    region: Optional[str] = None

class AWSResource(BaseModel):
    id: str
    type: str
    state: str
    cost_estimate: float

class CostAnalysisResponse(BaseModel):
    resources: List[AWSResource]
    recommendations: List[str]
    estimated_savings: float
