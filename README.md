# infer_server
## Admin API

The admin API is started automatically when running `python main.py`. It exposes batching configuration endpoints on port 8000:
- `GET /config/batching` returns current batch settings
- `POST /config/batching` with JSON `{ "batch_size": int, "queue_timeout": float }` updates the runtime behavior.
Standalone mode is still available by running `python admin_api.py`.

## Selecting a Service

Set `task` in `config.py` or via the environment to choose which AI service
the server exposes. Supported values are `pose` and `gesture`.

## Building Cython extensions

The postprocessing stage ships with an optional Cython implementation for
better performance. To build the extension locally run:

```bash
pip install cython numpy
python setup.py build_ext --inplace
```

If the compiled module is unavailable, the pure Python fallback will be used.

## Metrics Export

The server exposes monitoring metrics for Prometheus on port `8001`. If
`prometheus_client` is installed, run the application normally and Prometheus
can scrape `http://<host>:8001/metrics` to collect queue size, request rate, and
completed request statistics.  If the library is missing or the metrics server
fails to start, the application continues to run without exporting metrics.


Metrics from the queue, completion, and RPS monitors are written as separate CSV
files under an automatically created `logs/` directory. Run `python metrics/merge_metrics.py`
to combine these into `logs/merged_stats.csv` for easier analysis.
