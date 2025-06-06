import time
import queue
from utils.request_logger import RequestLogger

class RequestWrapper:
    def __init__(self, frame):
        
        self.frame = frame
        self.result_queue = queue.Queue()
        self.enqueue_time = time.time()
        self.logger = RequestLogger()
        self.logger.mark("enqueue")  # 起點標記

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
            trigger_time = time.time() - start_time
            trigger_type = "full batch" if len(batch_images) == self.batch_size else "timeout"
            for wrapper in wrappers:
                with wrapper.logger.phase("wait"):
                    pass  # wait phase = enqueue 到 infer_start
            infer_start = time.time()
            
            batch_size = len(wrappers)
            
            with wrappers[0].logger.phase("inference"):
                results = self.worker.predict(batch_images)
            infer_end = time.time()
            #計算第一個請求的等待時間
            #-------------------------------
            for wrapper, result in zip(wrappers, results):
                wait_time = infer_start - wrapper.enqueue_time
                wrapper.logger.batch_size = batch_size 
                print(f"[Wait] {wait_time*1000:.2f} ms")
                wrapper.logger.trigger_type = trigger_type
                wrapper.logger.trigger_time = trigger_time
                wrapper.logger.trigger_time = trigger_time
                wrapper.result_queue.put(result)

            print(f"[Batch] Inference: {(infer_end - infer_start)*1000:.2f} ms, "
                  f"Total Cycle: {(time.time() - start_time)*1000:.2f} ms")
