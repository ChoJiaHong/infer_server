# Docker & Kubernetes Deployment

This guide shows how to build the container image and deploy the server on Kubernetes. It also covers configuring Prometheus to scrape metrics.

## Building the Docker image

Run the following command from the project root. The repository contains a `Dockerfile` that installs all dependencies and starts the gRPC server.

```bash
docker build -t infer-server:latest .
```

The resulting image can be pushed to your registry and referenced by Kubernetes manifests.

## Example Deployment YAML

Below is a minimal `Deployment` that runs the server and a corresponding `Service` that exposes both gRPC and metrics ports.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: infer-server
spec:
  replicas: 1
  selector:
    matchLabels:
      app: infer-server
  template:
    metadata:
      labels:
        app: infer-server
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8001"
        prometheus.io/path: "/metrics"
    spec:
      containers:
      - name: server
        image: infer-server:latest
        args: ["python", "main.py"]
        ports:
        - containerPort: 50052  # gRPC
        - containerPort: 8000   # admin API
        - containerPort: 8001   # Prometheus metrics
```

```yaml
---
apiVersion: v1
kind: Service
metadata:
  name: infer-server
spec:
  selector:
    app: infer-server
  ports:
  - name: grpc
    port: 50052
    targetPort: 50052
  - name: admin
    port: 8000
    targetPort: 8000
  - name: metrics
    port: 8001
    targetPort: 8001
```

Apply the manifests with `kubectl apply -f <file>.yaml` or create them directly using `kubectl create` commands.

## Prometheus discovery

Prometheus discovers the metrics endpoint through the annotations added to the pod template above. When `prometheus.io/scrape: "true"` is present, Prometheus scrapes `http://<pod_ip>:8001/metrics` automatically. Ensure your Prometheus configuration includes Kubernetes service discovery so that the scraper finds pods with this annotation.
