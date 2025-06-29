import threading


class SingleFrameProcessor:
    """Processes frames one at a time using a shared worker."""

    def __init__(self, worker):
        self.worker = worker
        self._lock = threading.Lock()

    def predict(self, frame):
        """Run prediction for a single frame in a thread-safe manner."""
        with self._lock:
            return self.worker.predict([frame])[0]
