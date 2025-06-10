import json
from utils.timing import timing_decorator
from utils.landmarks import yolo_result2landmarks

class Postprocessor:
    def process(self, result): raise NotImplementedError

class PosePostprocessor(Postprocessor):
    @timing_decorator("Postprocess")
    def process(self, result):
        skeletons = []
        for i, det in enumerate(result):
            landmarks = yolo_result2landmarks(det.keypoints)
            skeletons.append({"id": i, "keypoints": landmarks})
        return json.dumps(skeletons)
