import json

import joblib
import numpy as np
from sagemaker_inference import content_types
from sagemaker_inference.default_inference_handler import DefaultInferenceHandler
from sagemaker_inference.errors import UnsupportedFormatError


class InferenceHandler(DefaultInferenceHandler):
    def default_model_fn(self, model_dir):
        # Hard code the model artifact that ships
        # with the Docker container.
        model_path = "/opt/ml/model/model.joblib"
        return joblib.load(model_path)

    def default_input_fn(self, input_data, content_type):
        # Accept JSON, e.g. {"distance": 150.3}.
        # For simplicity, allow only scoring one
        # JSON object at a time.
        if content_type == content_types.JSON:
            data = json.loads(input_data)["distance"]
            return np.log(data).reshape(1, -1)
        raise UnsupportedFormatError(content_type)

    def default_predict_fn(self, data, model):
        # Invoke the sklearn model predict method.
        return model.predict(data)

    def default_output_fn(self, prediction, accept):
        # Create JSON response, e.g. {"cost": 25.7}.
        if accept == content_types.JSON:
            response = {"cost": round(prediction[0], 2)}
            return json.dumps(response)
        raise UnsupportedFormatError(accept)
