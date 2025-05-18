import boto3
from typing import List, Dict
from ..models import AWSResource

async def get_s3_buckets(region: str) -> List[AWSResource]:
    """Fetch S3 buckets with cost-relevant metrics"""
    client = boto3.client('s3', region_name=region)
    try:
        response = client.list_buckets()
        return [
            AWSResource(
                id=bucket['Name'],
                type="S3",
                state="Active",
                cost_estimate=0.0  # TODO: Add actual cost calculation
            )
            for bucket in response['Buckets']
        ]
    except Exception as e:
        raise Exception(f"S3 API Error: {str(e)}")