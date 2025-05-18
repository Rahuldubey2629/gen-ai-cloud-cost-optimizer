import click
import requests
from typing import Dict, Any

@click.group()
def cli():
    """AWS Cost Optimizer CLI"""
    pass

@cli.command()
@click.option("--prompt", required=True, help="Your optimization query")
@click.option("--region", default="us-east-1", help="AWS region")
def analyze(prompt: str, region: str):
    """Analyze AWS resources for cost optimization"""
    try:
        response = requests.post(
            "http://localhost:8000/query",
            json={"prompt": prompt, "region": region}
        )
        click.echo(response.json())
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)

if __name__ == "__main__":
    cli()
