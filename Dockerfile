# 1. Base Image
FROM python:3.13-slim

# 2. Environment settings (optional but common)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Set working directory
WORKDIR /app

# 4. Copy dependency file first (important for caching)
COPY requirements.txt .

# 5. Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy application code
COPY . . 

# 7. Expose port (optional, documentation only)
EXPOSE 8000

# 8. Run the app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]