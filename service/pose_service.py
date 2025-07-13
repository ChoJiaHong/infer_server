import threading
from proto import pose_pb2_grpc
from proto import pose_pb2
from model.batch_worker import BatchWorker
from processor.batch_processor import BatchProcessor
from batch_config import BatchConfig, global_batch_config
from core.request_wrapper import RequestWrapper
from infra.request_queue import globalRequestQueue  # assume this exists
from utils.logger import get_logger
from processor.preprocessor import PosePreprocessor
from processor.postprocessor import PosePostprocessor
from .base_service import BaseService

class PoseDetectionService(BaseService, pose_pb2_grpc.MirrorServicer):
    def __init__(self, config: BatchConfig = global_batch_config):
        self.worker = BatchWorker()
        self.queue = globalRequestQueue
        self.processor = BatchProcessor(
            worker=self.worker,
            queue=self.queue,
            config=config
        )
        self.logger = get_logger(__name__)
        threading.Thread(target=self.processor.run_forever, daemon=True).start()
        super().__init__(PosePreprocessor(), PosePostprocessor())

    def predict(self, frame, logger, client_ip):
        wrapper = RequestWrapper(frame)
        wrapper.logger = logger
        logger.set("receive_ts", wrapper.receive_ts)
        self.queue.put(wrapper)
        self.logger.info(
            "Request %s enqueued from %s | size=%d",
            logger.request_id,
            client_ip,
            self.queue.qsize(),
        )
        try:
            result = wrapper.result_queue.get(timeout=2.0)
        except Exception as e:
            self.logger.error("Timeout waiting for result for %s: %s", logger.request_id, e)
            result = None
        return result

    def build_response(self, processed):
        return pose_pb2.FrameResponse(skeletons=processed)

    def SkeletonFrame(self, request, context):
        return self.handle_request(request.image_data, context)
