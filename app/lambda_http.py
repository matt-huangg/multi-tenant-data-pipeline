"""Lambda entry point for the FastAPI HTTP API."""

from mangum import Mangum

from app.main import app


lambda_handler = Mangum(app)
