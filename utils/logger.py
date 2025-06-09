import time
import csv
import os
from contextlib import contextmanager
from uuid import uuid4

LOG_PATH = "logs/request_trace.csv"
FIELDNAMES = [
    "request_id", "client_ip", "batch_size",
    "wait_ms", "trigger_type", "trigger_time_ms",
    "inference_ms", "postprocess_ms", "total_ms"
]

class RequestLogger:
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
        return self.marks.get(name)


    def duration(self, label):
        if label in self.time_ref:
            return (time.time() - self.time_ref[label]) * 1000
        return None
    
    def print_summary(self):
        print("[RequestLogger Summary]")
        for k, v in self.fields.items():
            print(f"  {k}: {v}")


    @contextmanager
    def phase(self, name):
        start = time.time()
        yield
        end = time.time()
        self.fields[f"{name}_ms"] = (end - start) * 1000

    def write(self):
        self.fields["total_ms"] = (time.time() - self._start_total) * 1000

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
