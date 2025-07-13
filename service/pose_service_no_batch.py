from proto import pose_pb2_grpc
from proto import pose_pb2
from model.batch_worker import BatchWorker
from processor.single_processor import SingleFrameProcessor
from utils.logger import get_logger
from processor.preprocessor import PosePreprocessor
from processor.postprocessor import PosePostprocessor
from infra.request_queue import globalRequestQueue  # assume this exists
from .base_service import BaseService
class PoseDetectionServiceNoBatch(BaseService, pose_pb2_grpc.MirrorServicer):
    """gRPC service that processes each request without batching."""

    def __init__(self):
        self.worker = BatchWorker()
        self.processor = SingleFrameProcessor(self.worker)
        self.logger = get_logger(__name__)
        self.queue = globalRequestQueue
        super().__init__(PosePreprocessor(), PosePostprocessor())

    def predict(self, frame, logger, client_ip):
        logger.update({
            "batch_size": 1,
            "trigger_type": "single",
            "trigger_time_ms": 0,
        })
        self.queue.put(1)
        try:
            return self.processor.predict(frame)
        finally:
            if not self.queue.empty():
                self.queue.get_nowait()

    def build_response(self, processed):
        return pose_pb2.FrameResponse(skeletons=processed)

    def SkeletonFrame(self, request, context):
        return self.handle_request(request.image_data, context)

