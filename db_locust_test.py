import os
import django
import time
from datetime import datetime
from locust import TaskSet, task, between, User
from locust import events
from faker import Faker
from django.utils import timezone
from dotenv import load_dotenv

# Load environment variables and Django settings
load_dotenv()
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_app.settings')
django.setup()

from new_app.models import MyModel  # Replace with your actual model

faker = Faker()

class DBTaskSet(TaskSet):

    @task(2)
    def read_my_model(self):
        start_time = time.time()
        try:
            logs = MyModel.objects.order_by('-date_done')[:100]
            _ = [log.request_id for log in logs]
            total_time = (time.time() - start_time) * 1000
            self.environment.events.request_success.fire(
                request_type="django-db",
                name="read_my_model",
                response_time=total_time,
                response_length=len(logs)
            )
        except Exception as e:
            total_time = (time.time() - start_time) * 1000
            self.environment.events.request_failure.fire(
                request_type="django-db",
                name="read_my_model",
                response_time=total_time,
                exception=e
            )

    @task(2)
    def write_my_model(self):
        start_time = time.time()
        try:
            MyModel.objects.create(
                request_id=faker.uuid4(),
                date_done=timezone.now()
            )
            total_time = (time.time() - start_time) * 1000
            self.environment.events.request_success.fire(
                request_type="django-db",
                name="write_my_model",
                response_time=total_time,
                response_length=1
            )
        except Exception as e:
            total_time = (time.time() - start_time) * 1000
            self.environment.events.request_failure.fire(
                request_type="django-db",
                name="write_my_model",
                response_time=total_time,
                exception=e
            )

    @task(1)
    def update_my_model(self):
        start_time = time.time()
        try:
            obj = MyModel.objects.order_by('?').first()
            if obj:
                obj.date_done = timezone.now()
                obj.save()
            total_time = (time.time() - start_time) * 1000
            self.environment.events.request_success.fire(
                request_type="django-db",
                name="update_my_model",
                response_time=total_time,
                response_length=1
            )
        except Exception as e:
            total_time = (time.time() - start_time) * 1000
            self.environment.events.request_failure.fire(
                request_type="django-db",
                name="update_my_model",
                response_time=total_time,
                exception=e
            )

class DBUser(User):
    tasks = [DBTaskSet]
    wait_time = between(1, 3)  # simulate user think-time
