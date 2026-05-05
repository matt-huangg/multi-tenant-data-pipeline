"""Lambda entry point for the FastAPI HTTP API.

API Gateway sends Lambda events, while FastAPI expects ASGI requests. Mangum is
the adapter between those two protocols.
"""

from mangum import Mangum

from app.main import app


# Terraform points the HTTP Lambda handler at this symbol.
lambda_handler = Mangum(app)
