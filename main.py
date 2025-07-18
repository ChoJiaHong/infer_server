import grpc
from concurrent import futures
import time

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

#--------------------------------

class HealthServicer(health_pb2_grpc.HealthServicer):
    def Check(self, request, context):
        return health_pb2.HealthCheckResponse(status=health_pb2.HealthCheckResponse.SERVING)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=100))
    health_pb2_grpc.add_HealthServicer_to_server(HealthServicer(), server)
    pose_pb2_grpc.add_MirrorServicer_to_server(
        PoseDetectionService(batch_size=settings.batch_size, timeout=settings.queue_timeout),
        server
    )
    server.add_insecure_port('[::]:' + settings.gRPC_port)
    server.start()
    print(f"[pose] gRPC server running on port {settings.gRPC_port}")
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == "__main__":
    #----------服務註冊位置-------------------
    # metrics/registry.py（繼續）
    """ monitorRegistry.register(name="rps",instance= RPSMonitor(interval=1.0))
    monitorRegistry.register("global_queue_size", QueueSizeMonitor(globalRequestQueue, sample_interval=0.005, report_interval=1.0)) """
    #monitorRegistry.start_all()
    #----------------------------------------
    serve()
