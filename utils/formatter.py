import numpy as np
import cv2
import json
from utils.timing import timing_decorator

@timing_decorator("Preprocess")
def preprocess_image(image_data):
    img_array = np.frombuffer(image_data, np.uint8)
    return cv2.imdecode(img_array, cv2.IMREAD_COLOR)

@timing_decorator("Postprocess")
def postprocess_result(result):
    skeletons = []
    for i, det in enumerate(result):
        landmarks = yolo_result2landmarks(det.keypoints)
        skeletons.append({"id": i, "keypoints": landmarks})
    return json.dumps(skeletons)

def yolo_result2landmarks(kpts):
    kpts_xy = kpts[0].xy.cpu().numpy()
    kpts_conf = kpts[0].conf.cpu().numpy()
    num_kpts = kpts_xy.shape[1]
    return [
        (int(kpts_xy[0][kid][0]), int(kpts_xy[0][kid][1]),
         round(float(kpts_conf[0][kid]), 3))
        for kid in range(num_kpts) if kpts_conf[0][kid] >= 0.5
    ]
