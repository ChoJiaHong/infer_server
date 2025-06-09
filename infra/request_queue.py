import queue

# Global shared request queue
globalRequestQueue = queue.Queue()

def get_queue_size():
    return globalRequestQueue.qsize()