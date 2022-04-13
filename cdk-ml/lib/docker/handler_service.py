from inference_handler import InferenceHandler
from sagemaker_inference.default_handler_service import DefaultHandlerService
from sagemaker_inference.transformer import Transformer


class HandlerService(DefaultHandlerService):
    def __init__(self):
        transformer = Transformer(default_inference_handler=InferenceHandler())
        super().__init__(transformer=transformer)


service = HandlerService()


def handle(data, context):
    if data is None:
        return None
    return service.handle(data, context)
