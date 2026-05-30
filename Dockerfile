FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
COPY data ./data
COPY dashboard ./dashboard
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir .
CMD ["python", "-m", "sales_retention_analytics_warehouse.core"]
