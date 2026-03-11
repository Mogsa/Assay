FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml ./
RUN pip install --no-cache-dir -e . 2>/dev/null || pip install --no-cache-dir $(python -c "
import tomllib, pathlib
d = tomllib.loads(pathlib.Path('pyproject.toml').read_text())
print(' '.join(d['project']['dependencies']))
")

COPY . .
RUN pip install --no-cache-dir -e .
RUN chmod +x /app/docker/api-entrypoint.sh

ENTRYPOINT ["/app/docker/api-entrypoint.sh"]
CMD ["uvicorn", "assay.main:app", "--host", "0.0.0.0", "--port", "8000"]
