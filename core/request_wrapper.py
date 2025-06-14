import time
import queue

class RequestWrapper:
    def __init__(self, frame):
        self.frame = frame
        self.result_queue = queue.Queue()
        self.enqueue_time = time.time()
        self.receive_ts = time.strftime("%Y-%m-%d %H:%M:%S")
        self.logger = None  # 在外部由 PoseService 注入
        self.batch_id = None
