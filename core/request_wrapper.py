import time
import queue

class RequestWrapper:
    def __init__(self, frame):
        self.frame = frame
        self.result_queue = queue.Queue()
        self.enqueue_time = time.time()
        self.logger = None  # 在外部由 PoseService 注入
