import numpy as np
import cv2
from utils.timing import timing_decorator

class Preprocessor:
    def process(self, image_data): raise NotImplementedError

class PosePreprocessor(Preprocessor):
    @timing_decorator("Preprocess")
    def process(self, image_data):
        img_array = np.frombuffer(image_data, np.uint8)
        return cv2.imdecode(img_array, cv2.IMREAD_COLOR)
