from ultralytics import YOLO
from config import settings
from utils.timing import timing_decorator

class BatchWorker:
    def __init__(self):
        self.model = YOLO(settings.weights)

    @timing_decorator("Batch Prediction")
    def predict(self, batch_images):
        return self.model(batch_images, device=settings.device,
                          conf=settings.conf_thres, iou=settings.iou_thres)
