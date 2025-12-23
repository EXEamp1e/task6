from locust import HttpUser, task, between


class FlaskAppUser(HttpUser):
    wait_time = between(1, 3)  # Пауза 1-3 сек между запросами

    @task(4)  # Чтение счетчика - 40% нагрузки
    def get_counter(self):
        self.client.get("/api/counter")

    @task(2)  # Увеличение - 20%
    def increment_counter(self):
        self.client.post("/api/counter/increment")

    @task(2)  # Уменьшение - 20%
    def decrement_counter(self):
        self.client.post("/api/counter/decrement")

    @task(1)  # Сброс - 10%
    def reset_counter(self):
        self.client.post("/api/counter/reset")

    @task(1)  # Главная страница - 10%
    def root(self):
        self.client.get("/")
