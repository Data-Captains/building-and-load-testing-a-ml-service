FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

# Install necessary dependencies and requirements.
RUN apt-get update && \
    apt-get -y install --no-install-recommends \
    build-essential \
    ca-certificates \
    curl \
    openjdk-8-jdk-headless \
    python3-distutils \
    software-properties-common
RUN apt-get -y install python3.9
RUN curl -O https://bootstrap.pypa.io/get-pip.py
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.9 1
RUN python3.9 get-pip.py

COPY requirements.txt /usr/local/tmp/requirements.txt
RUN pip install -r /usr/local/tmp/requirements.txt

# Copy the model artifact (make it happy by creating the special directory
# /opt/ml/model which is a special directory for model artifacts in SageMaker
# containers).
RUN mkdir -p /opt/ml/model
COPY model.joblib /opt/ml/model/model.joblib

# Copy the Python files and declare the entrypoint for the image.
COPY handler_service.py /usr/local/lib/handler_service.py
COPY inference_handler.py /usr/local/lib/inference_handler.py
COPY entrypoint.py /usr/local/bin/entrypoint.py
ENTRYPOINT ["python", "/usr/local/bin/entrypoint.py"]

CMD ["serve"]