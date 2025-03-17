from django.test import TestCase
from unittest.mock import patch, MagicMock


class MetaDataTests(TestCase):
    def setUp(self) -> None:
        self.sample_integer_metadata = {
            "name": "Test Integer",
            "type": "INTEGER",
            "min": 1,
            "max": 100,
            "comment": "Test comment",
        }

        self.sample_enum_metadata = {
            "name": "Test Enum",
            "type": "ENUM",
            "list_values": [{"value": "Option1"}, {"value": "Option2"}],
            "comment": "Test ENUM comment",
        }
    
    @patch("meta_data.tasks.requests.get")
    @patch("meta_data.tasks.get_auth_credentials", return_value=("user", "pass"))
    def test_fetch_metadata_success(self, mock_auth, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = [self.sample_integer_metadata]
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        data = fetch_metadata("fake_url", {})
        self.assertEqual(data, [self.sample_integer_metadata])

    @patch("meta_data.tasks.requests.get")
    @patch("meta_data.tasks.get_auth_credentials", return_value=("user", "pass"))
    def test_fetch_metadata_failure(self, mock_auth, mock_get):
        mock_get.side_effect = Exception("Request failed")
        data = fetch_metadata("fake_url", {})
        self.assertIsNone(data)
    
    def test_process_metadata_definition_integer(self):
        meta_data_def = process_metadata_definition(self.sample_integer_metadata)
        self.assertEqual(meta_data_def.name, "Test Integer")
        self.assertEqual(meta_data_def.value_syntax, '{ "min": 1, "max": 100 }')
    
    def test_process_metadata_definition_enum(self):
        meta_data_def = process_metadata_definition(self.sample_enum_metadata)
        self.assertEqual(meta_data_def.name, "Test Enum")
        self.assertEqual(meta_data_def.value_syntax, "")
    
    def test_process_valid_values(self):
        meta_data_def = process_metadata_definition(self.sample_enum_metadata)
        process_valid_values(meta_data_def, self.sample_enum_metadata)
        
        values = MetaDataValidValue.objects.filter(meta_data_definition=meta_data_def)
        self.assertEqual(values.count(), 2)
        self.assertTrue(values.filter(valid_value="Option1").exists())
        self.assertTrue(values.filter(valid_value="Option2").exists())
    
    @patch("meta_data.tasks.fetch_metadata")
    @patch("meta_data.tasks.process_metadata_definition")
    @patch("meta_data.tasks.process_valid_values")
    def test_update_metadata(self, mock_process_valid_values, mock_process_metadata_def, mock_fetch_metadata):
        mock_fetch_metadata.return_value = [self.sample_integer_metadata, self.sample_enum_metadata]
        mock_meta_def = MagicMock()
        mock_process_metadata_def.side_effect = [mock_meta_def, mock_meta_def]
        
        result = update_metadata()
        self.assertEqual(result, "Success")
        mock_process_metadata_def.assert_called()
        mock_process_valid_values.assert_called_once_with(mock_meta_def, self.sample_enum_metadata)
