import time
import queue
from utils.logger import logger_context
from core.request_wrapper import RequestWrapper
from core.predict_pool import PredictThreadPool

class BatchProcessor:
    def __init__(self, predict_pool: PredictThreadPool, queue, batch_size, timeout):
        self.predict_pool = predict_pool
        self.queue = queue
        self.batch_size = batch_size
        self.timeout = timeout

    def run_forever(self):
        while True:
            wrappers = self._collect_batch()
            if wrappers:
                self._run_inference(wrappers)

    def _collect_batch(self):
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

        self.trigger_type = "full batch" if len(wrappers) == self.batch_size else "timeout"
        self.trigger_time = time.time() - start_time
        return wrappers

    def _run_inference(self, wrappers):
        for wrapper in wrappers:
            wrapper.logger.mark("infer_start")
            wrapper.logger.update({
                "batch_size": len(wrappers),
                "trigger_type": self.trigger_type,
                "trigger_time": self.trigger_time
            })

        batch_images = [w.frame for w in wrappers]
        self.predict_pool.submit(batch_images, wrappers, self.trigger_time)
        return

