FROM python:3.12-slim

WORKDIR /app

# Deno binary for the Pyodide sandbox (generative UI server-side validation).
# prefab_ui looks for `deno` via PATH; the first cold-start downloads Pyodide
# (needs network egress) then caches it in DENO_DIR.
COPY --from=denoland/deno:bin /deno /usr/local/bin/deno

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY alembic.ini ./
COPY alembic ./alembic

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
