import time
import queue
from utils.logger import logger_context

class RequestWrapper:
    def __init__(self, frame):
        self.frame = frame
        self.result_queue = queue.Queue()
        self.enqueue_time = time.time()
        self.logger = logger_context()
        self.logger.mark("enqueue")

class BatchProcessor:
    def __init__(self, worker, queue, batch_size, timeout):
        self.worker = worker
        self.queue = queue
        self.batch_size = batch_size
        self.timeout = timeout

    def run_forever(self):
        while True:
            self._process_batch()

    def _process_batch(self):
        batch_images = []
        wrappers = []
        start_time = time.time()

        while len(batch_images) < self.batch_size and (time.time() - start_time) < self.timeout:
            try:
                wrapper = self.queue.get(timeout=0.01)
                batch_images.append(wrapper.frame)
                wrappers.append(wrapper)
            except queue.Empty:
                continue

        if batch_images:
            infer_start = time.time()
            trigger_time = infer_start - start_time
            trigger_type = "full batch" if len(batch_images) == self.batch_size else "timeout"
            batch_size = len(wrappers)

            for wrapper in wrappers:
                wrapper.logger.mark("infer_start")
                wrapper.logger.update({
                    "batch_size": batch_size,
                    "trigger_type": trigger_type,
                    "trigger_time": trigger_time
                })

            with wrappers[0].logger.phase("inference"):
                results = self.worker.predict(batch_images)
            infer_end = time.time()

            for wrapper, result in zip(wrappers, results):
                wrapper.result_queue.put(result)

            print(f"[Batch] Inference: {(infer_end - infer_start)*1000:.2f} ms, "
                  f"Total Cycle: {(time.time() - start_time)*1000:.2f} ms")
