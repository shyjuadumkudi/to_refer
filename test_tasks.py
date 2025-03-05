import os
import time
import logging
import requests
from unittest.mock import patch, MagicMock
from django.test import TestCase
from requests.auth import HTTPBasicAuth
from meta_data.models import MetaDataDefinition, MetaDataValidValue
from my_other_app.utilities import get_passwd_from_cv
from myapp.tasks import fetch_metadata, update_metadata


class TestMetadataUpdate(TestCase):
    """
    Unit tests for fetch_metadata function and update_metadata Celery task.
    """

    @patch("myapp.tasks.requests.get")
    @patch("myapp.tasks.get_passwd_from_cv")
    def test_fetch_metadata_success(self, mock_get_passwd, mock_get):
        """
        Test fetch_metadata function with a successful API response.
        """
        os.environ["USERNAME"] = "test_user"
        os.environ["env"] = "dev"
        mock_get_passwd.return_value = "mocked_password"

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"meta_data_definition_id": 1, "name": "Test Metadata"}]
        mock_get.return_value = mock_response

        result = fetch_metadata("https://api.example.com", {})

        self.assertIsNotNone(result)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["meta_data_definition_id"], 1)
        mock_get.assert_called_once_with(
            "https://api.example.com",
            headers={},
            auth=HTTPBasicAuth("test_user", "mocked_password"),
            verify=False,
            timeout=10
        )

    @patch("myapp.tasks.requests.get")
    def test_fetch_metadata_failure(self, mock_get):
        """
        Test fetch_metadata function with a failed API request.
        """
        os.environ["USERNAME"] = "test_user"
        os.environ["env"] = "prod"
        os.environ["passwd"] = "secure_pass"

        mock_get.side_effect = requests.exceptions.RequestException("API failure")

        result = fetch_metadata("https://api.example.com", {})

        self.assertIsNone(result)
        self.assertEqual(mock_get.call_count, 3)  # Ensure it retries

    @patch("myapp.tasks.requests.get")
    def test_fetch_metadata_retries(self, mock_get):
        """
        Test that fetch_metadata retries on failure.
        """
        os.environ["USERNAME"] = "test_user"
        os.environ["passwd"] = "secure_pass"

        mock_get.side_effect = requests.exceptions.RequestException("Temporary API failure")

        result = fetch_metadata("https://api.example.com", {})

        self.assertIsNone(result)
        self.assertEqual(mock_get.call_count, 3)  # Ensure it retries up to 3 times

    @patch("myapp.tasks.fetch_metadata")
    @patch("myapp.tasks.MetaDataDefinition.objects.update_or_create")
    @patch("myapp.tasks.MetaDataValidValue.objects.update_or_create")
    def test_update_metadata_success(self, mock_valid_values_create, mock_meta_def_create, mock_fetch_metadata):
        """
        Test update_metadata task when metadata is successfully fetched and updated in the DB.
        """
        mock_fetch_metadata.return_value = [
            {
                "meta_data_definition_id": 1,
                "name": "Test Metadata",
                "type": "string",
                "allowed_object_type": "host",
                "comment": "Test comment",
                "gui_default_value": "default",
                "value_syntax": "regex",
                "flags": "required",
                "valid_values": "Value1, Value2",
            }
        ]

        mock_meta_def_create.return_value = (MagicMock(id=1, name="Test Metadata"), True)
        mock_valid_values_create.return_value = (MagicMock(valid_value="Value1"), True)

        result = update_metadata()

        self.assertEqual(result, "Success")
        mock_meta_def_create.assert_called_once_with(
            meta_data_definition_id=1,
            defaults={
                "name": "Test Metadata",
                "type": "string",
                "allowed_object_type": "host",
                "comment": "Test comment",
                "gui_default_value": "default",
                "value_syntax": "regex",
                "flags": "required",
            },
        )
        mock_valid_values_create.assert_any_call(meta_data_definition=mock_meta_def_create.return_value[0], valid_value="Value1")
        mock_valid_values_create.assert_any_call(meta_data_definition=mock_meta_def_create.return_value[0], valid_value="Value2")

    @patch("myapp.tasks.fetch_metadata")
    def test_update_metadata_api_failure(self, mock_fetch_metadata):
        """
        Test update_metadata task when the API fails.
        """
        mock_fetch_metadata.return_value = None

        result = update_metadata()

        self.assertEqual(result, "Failed")

    @patch("myapp.tasks.fetch_metadata")
    @patch("myapp.tasks.MetaDataDefinition.objects.update_or_create")
    def test_update_metadata_exception_handling(self, mock_meta_def_create, mock_fetch_metadata):
        """
        Test update_metadata task when an exception occurs.
        """
        mock_fetch_metadata.return_value = [
            {
                "meta_data_definition_id": 1,
                "name": "Test Metadata",
                "valid_values": "Value1, Value2",
            }
        ]

        mock_meta_def_create.side_effect = Exception("DB Error")

        with patch.object(update_metadata, "retry") as mock_retry:
            result = update_metadata()

            self.assertEqual(result, None)
            mock_retry.assert_called_once()
