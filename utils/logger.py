import time
import csv
import os
import logging
from contextlib import contextmanager
from uuid import uuid4
from collections import deque

# basic application logging configuration
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
LOG_FORMAT = "[%(levelname)s][%(name)s][%(asctime)s] %(message)s"
logging.basicConfig(level=getattr(logging, LOG_LEVEL, logging.INFO),
                    format=LOG_FORMAT)

def get_logger(name=None):
    """Return a module-level logger."""
    return logging.getLogger(name)

LOG_PATH = "logs/request_trace.csv"
# number of requests to keep for rolling average
ROLLING_WINDOW = int(os.environ.get("LOG_ROLLING_WINDOW", 20))

FIELDNAMES = [
    "request_id", "client_ip", "batch_size",
    "wait_ms", "trigger_type", "trigger_time_ms",
    "inference_ms", "postprocess_ms", "total_ms",
    "avg_task_duration_ms", "wait_level", "latency_level", "efficiency_tag"
]


def get_wait_level(wait_ms: float) -> str:
    """Classify waiting time into a qualitative level."""
    if wait_ms < 50:
        return "low"
    if wait_ms < 200:
        return "medium"
    return "high"


def get_latency_level(latency_ms: float) -> str:
    """Classify total latency into a qualitative level."""
    if latency_ms < 100:
        return "low"
    if latency_ms < 500:
        return "medium"
    return "high"


def get_efficiency_tag(wait_ms: float, latency_ms: float, avg_ms: float) -> str:
    """Generate a simple efficiency tag based on wait and latency ratios."""
    if latency_ms == 0:
        return "unknown"
    wait_ratio = wait_ms / latency_ms
    if wait_ratio < 0.2 and latency_ms <= avg_ms * 1.2:
        return "efficient"
    return "inefficient"

class RequestLogger:
    _recent_durations = deque(maxlen=ROLLING_WINDOW)

    def __init__(self):
        self.request_id = uuid4().hex[:8]
        self.start_times = {}
        self.fields = {
            "request_id": self.request_id,
            "wait_ms": 0,
            "trigger_time_ms": 0,
            "inference_ms": 0,
            "postprocess_ms": 0,
            "total_ms": 0,
        }
        self.time_ref = {}
        self._start_total = time.time()

    def set(self, key, value):
        self.fields[key] = value

    def update(self, kv_dict):
        self.fields.update(kv_dict)

    def set_mark(self, label):
        self.time_ref[label] = time.time()
        
    def get_mark(self, name: str):
        return self.time_ref.get(name)


    def duration(self, label):
        if label in self.time_ref:
            return (time.time() - self.time_ref[label]) * 1000
        return None
    
    def print_summary(self):
        req_log = logging.getLogger("request")
        req_log.info("[RequestLogger Summary]")
        for k, v in self.fields.items():
            req_log.info("  %s: %s", k, v)


    @contextmanager
    def phase(self, name):
        start = time.time()
        yield
        end = time.time()
        self.fields[f"{name}_ms"] = (end - start) * 1000

    def write(self):
        self.fields["total_ms"] = (time.time() - self._start_total) * 1000

        # update rolling statistics
        RequestLogger._recent_durations.append(self.fields["total_ms"])
        avg_ms = sum(RequestLogger._recent_durations) / len(RequestLogger._recent_durations)
        self.fields["avg_task_duration_ms"] = avg_ms

        # classification fields
        self.fields["wait_level"] = get_wait_level(self.fields.get("wait_ms", 0))
        self.fields["latency_level"] = get_latency_level(self.fields["total_ms"])
        self.fields["efficiency_tag"] = get_efficiency_tag(
            self.fields.get("wait_ms", 0), self.fields["total_ms"], avg_ms
        )

        is_new = not os.path.exists(LOG_PATH)
        with open(LOG_PATH, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            if is_new:
                writer.writeheader()
            writer.writerow(self.fields)

@contextmanager
def logger_context():
    logger = RequestLogger()
    try:
        yield logger
    finally:
        pass
