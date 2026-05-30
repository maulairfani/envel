FROM python:3.12-slim

WORKDIR /app

# Deno binary untuk sandbox Pyodide (generative UI server-side validation).
# prefab_ui mencari `deno` via PATH; cold-start pertama mengunduh Pyodide
# (butuh egress jaringan) lalu cache di DENO_DIR.
COPY --from=denoland/deno:bin /deno /usr/local/bin/deno

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY alembic.ini ./
COPY alembic ./alembic

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
