import os
import django
from locust import TaskSet, task, between, User
from faker import Faker
from dotenv import load_dotenv
from django.utils import timezone

# Set up Django environment
load_dotenv()
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_app.settings')
django.setup()

from new_app.models import MyModel  # Replace with your actual model

faker = Faker()

class DBTaskSet(TaskSet):

    @task(2)
    def read_my_model(self):
        logs = MyModel.objects.order_by('-date_done')[:100]
        for log in logs:
            _ = log.request_id  # simulate access

    @task(2)
    def write_my_model(self):
        MyModel.objects.create(
            request_id=faker.uuid4(),
            date_done=timezone.now()
        )

    @task(1)
    def update_my_model(self):
        obj = MyModel.objects.order_by('?').first()
        if obj:
            obj.date_done = timezone.now()
            obj.save()

class DBUser(User):
    tasks = [DBTaskSet]
    wait_time = between(1, 3)
