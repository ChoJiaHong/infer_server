import csv
import os
import time
import uuid
from contextlib import contextmanager

class RequestLogger:
    def __init__(self, client_ip):
        self.fields = {
            "request_id": uuid.uuid4().hex[:8],
            "client_ip": client_ip,
            "timestamp": time.time()
        }
        self.start_times = {}
        self.log_path = "logs/request_trace.csv"

    def set(self, key, value):
        self.fields[key] = value

    def set_many(self, **kwargs):
        self.fields.update(kwargs)

    def duration(self, phase):
        if phase in self.start_times:
            return time.time() - self.start_times[phase]
        return None

    @contextmanager
    def phase(self, name):
        start = time.time()
        yield
        end = time.time()
        self.fields[f"{name}_ms"] = (end - start) * 1000  # 轉為 ms

    def write(self):
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
        write_header = not os.path.exists(self.log_path)

        with open(self.log_path, mode="a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self.fields.keys())
            if write_header:
                writer.writeheader()
            writer.writerow(self.fields)
