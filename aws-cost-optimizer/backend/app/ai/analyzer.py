from typing import Dict, List, Optional
from datetime import datetime, timedelta
import boto3
import json
from ..models import QueryRequest, CostAnalysisResponse, AWSResource

class CostAnalyzer:
    def __init__(self):
        self.ec2 = boto3.client('ec2')
        self.cloudwatch = boto3.client('cloudwatch')
        self.ce = boto3.client('ce')
        
        # Pricing reference data (fallback if Pricing API fails)
        self.price_reference = {
            'us-east-1': {
                't2.micro': 0.0116,
                't3.small': 0.0208,
                'm5.large': 0.096
            }
        }

    async def analyze_cost(self, request: QueryRequest) -> CostAnalysisResponse:
        """Main analysis method that coordinates all checks"""
        region = request.region or 'us-east-1'
        recommendations = []
        resources = []
        estimated_savings = 0.0
        
        # Get EC2 instances with utilization data
        ec2_instances = self._get_ec2_instances(region)
        resources.extend(ec2_instances)
        
        # Generate recommendations
        for instance in ec2_instances:
            rec, savings = self._analyze_ec2_instance(instance)
            if rec:
                recommendations.append(rec)
                estimated_savings += savings
        
        # Add general recommendations
        recommendations.extend(self._get_general_recommendations(region))
        
        return CostAnalysisResponse(
            resources=resources,
            recommendations=recommendations,
            estimated_savings=round(estimated_savings, 2)
        )

    def _get_ec2_instances(self, region: str) -> List[AWSResource]:
        """Get EC2 instances with utilization metrics"""
        instances = []
        response = self.ec2.describe_instances()
        
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                # Get CPU utilization
                cpu_stats = self.cloudwatch.get_metric_statistics(
                    Namespace='AWS/EC2',
                    MetricName='CPUUtilization',
                    Dimensions=[{'Name':'InstanceId', 'Value': instance['InstanceId']}],
                    StartTime=datetime.utcnow() - timedelta(days=14),
                    EndTime=datetime.utcnow(),
                    Period=86400,
                    Statistics=['Average']
                )
                avg_cpu = cpu_stats['Datapoints'][0]['Average'] if cpu_stats['Datapoints'] else 0
                
                instances.append(AWSResource(
                    id=instance['InstanceId'],
                    type=instance['InstanceType'],
                    state=instance['State']['Name'],
                    cost_estimate=self._get_instance_cost(instance['InstanceType'], region),
                    utilization=avg_cpu,
                    region=region
                ))
        
        return instances

    def _analyze_ec2_instance(self, instance: AWSResource) -> tuple:
        """Generate specific recommendations for an EC2 instance"""
        if instance.state != 'running':
            return f"Terminate stopped instance {instance.id} (saves ${instance.cost_estimate}/month)", instance.cost_estimate
        
        if instance.utilization < 15:
            smaller_type = self._get_smaller_instance_type(instance.type)
            if smaller_type:
                savings = instance.cost_estimate - self._get_instance_cost(smaller_type, instance.region)
                return (f"Downsize {instance.type} ({instance.id}) to {smaller_type} "
                       f"(current CPU: {instance.utilization}%, saves ${savings:.2f}/month)"), savings
        
        if instance.utilization > 80:
            return f"Investigate high CPU usage on {instance.id} ({instance.utilization}%)", 0
        
        return None, 0

    def _get_general_recommendations(self, region: str) -> List[str]:
        """Generate general cost optimization recommendations"""
        return [
            "Consider Reserved Instances for steady-state workloads",
            "Evaluate Spot Instances for fault-tolerant workloads",
            "Review unattached EBS volumes",
            "Check for obsolete snapshots"
        ]

    def _get_instance_cost(self, instance_type: str, region: str) -> float:
        """Get hourly cost for an instance type"""
        try:
            # Try AWS Pricing API
            pricing = boto3.client('pricing', region_name='us-east-1')
            response = pricing.get_products(
                ServiceCode='AmazonEC2',
                Filters=[
                    {'Type': 'TERM_MATCH', 'Field': 'instanceType', 'Value': instance_type},
                    {'Type': 'TERM_MATCH', 'Field': 'location', 'Value': self._get_region_name(region)},
                    {'Type': 'TERM_MATCH', 'Field': 'operatingSystem', 'Value': 'Linux'},
                    {'Type': 'TERM_MATCH', 'Field': 'tenancy', 'Value': 'shared'}
                ]
            )
            price_data = json.loads(response['PriceList'][0])
            return float(price_data['terms']['OnDemand'].popitem()[1]['priceDimensions'].popitem()[1]['pricePerUnit']['USD'])
        except:
            # Fallback to reference data
            return self.price_reference.get(region, {}).get(instance_type, 0)

    def _get_smaller_instance_type(self, current_type: str) -> Optional[str]:
        """Get next smaller instance type in same family"""
        type_map = {
            't2.micro': None,  # Already smallest
            't2.small': 't2.micro',
            't3.small': None,
            'm5.large': 'm5.xlarge'
        }
        return type_map.get(current_type)

    def _get_region_name(self, region_code: str) -> str:
        """Convert region code to full name"""
        region_map = {
            'us-east-1': 'US East (N. Virginia)',
            'us-west-2': 'US West (Oregon)'
        }
        return region_map.get(region_code, region_code)

async def analyze_cost(request: QueryRequest) -> CostAnalysisResponse:
    """Entry point for the analyzer"""
    return await CostAnalyzer().analyze_cost(request)