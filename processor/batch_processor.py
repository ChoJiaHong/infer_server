import time
import queue
from utils.logger import logger_context
from core.request_wrapper import RequestWrapper

class BatchProcessor:
    def __init__(self, worker, queue, batch_size, timeout):
        self.worker = worker
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
            wrapper.logger.set_mark("infer_start")
            wrapper.logger.update({
                "batch_size": len(wrappers),
                "trigger_type": self.trigger_type,
                "trigger_time": self.trigger_time
            })

        batch_images = [w.frame for w in wrappers]
        infer_start = time.time()

        with wrappers[0].logger.phase("inference"):
            results = self.worker.predict(batch_images)

        infer_end = time.time()
        print(f"[Batch] Inference: {(infer_end - infer_start)*1000:.2f} ms, "
              f"Total Cycle: {(time.time() - (infer_start - self.trigger_time))*1000:.2f} ms")

        self._dispatch_results(wrappers, results)

    def _dispatch_results(self, wrappers, results):
        for wrapper, result in zip(wrappers, results):
            wrapper.result_queue.put(result)
