# infer_server
## Admin API

The admin API is started automatically when running `python main.py`. It exposes batching configuration endpoints on port 8000:
- `GET /config/batching` returns current batch settings
- `POST /config/batching` with JSON `{ "batch_size": int, "queue_timeout": float }` updates the runtime behavior.
Standalone mode is still available by running `python admin_api.py`.

