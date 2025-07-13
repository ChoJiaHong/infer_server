from datetime import datetime
from proto import gesture_pb2_grpc
from proto import gesture_pb2
from model.gesture_worker import GestureWorker
from processor.single_processor import SingleFrameProcessor
from utils.logger import get_logger
from processor.preprocessor import GesturePreprocessor
from processor.postprocessor import GesturePostprocessor
from infra.request_queue import globalRequestQueue
from .base_service import BaseService


class GestureDetectionService(BaseService, gesture_pb2_grpc.GestureRecognitionServicer):
    """gRPC service handling gesture recognition requests."""

    def __init__(self):
        self.worker = GestureWorker()
        self.processor = SingleFrameProcessor(self.worker)
        self.queue = globalRequestQueue
        self.frame_index = 0
        super().__init__(GesturePreprocessor(), GesturePostprocessor())

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
        self.frame_index += 1
        return gesture_pb2.RecognitionReply(
            frame_index=self.frame_index,
            timestamp=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            action=processed,
        )

    def Recognition(self, request, context):
        return self.handle_request(request.image, context)
