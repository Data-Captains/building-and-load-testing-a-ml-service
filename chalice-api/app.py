import json

import boto3
from chalice import Chalice, Response
from pydantic import BaseModel, PositiveFloat, ValidationError

options = {
    "chalice": {"appName": "chalice-api"},
    "sageMaker": {"endpointName": "real-estate-evaluation"},
}


app = Chalice(app_name=options["chalice"]["appName"])


@app.route("/")
def index():
    return {
        "message": "Hello! POST to /evaluate to get real estate pricing information!"
    }


client = boto3.client("sagemaker-runtime")


class Distance(BaseModel):
    distance: PositiveFloat


@app.route("/evaluate", methods=["POST"])
def evaluate():
    """Loosely follow the SageMaker error codes associated with these exceptions.

    https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_runtime_InvokeEndpoint.html
    """
    response_headers = {"Content-Type": "application/json"}

    def make_code_message_body(code, message):
        return {
            "Code": code,
            "Message": message,
        }

    try:
        distance = Distance(**app.current_request.json_body)
        response = client.invoke_endpoint(
            EndpointName=options["sageMaker"]["endpointName"],
            ContentType="application/json",
            Body=json.dumps(distance.dict()),
        )
        return Response(
            body=response["Body"].read(),
            headers=response_headers,
            status_code=200,
        )
    except ValidationError as exception:
        return Response(
            body=make_code_message_body(
                "ValidationError (pydantic)", exception.errors()
            ),
            headers=response_headers,
            status_code=400,
        )
    except client.exceptions.InternalFailure as exception:
        return Response(
            body=make_code_message_body(
                "InternalFailure (SageMakerRuntime)", exception.response
            ),
            headers=response_headers,
            status_code=500,
        )
    except client.exceptions.ServiceUnavailable as exception:
        return Response(
            body=make_code_message_body(
                "ServiceUnavailable (SageMakerRuntime)", exception.response
            ),
            headers=response_headers,
            status_code=500,
        )
    except client.exceptions.ValidationError as exception:
        return Response(
            body=make_code_message_body(
                "ValidationError (SageMakerRuntime)", exception.response
            ),
            headers=response_headers,
            status_code=400,
        )
    except client.exceptions.ModelError as exception:
        return Response(
            body=make_code_message_body(
                "ModelError (SageMakerRuntime)", exception.response
            ),
            headers=response_headers,
            status_code=424,
        )
    except client.exceptions.InternalDependencyException as exception:
        return Response(
            body=make_code_message_body(
                "InternalDependencyException (SageMakerRuntime)", exception.response
            ),
            headers=response_headers,
            status_code=530,
        )
    except client.exceptions.ModelNotReadyException as exception:
        return Response(
            body=make_code_message_body(
                "ModelNotReadyException (SageMakerRuntime)", exception.response
            ),
            headers=response_headers,
            status_code=429,
        )
    except client.exceptions.ClientError as exception:
        return Response(
            body=make_code_message_body(
                "ClientError (SageMakerRuntime)", exception.response
            ),
            headers=response_headers,
            status_code=400,
        )
    except Exception:
        return Response(
            body=make_code_message_body("UnknownError", "An unknown error occurred."),
            headers=response_headers,
            status_code=500,
        )
