# Install Celery and Redis:
pip install celery redis

# Inside settings.py, configure Celery:
CELERY_BROKER_URL = "redis://localhost:6379/0"  # Ensure Redis is running
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"

# Inside your Django app, create a celery.py file:
from celery import Celery

app = Celery("myproject")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

# Run Celery Worker
# Start Celery worker in a separate terminal:
celery -A myproject worker --loglevel=info

# Schedule the Task Using Celery Beat (for Daily Execution)
# Install Celery Beat:
pip install django-celery-beat

# Add django_celery_beat to INSTALLED_APPS in settings.py:
INSTALLED_APPS = [
    "django_celery_beat",
    # other apps
]

# Run migrations:
python manage.py migrate django_celery_beat

# Start Celery Beat:
celery -A myproject beat --loglevel=info

# Start Celery Beat:
celery -A myproject beat --loglevel=info


Then, schedule the task from the Django admin panel:

Go to Admin Panel → Periodic Tasks
Create a New Periodic Task:
Name: Update MetaDataDefinitions
Task: myapp.tasks.update_metadata_definitions
Schedule: Every Day (or set your preferred schedule)
Enabled: ✅ Checked

# python manage.py shell
from myapp.tasks import update_metadata_definitions
update_metadata_definitions.delay()

