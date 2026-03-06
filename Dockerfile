FROM python:3.12-slim

WORKDIR /app

COPY . .
RUN pip install --no-cache-dir -e .
RUN chmod +x /app/docker/api-entrypoint.sh

ENTRYPOINT ["/app/docker/api-entrypoint.sh"]
CMD ["uvicorn", "assay.main:app", "--host", "0.0.0.0", "--port", "8000"]
