FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
COPY data ./data
COPY dashboard ./dashboard
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir .
CMD ["uvicorn", "sales_retention_analytics_warehouse.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
