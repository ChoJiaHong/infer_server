# infer_server

This gRPC service batches incoming images and performs pose detection with
multiple worker threads.

## Configuration

- `num_workers` in `config.py` controls the number of threads used for
  inference. Each thread creates its own `BatchWorker` on first use.

## Architecture

```
PoseDetectionService
    └─ BatchProcessor (collects requests)
        └─ PredictThreadPool → BatchWorker
```
