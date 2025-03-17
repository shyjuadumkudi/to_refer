from django.test import TestCase
from unittest.mock import patch, MagicMock

from my_other_app.utilities import get_passwd_from_cv


class MetadataUpdateTests(TestCase):
    def setUp(self) -> None:
        self.sample_integer_record = {
            "meta_data_definition_id": 1,
            "name": "Test Integer",
            "type": "INTEGER",
            "allowed_object_type": "object",
            "comment": "Test comment",
            "gui_default_value": "10",
            "value_syntax": "",
            "flags": "",
            "min": 1,
            "max": 100
        }

        self.sample_enum_record = {
            "meta_data_definition_id": 2,
            "name": "Test Enum",
            "type": "ENUM",
            "allowed_object_type": "object",
            "comment": "Test comment",
            "gui_default_value": "",
            "value_syntax": "",
            "flags": "",
            "list_values": [{"value": "Option1"}, {"value": "Option2"}]
        }

    @patch("your_module.requests.get")
    def test_fetch_metadata_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = [self.sample_integer_record]
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        data = fetch_metadata("https://fakeurl.com", {}, retries=1)
        self.assertEqual(data, [self.sample_integer_record])

    @patch("your_module.MetaDataDefinition.objects.update_or_create")
    def test_process_metadata_definition_integer(self, mock_update_or_create):
        mock_update_or_create.return_value = (MagicMock(name="MetaDataDefinition"), True)
        meta_def = process_metadata_definition(self.sample_integer_record)

        self.assertEqual(meta_def.name, "MetaDataDefinition")
        mock_update_or_create.assert_called_once()

    @patch("your_module.MetaDataValidValue.objects.update_or_create")
    @patch("your_module.MetaDataDefinition.objects.update_or_create")
    def test_process_valid_values_enum(self, mock_meta_update, mock_valid_value_update):
        meta_def_mock = MagicMock()
        mock_meta_update.return_value = (meta_def_mock, True)
        process_valid_values(meta_def_mock, self.sample_enum_record)

        self.assertEqual(mock_valid_value_update.call_count, 2)  # Two values in list_values

    @patch("your_module.fetch_metadata")
    @patch("your_module.process_metadata_definition")
    @patch("your_module.process_valid_values")
    def test_update_metadata_success(self, mock_process_valid_values, mock_process_metadata_definition, mock_fetch_metadata):
        mock_fetch_metadata.return_value = [self.sample_enum_record]
        mock_process_metadata_definition.return_value = MagicMock()

        result = update_metadata()
        self.assertEqual(result, "Success")
        mock_process_metadata_definition.assert_called_once()
        mock_process_valid_values.assert_called_once()
