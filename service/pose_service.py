import threading
import queue
import time
import pose_pb2
import pose_pb2_grpc

from processor.batch_processor import RequestWrapper, BatchProcessor
from model.batch_worker import BatchWorker
from utils.preprocessor import PosePreprocessor
from utils.postprocessor import PosePostprocessor

class PoseDetectionService(pose_pb2_grpc.MirrorServicer):
    def __init__(self, batch_size, timeout):
        self.queue = queue.Queue()
        self.worker = BatchWorker()
        self.processor = BatchProcessor(self.worker, self.queue, batch_size, timeout)
        self.preprocessor = PosePreprocessor()
        self.postprocessor = PosePostprocessor()
        threading.Thread(target=self.processor.run_forever, daemon=True).start()

    def SkeletonFrame(self, request, context):
        frame = self.preprocessor.process(request.image_data)
        
        # 擷取 client IP
        peer = context.peer()  # e.g. ipv4:192.168.0.12:40000
        ip = peer.split(":")[1] if peer.startswith("ipv4") else "unknown"
        
        wrapper = RequestWrapper(frame)
        wrapper.logger.client_ip = ip
        self.queue.put(wrapper)

        try:
            raw_result = wrapper.result_queue.get(timeout=1.0)
            with wrapper.logger.phase("postprocess"):
                processed_result = self.postprocessor.process(raw_result)
        except queue.Empty:
            print("[Error] Result timeout.")
            processed_result = ""
        wrapper.logger.print_summary()
        #wrapper.logger.export_csv()
        return pose_pb2.FrameResponse(skeletons=processed_result)
