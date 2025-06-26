import time
import pose_pb2_grpc
import pose_pb2
from model.batch_worker import BatchWorker
from utils.logger import logger_context, get_logger
from utils.preprocessor import PosePreprocessor
from utils.postprocessor import PosePostprocessor
from metrics.registry import monitorRegistry

class PoseDetectionServiceNoBatch(pose_pb2_grpc.MirrorServicer):
    """gRPC service that processes each request without batching."""

    def __init__(self):
        self.worker = BatchWorker()
        self.preprocessor = PosePreprocessor()
        self.postprocessor = PosePostprocessor()
        self.logger = get_logger(__name__)

    def SkeletonFrame(self, request, context):
        rps = monitorRegistry.get("rps")
        if rps:
            rps.increment()

        client_ip = context.peer().split(":")[-1].replace("ipv4/", "")
        with logger_context() as logger:
            logger.set_mark("start")
            logger.set("client_ip", client_ip)
            logger.set("receive_ts", time.strftime("%Y-%m-%d %H:%M:%S"))
            logger.update({
                "batch_size": 1,
                "trigger_type": "single",
                "trigger_time_ms": 0,
            })

            with logger.phase("preprocess"):
                frame = self.preprocessor.process(request.image_data)

            with logger.phase("inference"):
                result = self.worker.predict([frame])[0]

            with logger.phase("postprocess"):
                processed = self.postprocessor.process(result)

            logger.write()

            completion = monitorRegistry.get("completion")
            if completion:
                completion.increment()

            return pose_pb2.FrameResponse(skeletons=processed)
