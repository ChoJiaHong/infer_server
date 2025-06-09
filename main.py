import grpc
from concurrent import futures
import time
from utils.logger import get_logger

from service.pose_service import PoseDetectionService
from grpc_health.v1 import health_pb2_grpc, health_pb2
import pose_pb2_grpc
from config import settings


#----------導入註冊服務----------------
from metrics import registry
from infra.request_queue import globalRequestQueue
from metrics.registry import monitorRegistry
from metrics.rps_monitor import RPSMonitor
from metrics.queue_monitor import QueueSizeMonitor
from metrics.system_monitor import SystemMetricsWriter

#--------------------------------

class HealthServicer(health_pb2_grpc.HealthServicer):
    def Check(self, request, context):
        return health_pb2.HealthCheckResponse(status=health_pb2.HealthCheckResponse.SERVING)

def serve():
    logger = get_logger(__name__)
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=100))
    health_pb2_grpc.add_HealthServicer_to_server(HealthServicer(), server)
    # create service instance so we can reference its processor in monitors
    pose_service = PoseDetectionService(
        batch_size=settings.batch_size,
        timeout=settings.queue_timeout,
    )
    pose_pb2_grpc.add_MirrorServicer_to_server(pose_service, server)

    # setup monitors
    rps_monitor = RPSMonitor(interval=1.0)
    queue_monitor = QueueSizeMonitor(
        globalRequestQueue,
        sample_interval=0.005,
        report_interval=1.0,
    )
    system_monitor = SystemMetricsWriter(
        queue=globalRequestQueue,
        rps_monitor=rps_monitor,
        batch_processor=pose_service.processor,
        interval=1.0,
    )

    monitorRegistry.register("rps", rps_monitor)
    monitorRegistry.register("queue_monitor", queue_monitor)
    monitorRegistry.register("system_monitor", system_monitor)
    monitorRegistry.start_all()
    server.add_insecure_port('[::]:' + settings.gRPC_port)
    server.start()
    logger.info("gRPC server running on port %s", settings.gRPC_port)
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        logger.info("Shutting down server")
        server.stop(0)

if __name__ == "__main__":
    serve()
