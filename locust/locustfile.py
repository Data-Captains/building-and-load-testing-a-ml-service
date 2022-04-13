import random

from locust import FastHttpUser, constant_pacing, task

# baseUrl must match the URL of the REST API of the chalice-api stack.
options = {
    "apiUrl": "ADD YOUR API GATEWAY REST API URL HERE",
}


class MyLocust(FastHttpUser):
    host = options["apiUrl"]
    wait_time = constant_pacing(1)

    @task
    def evaluate(self):
        self.client.post(
            "/evaluate",
            json={"distance": 1.0 + random.random() * 6499.0},
            verify=False,
        )
