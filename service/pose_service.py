import threading
import pose_pb2_grpc
import pose_pb2
from model.batch_worker import BatchWorker
from processor.batch_processor import BatchProcessor
from core.request_wrapper import RequestWrapper
from infra.request_queue import globalRequestQueue  # assume this exists
from utils.logger import logger_context
from utils.preprocessor import PosePreprocessor
from utils.postprocessor import PosePostprocessor
from metrics.registry import monitorRegistry

class PoseDetectionService(pose_pb2_grpc.MirrorServicer):
    def __init__(self, batch_size, timeout):
        self.worker = BatchWorker()
        self.queue = globalRequestQueue
        self.processor = BatchProcessor(
            worker=self.worker,
            queue=self.queue,
            batch_size=batch_size,
            timeout=timeout
        )
        self.preprocessor = PosePreprocessor()
        self.postprocessor = PosePostprocessor()
        threading.Thread(target=self.processor.run_forever, daemon=True).start()

    def SkeletonFrame(self, request, context):
        
        rps = monitorRegistry.get("rps")
        if rps:
            rps.increment()
            
        client_ip = context.peer().split(":")[-1].replace("ipv4/", "")
        with logger_context() as logger:
            logger.set_mark("start")
            logger.set("client_ip", client_ip)

            with logger.phase("preprocess"):
                frame = self.preprocessor.process(request.image_data)

            wrapper = RequestWrapper(frame)
            wrapper.logger = logger  # 將 logger 傳入 wrapper
            self.queue.put(wrapper)

            try:
                result = wrapper.result_queue.get(timeout=2.0)
                with logger.phase("postprocess"):
                    processed = self.postprocessor.process(result)
            except Exception as e:
                print("[Error] Timeout waiting for result:", e)
                processed = ""

            #logger.write()
            return pose_pb2.FrameResponse(skeletons=processed)
