from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .services.ec2_service import get_ec2_instances
from .services.s3_service import get_s3_buckets
from .models import QueryRequest
from .services import ec2_service, s3_service
from .ai.analyzer import analyze_cost

app = FastAPI(title="AWS Cost Optimizer")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/query")
async def cost_analysis(request: QueryRequest):
    """Main endpoint for cost optimization queries"""
    return await analyze_cost(request)
