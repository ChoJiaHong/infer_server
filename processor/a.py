# processor/batch_processor.py

import time
from utils.logger import RequestLogger

class BatchProcessor:
    def __init__(self, queue, batch_size, timeout, model):
        self.queue = queue
        self.batch_size = batch_size
        self.timeout = timeout
        self.model = model

    def process_batch(self):
        batch_images = []
        wrappers = []
        start_time = time.time()

        while len(batch_images) < self.batch_size and (time.time() - start_time) < self.timeout:
            try:
                wrapper = self.queue.get(timeout=0.01)
                batch_images.append(wrapper.frame)
                wrappers.append(wrapper)
            except Exception:
                continue

        if not batch_images:
            return

        # Logging trigger metadata
        trigger_time = time.time() - start_time
        trigger_type = "full batch" if len(batch_images) == self.batch_size else "timeout"
        batch_size = len(batch_images)

        # 設定批次統一的 trigger 參數
        for wrapper in wrappers:
            wrapper.logger.update({
                "batch_size": batch_size,
                "trigger_type": trigger_type,
                "trigger_time": trigger_time
            })

        with RequestLogger.batch_phase(wrappers):
            results = self.model.predict(batch_images)

        for wrapper, result in zip(wrappers, results):
            wrapper.logger.complete()
            wrapper.result_queue.put(result)
