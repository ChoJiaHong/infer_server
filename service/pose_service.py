import threading
import pose_pb2_grpc
import pose_pb2
from model.batch_worker import BatchWorker
from processor.batch_processor import BatchProcessor
from batch_config import BatchConfig, global_batch_config
from infra.request_queue import globalRequestQueue  # shared request queue
from utils.logger import logger_context, get_logger
from utils.preprocessor import PosePreprocessor
from utils.postprocessor import PosePostprocessor
from metrics.registry import monitorRegistry

class PoseDetectionService(pose_pb2_grpc.MirrorServicer):
    def __init__(self, config: BatchConfig = global_batch_config):
        self.worker = BatchWorker()
        self.processor = BatchProcessor(
            worker=self.worker,
            queue=globalRequestQueue,
            config=config
        )
        self.preprocessor = PosePreprocessor()
        self.postprocessor = PosePostprocessor()
        self.logger = get_logger(__name__)
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

            result = self.processor.predict(frame, logger)

            with logger.phase("postprocess"):
                if result is not None:
                    processed = self.postprocessor.process(result)
                else:
                    processed = ""

            logger.write()

            completion = monitorRegistry.get("completion")
            if completion:
                completion.increment()

            return pose_pb2.FrameResponse(skeletons=processed)
