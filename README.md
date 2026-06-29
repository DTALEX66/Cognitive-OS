# Cognitive-OS v2

Cognitive-OS is the front runtime for the Knowledge-Base and Inspiration-Research projects. It turns incoming material into routed cognitive objects, memory records, execution traces, evaluation results, and machine lessons.

## Run

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

For a new Windows development machine, run the repository environment setup first:

```powershell
.\scripts\setup_env.ps1
.\.venv\Scripts\python.exe scripts\doctor_environment.py --fix --check-files
```

The cross-device handoff plan is in `workspace/DEVELOPMENT_HANDOFF.md`.

## Current API Surface

| Endpoint | Purpose |
| --- | --- |
| `GET /health` | Health check |
| `POST /ingest` | Ingest one text object |
| `POST /ingest/file` | Ingest one project-local Markdown or text file |
| `POST /ingest/directory` | Ingest a project-local directory of Markdown or text files |
| `POST /route` | Return the attention route for one text object |
| `POST /run` | Execute the minimum cognitive loop |
| `POST /memory/search` | Search saved memory records |
| `GET /memory/lessons` | List machine lessons |
| `GET /traces` | List execution traces |
| `GET /tools` | List registered tools and risk levels |

## File Ingestion v1

File ingestion is intentionally local and conservative. Paths must stay inside this repository. The default directory pattern is `*.md`, the supported extensions are `.md`, `.markdown`, and `.txt`, and the current per-file size limit is 2 MB.

Useful payload keys:

- `path`: repository-local file or directory path.
- `source`: optional source label, such as `obsidian`, `knowledge-base`, or `inspiration-research`.
- `pattern`: optional directory glob, default `*.md`.
- `limit`: optional directory item limit, capped at 100.
- `metadata`: optional metadata object copied onto every ingested document.

## Smoke Test

```powershell
python -m compileall app
```

You can also use FastAPI interactive docs after starting the server:

```text
http://127.0.0.1:8000/docs
```
