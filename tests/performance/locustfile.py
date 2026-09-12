"""
Load test executed in the pipeline's `performance-test` stage before a
production release, e.g.:

    locust -f tests/performance/locustfile.py --headless \
           -u 50 -r 5 -t 1m --host $API_BASE_URL \
           --csv=perf-report --exit-code-on-error 1
"""
from locust import HttpUser, task, between


class ApiUser(HttpUser):
    wait_time = between(0.5, 2.0)

    @task(3)
    def health(self):
        self.client.get("/health")

    @task(1)
    def list_items(self):
        self.client.get("/items")

    @task(1)
    def create_item(self):
        self.client.post("/items", params={"name": "load-test-item"})
