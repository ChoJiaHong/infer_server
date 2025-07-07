import time
import queue
from utils.logger import logger_context, get_logger

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
        self.logger = logger_context()

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
            self.logger.info(
                "Batch collected size=%d trigger=%s wait=%.3f",
                batch_size,
                trigger_type,
                trigger_time,
            )

            for wrapper in wrappers:
                wrapper.logger.mark("infer_start")
                wrapper.logger.update({
                    "batch_size": batch_size,
                    "trigger_type": trigger_type,
                    "trigger_time": trigger_time
                })

            self.logger.info("Inference start batch_size=%d", batch_size)
            with wrappers[0].logger.phase("inference"):
                results = self.worker.predict(batch_images)
            infer_end = time.time()
            self.logger.info(
                "Inference done %.2f ms, total cycle %.2f ms",
                (infer_end - infer_start)*1000,
                (time.time() - start_time)*1000,
            )

            for wrapper, result in zip(wrappers, results):
                wrapper.result_queue.put(result)

            self.logger.debug("Dispatched results for batch of %d", batch_size)
