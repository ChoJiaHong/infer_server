from gesture_server.vision.ssd.mobilenetv1_ssd import (
    create_mobilenetv1_ssd, create_mobilenetv1_ssd_predictor,
)
from gesture_server.vision.utils.misc import Timer
from config import settings


class GestureWorker:
    """Load the SSD gesture model and run inference."""

    def __init__(self):
        label_path = getattr(settings, "gesture_label_path", "gesture_server/voc-model-labels.txt")
        self.class_names = [name.strip() for name in open(label_path).readlines()]
        model_path = getattr(settings, "gesture_weights", "gesture_server/mb1-ssd-best.pth")
        self.net = create_mobilenetv1_ssd(len(self.class_names), is_test=True)
        self.net.load(model_path)
        self.predictor = create_mobilenetv1_ssd_predictor(self.net, candidate_size=200)
        self.timer = Timer()

    def predict(self, image):
        """Run inference on a single RGB image."""
        self.timer.start()
        boxes, labels, probs = self.predictor.predict(image, 10, 0.8)
        self.timer.end()
        return boxes, labels, probs
