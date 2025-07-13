import abc
from metrics.registry import monitorRegistry
from utils.logger import logger_context, get_logger


class BaseService(abc.ABC):
    """Abstract service providing common request handling."""

    def __init__(self, preprocessor, postprocessor):
        self.preprocessor = preprocessor
        self.postprocessor = postprocessor
        self.logger = get_logger(self.__class__.__name__)

    @abc.abstractmethod
    def predict(self, frame, logger, client_ip):
        """Run inference and return raw results."""
        raise NotImplementedError

    @abc.abstractmethod
    def build_response(self, processed):
        """Create gRPC response from processed result."""
        raise NotImplementedError

    def handle_request(self, image_data, context):
        rps = monitorRegistry.get("rps")
        if rps:
            rps.increment()

        client_ip = context.peer().split(":")[-1].replace("ipv4/", "")
        with logger_context() as logger:
            logger.set_mark("start")
            logger.set("client_ip", client_ip)

            with logger.phase("preprocess"):
                frame = self.preprocessor.process(image_data)

            result = self.predict(frame, logger, client_ip)

            if result is not None:
                with logger.phase("postprocess"):
                    processed = self.postprocessor.process(result)
            else:
                processed = ""

            logger.write()

            completion = monitorRegistry.get("completion")
            if completion:
                completion.increment()

            return self.build_response(processed)
