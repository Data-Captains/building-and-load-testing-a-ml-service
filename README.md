# Building and Load Testing a Machine Learning Service

## Purpose

To demonstrate how to create a Machine Learning (ML) service using
[Amazon SageMaker](https://aws.amazon.com/sagemaker/)
and
[AWS Chalice](https://aws.github.io/chalice/),
and how to load test it using
[`locust`](https://locust.io/).

To demonstrate how Amazon SageMaker autoscaling operates.

## Building it all from scratch

These are the steps that we followed.

- Create a Python virtual environment (we used Python 3.9.7).

- Install the requirements with `pip install -r requirements.txt`.

- Install the pre-commit hooks with `pre-commit install`.

- Ensure that you have the following installed:
  - `node` (we used version `v14.15.0`)
  - `tsc` (we used version `4.6.3`)
  - `cdk` (we used version `2.20.0`).

  For reference,
  [here](https://docs.aws.amazon.com/cdk/v2/guide/getting_started.html)
  is the setup guide for the AWS CDK.

- Create a new CDK app with
  `mkdir cdk-ml && cd cdk-ml && cdk init app --language typescript && cd ..`

  We used TypeScript to build the ML stack with AWS CDK, but one could use
  the Python version of AWS CDK here if preferred.

- Create the Docker image and the required artifacts to serve the ML model
  with SageMaker in `cdk-ml/lib/docker`.

- Also, create the ML model artifact by running the simple Jupyter notebook
  located at `jupyter/build-ml-model.ipynb`.

- Define the ML stack in `cdk-ml/lib/cdk-ml-stack.ts`.

- Create a new Chalice app with `chalice new-project chalice-api`.

- Define a REST API with a route (`/evaluate`) that calls the SageMaker
  model endpoint in `chalice-api/app.py`.

- Write the `locust/locustfile.py` file that controls the `locust` load test.
  Make sure to point `locust` to the base URL of the REST API.

- Deployment of the CDK ML stack and of the Chalice API app:

  - First, we deploy the CDK ML app with

    ```sh
    cd cdk-ml && cdk deploy && cd ..
    ```

  - Next, we deploy the Chalice API with

    ```sh
    cd chalice-api && chalice deploy && cd ..
    ```

- Perform your load testing (from the `locust` directory, execute `locust` and
  navigate to the `locust` UI in your browser).

- Clean up:

  - First, we destroy the Chalice API with

    ```sh
    cd chalice-api && chalice delete && cd ..
    ```

  - Finally, we destroy the CDK ML app with

    ```sh
    cd cdk-ml && cdk destroy && cd ..
    ```

## Distributed load tests with `locust`

There are some options out there to run `locust` in distributed fashion, for
instance:

- [`locust-swarm`](https://github.com/SvenskaSpel/locust-swarm)

- [`cdk-deployment-of-locust`](https://github.com/aws-samples/cdk-deployment-of-locust)
