import boto3
from datetime import datetime, timedelta
from typing import List
from ..models import AWSResource

async def get_ec2_instances(region: str) -> List[AWSResource]:
    """Fetch EC2 instances with utilization and cost data"""
    session = boto3.Session(region_name=region)
    ec2 = session.client('ec2')
    cloudwatch = session.client('cloudwatch')
    pricing = session.client('pricing', region_name='us-east-1')  # Pricing API only available in us-east-1
    
    try:
        instances = []
        response = ec2.describe_instances()
        
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                # Get CPU utilization
                cpu_stats = cloudwatch.get_metric_statistics(
                    Namespace='AWS/EC2',
                    MetricName='CPUUtilization',
                    Dimensions=[{'Name':'InstanceId', 'Value': instance['InstanceId']}],
                    StartTime=datetime.utcnow() - timedelta(days=14),
                    EndTime=datetime.utcnow(),
                    Period=86400,
                    Statistics=['Average']
                )
                avg_cpu = cpu_stats['Datapoints'][0]['Average'] if cpu_stats['Datapoints'] else 0
                
                # Get actual pricing
                cost = get_instance_price(pricing, instance['InstanceType'], region)
                
                instances.append(AWSResource(
                    id=instance['InstanceId'],
                    type=instance['InstanceType'],
                    state=instance['State']['Name'],
                    cost_estimate=cost * 730,  # Monthly estimate (24*30.5)
                    utilization=avg_cpu,
                    az=instance['Placement']['AvailabilityZone']
                ))
        
        return instances
    except Exception as e:
        raise Exception(f"EC2 Service Error: {str(e)}")

def get_instance_price(pricing_client, instance_type: str, region: str) -> float:
    """Get actual price from AWS Pricing API"""
    try:
        response = pricing_client.get_products(
            ServiceCode='AmazonEC2',
            Filters=[
                {'Type': 'TERM_MATCH', 'Field': 'instanceType', 'Value': instance_type},
                {'Type': 'TERM_MATCH', 'Field': 'location', 'Value': get_region_name(region)},
                {'Type': 'TERM_MATCH', 'Field': 'operatingSystem', 'Value': 'Linux'},
                {'Type': 'TERM_MATCH', 'Field': 'tenancy', 'Value': 'shared'},
                {'Type': 'TERM_MATCH', 'Field': 'preInstalledSw', 'Value': 'NA'},
                {'Type': 'TERM_MATCH', 'Field': 'capacitystatus', 'Value': 'Used'}
            ],
            MaxResults=1
        )
        price_item = json.loads(response['PriceList'][0])
        return float(price_item['terms']['OnDemand'].popitem()[1]['priceDimensions'].popitem()[1]['pricePerUnit']['USD'])
    except:
        return get_fallback_price(instance_type)

def get_region_name(region_code):
    """Convert region code to full name (e.g. us-east-1 -> US East (N. Virginia))"""
    endpoint_file = boto3.session.Session().get_config_variable('endpoints_url')
    with open(endpoint_file, 'r') as f:
        endpoints = json.load(f)
    return endpoints['partitions'][0]['regions'][region_code]['description']

def get_fallback_price(instance_type):
    """Fallback pricing when API fails"""
    prices = {
        't2.micro': 0.0116,
        't3.small': 0.0208,
        'm5.large': 0.096
    }
    return prices.get(instance_type, 0)