# gen-ai-cloud-cost-optimizer
gen-ai-cloud-cost-optimizer

You are an expert backend engineer tasked with building a production-ready, optimized FastAPI backend service.

Requirements:
- Expose a POST endpoint /query that accepts JSON with a "prompt" string field.
- Detect the AWS region from the prompt (default to "us-east-1" if none found).
- Analyze the prompt to determine which AWS services are requested (e.g., EC2, S3, Lambda).
- Use boto3 to query only the requested AWS services dynamically, collecting relevant info:
  - For EC2: list instances with id, type, state, and availability zone.
  - For S3: list bucket names and creation dates.
- Integrate a generative AI function (stub or real) that analyzes the prompt and returns a string analysis.
- Return a JSON response with the region, requested AWS data, and AI analysis.
- Use environment variables for all sensitive info (AWS keys, AI keys).
- Include proper error handling and logging.
- Add CORS middleware allowing any origin.
- Write clear, maintainable, and modular Python code.
- Prefer async where appropriate to improve scalability.
- Document the code with comments.
- The code should be ready to deploy in a cloud or container environment.

Generate the full FastAPI backend Python code implementing this functionality.
And taining the model for more optimised response
Main goal of project is to give user a way to optimise the cost of aws resources
