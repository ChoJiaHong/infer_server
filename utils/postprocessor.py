import json
import numpy as np
from utils.timing import timing_decorator

class Postprocessor:
    def process(self, result): raise NotImplementedError

class PosePostprocessor(Postprocessor):
    @timing_decorator("Postprocess")
    def process(self, result):
        skeletons = []
        for i, det in enumerate(result):
            landmarks = self._yolo_result2landmarks(det.keypoints)
            skeletons.append({"id": i, "keypoints": landmarks})
        return json.dumps(skeletons)

    def _yolo_result2landmarks(self, kpts):
        kpts_xy = kpts[0].xy.cpu().numpy()
        kpts_conf = kpts[0].conf.cpu().numpy()
        num_kpts = kpts_xy.shape[1]
        return [
            (int(kpts_xy[0][kid][0]), int(kpts_xy[0][kid][1]),
             round(float(kpts_conf[0][kid]), 3))
            for kid in range(num_kpts) if kpts_conf[0][kid] >= 0.5
        ]
