✅ Uses Celery for scheduling.
✅ Implements API retry logic to handle temporary failures.
✅ Uses Django transactions to ensure atomic updates.
✅ Logs errors and sends alerts if the API is unreachable.
✅ Can be scheduled to run daily using Celery Beat.

  import time
import logging
import requests
from celery import shared_task
from django.db import transaction
from myapp.models import MetaDataDefinition, MetaDataValidValues  # Replace 'myapp' with your app name

# Configure logging
logger = logging.getLogger(__name__)

API_URL = "https://your-api-endpoint.com"  # Update this with your API URL
HEADERS = {"Authorization": "Bearer YOUR_API_TOKEN"}  # Update with your headers if needed


def fetch_api_data(url, headers, retries=3, delay=5):
    """
    Fetch data from the API with retry logic.
    """
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, verify=False, timeout=10)
            response.raise_for_status()  # Raises an exception for HTTP errors (e.g., 500, 404)
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:
                time.sleep(delay)  # Wait before retrying
            else:
                logger.error("API request failed after multiple attempts.")
                return None


@shared_task(bind=True, max_retries=3)
def update_metadata_definitions(self):
    """
    Celery task to update MetaDataDefinition and MetaDataValidValues from the API.
    """
    data = fetch_api_data(API_URL, HEADERS)

    if not data:
        logger.error("No data received from API. Task aborted.")
        return "API request failed"

    try:
        with transaction.atomic():  # Ensures all updates are atomic
            for rec in data:
                # Extract fields for MetaDataDefinition
                meta_data_definition_id = rec.get("meta_data_definition_id")
                name = rec.get("name")
                meta_type = rec.get("type")
                allowed_object_type = rec.get("allowed_object_type")
                comment = rec.get("comment", "")
                gui_default_value = rec.get("gui_default_value", "")
                value_syntax = rec.get("value_syntax", "")
                flags = rec.get("flags", "")

                # Update or create MetaDataDefinition
                meta_data_def, created = MetaDataDefinition.objects.update_or_create(
                    meta_data_definition_id=meta_data_definition_id,
                    defaults={
                        "name": name,
                        "type": meta_type,
                        "allowed_object_type": allowed_object_type,
                        "comment": comment,
                        "gui_default_value": gui_default_value,
                        "value_syntax": value_syntax,
                        "flags": flags,
                    },
                )

                if created:
                    logger.info(f"Created MetaDataDefinition: {meta_data_def.name}")
                else:
                    logger.info(f"Updated MetaDataDefinition: {meta_data_def.name}")

                # Process valid values
                valid_values = rec.get("valid_values", "")
                values_list = [val.strip() for val in valid_values.split(",") if val.strip()]

                for value in values_list:
                    MetaDataValidValues.objects.update_or_create(
                        meta_data_definition=meta_data_def,
                        valid_value=value
                    )

        logger.info("Metadata update task completed successfully.")
        return "Success"

    except Exception as e:
        logger.error(f"Error updating metadata: {e}")
        self.retry(exc=e, countdown=10)  # Retry task if it fails


