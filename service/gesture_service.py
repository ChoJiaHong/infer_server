from datetime import datetime
from proto import gesture_pb2_grpc
from proto import gesture_pb2
from model.gesture_worker import GestureWorker
from processor.single_processor import SingleFrameProcessor
from utils.logger import logger_context, get_logger
from utils.preprocessor import GesturePreprocessor
from utils.postprocessor import GesturePostprocessor
from metrics.registry import monitorRegistry
from infra.request_queue import globalRequestQueue


class GestureDetectionService(gesture_pb2_grpc.GestureRecognitionServicer):
    """gRPC service handling gesture recognition requests."""

    def __init__(self):
        self.worker = GestureWorker()
        self.preprocessor = GesturePreprocessor()
        self.postprocessor = GesturePostprocessor()
        self.processor = SingleFrameProcessor(self.worker)
        self.logger = get_logger(__name__)
        self.queue = globalRequestQueue
        self.frame_index = 0

    def Recognition(self, request, context):
        rps = monitorRegistry.get("rps")
        if rps:
            rps.increment()

        self.queue.put(1)
        client_ip = context.peer().split(":")[-1].replace("ipv4/", "")
        with logger_context() as logger:
            logger.set_mark("start")
            logger.set("client_ip", client_ip)
            logger.set("receive_ts", datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3])
            logger.update({
                "batch_size": 1,
                "trigger_type": "single",
                "trigger_time_ms": 0,
            })

            with logger.phase("preprocess"):
                frame = self.preprocessor.process(request.image)

            with logger.phase("inference"):
                result = self.processor.predict(frame)

            with logger.phase("postprocess"):
                action = self.postprocessor.process(result)

            logger.write()

            completion = monitorRegistry.get("completion")
            if completion:
                completion.increment()

            self.frame_index += 1
            response = gesture_pb2.RecognitionReply(
                frame_index=self.frame_index,
                timestamp=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                action=action,
            )

        if not self.queue.empty():
            self.queue.get_nowait()

        return response
