# infer_server
## Admin API

Run `python admin_api.py` to start a FastAPI server on port 8000 providing batching configuration endpoints:
- `GET /config/batching` returns current batch settings
- `POST /config/batching` with JSON `{ "batch_size": int, "queue_timeout": float }` updates the runtime behavior.

