import time
import uuid
import os
import csv
import contextlib
import logging
from utils.logger import RequestLogger
class RequestLogger:
    def __init__(self, log_dir="logs", client_ip="None"):
        self.request_id = uuid.uuid4().hex[:8]
        self.timestamps = {}
        self.log_dir = log_dir
        self.client_ip = client_ip
        os.makedirs(log_dir, exist_ok=True)

    def mark(self, label):
        self.timestamps[label] = time.time()

    @contextlib.contextmanager
    def phase(self, label):
        start_key = f"{label}_start"
        end_key = f"{label}_end"
        self.mark(start_key)
        try:
            yield
        finally:
            self.mark(end_key)

    def duration(self, label):
        try:
            return (self.timestamps[f"{label}_end"] - self.timestamps[f"{label}_start"]) * 1000
        except KeyError:
            return None

    def export_csv(self):
        row = {
            "request_id": self.request_id,
            "client_ip": self.client_ip,
            "batch_size": self.batch_size,
            "wait_ms": self.duration("wait"),
            "trigger_type": self.trigger_type,
            "trigger_time_ms": self.trigger_time,
            "inference_ms": self.duration("inference"),
            "postprocess_ms": self.duration("postprocess"),
            "total_ms": self.compute_total_duration(),
        }

        csv_path = os.path.join(self.log_dir, "request_trace.csv")
        write_header = not os.path.exists(csv_path)

        with open(csv_path, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=row.keys())
            if write_header:
                writer.writeheader()
            writer.writerow(row)

    def print_summary(self):
        logger = logging.getLogger("request")
        logger.info(
            "[%s] wait=%.2fms | infer=%.2fms | post=%.2fms | total=%.2fms",
            self.request_id,
            self.duration('wait'),
            self.duration('inference'),
            self.duration('postprocess'),
            self.compute_total_duration(),
        )

    def compute_total_duration(self):
        d = 0
        for key in ["wait", "inference", "postprocess"]:
            dur = self.duration(key)
            if dur is not None:
                d += dur
        return d
