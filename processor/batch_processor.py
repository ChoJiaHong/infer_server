import time
import queue
from utils.logger import logger_context, get_logger
from core.request_wrapper import RequestWrapper

class BatchProcessor:
    def __init__(self, worker, queue, batch_size, timeout):
        self.worker = worker
        self.queue = queue
        self.batch_size = batch_size
        self.timeout = timeout
        self.logger = get_logger(__name__)
        self.last_batch_size = 0
        self.last_trigger = None

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
        self.last_trigger = self.trigger_type
        if wrappers:
            self.logger.info(
                "Batch collected size=%d trigger=%s wait=%.3f", len(wrappers),
                self.trigger_type, self.trigger_time
            )
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

        self.logger.info("Inference start batch_size=%d", len(wrappers))
        with wrappers[0].logger.phase("inference"):
            results = self.worker.predict(batch_images)

        infer_end = time.time()
        self.logger.info(
            "Inference done %.2f ms, total cycle %.2f ms",
            (infer_end - infer_start)*1000,
            (time.time() - (infer_start - self.trigger_time))*1000,
        )

        self._dispatch_results(wrappers, results)
        self.last_batch_size = len(wrappers)

    def _dispatch_results(self, wrappers, results):
        self.logger.debug("Dispatching results to %d wrappers", len(wrappers))
        for wrapper, result in zip(wrappers, results):
            wrapper.result_queue.put(result)

    def get_last_batch_size(self):
        """Return the size of the most recently processed batch."""
        return self.last_batch_size

    def get_last_trigger(self):
        """Return the trigger type of the most recently collected batch."""
        return self.last_trigger
