import threading
import time

class RPSMonitor:
    def __init__(self, interval=1.0):
        self.interval = interval
        self.counter = 0
        self.lock = threading.Lock()

    def increment(self):
        with self.lock:
            self.counter += 1

    def start(self):
        def loop():
            while True:
                time.sleep(self.interval)
                with self.lock:
                    rps = self.counter
                    self.counter = 0
                print(f"[Monitor] RPS = {rps}")
        threading.Thread(target=loop, daemon=True).start()

