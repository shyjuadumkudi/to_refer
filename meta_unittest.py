class FetchMetadataTestCase(unittest.TestCase):
    @patch("my_app.tasks.requests.get")  # Mock requests.get
    def test_fetch_metadata_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = [{"meta_data_definition_id": 1, "name": "Test"}]
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        result = fetch_metadata("https://api.example.com/metadatadef", {"Content-Type": "application/json"})
        self.assertIsNotNone(result)
        self.assertEqual(result[0]["name"], "Test")

    @patch("my_app.tasks.requests.get")
    def test_fetch_metadata_failure(self, mock_get):
        mock_get.side_effect = Exception("API Error")
        
        result = fetch_metadata("https://api.example.com/metadatadef", {"Content-Type": "application/json"})
        self.assertIsNone(result)


class ProcessMetadataDefinitionTestCase(unittest.TestCase):
    @patch("meta_data.models.MetaDataDefinition.objects.update_or_create")
    def test_process_metadata_definition_integer(self, mock_update_or_create):
        mock_update_or_create.return_value = (MagicMock(name="MetaDataDef"), True)

        record = {
            "meta_data_definition_id": 1,
            "name": "Test Integer",
            "type": "INTEGER",
            "min": 0,
            "max": 100
        }

        result = process_metadata_definition(record)
        self.assertEqual(result.name, "MetaDataDef")
        self.assertEqual(mock_update_or_create.call_count, 1)

    @patch("meta_data.models.MetaDataDefinition.objects.update_or_create")
    def test_process_metadata_definition_enum(self, mock_update_or_create):
        mock_update_or_create.return_value = (MagicMock(name="MetaDataDef"), False)

        record = {
            "meta_data_definition_id": 2,
            "name": "Test Enum",
            "type": "ENUM",
            "list_values": [{"value": "Option1"}, {"value": "Option2"}]
        }

        result = process_metadata_definition(record)
        self.assertEqual(result.name, "MetaDataDef")


class ProcessValidValuesTestCase(unittest.TestCase):
    @patch("meta_data.models.MetaDataValidValue.objects.update_or_create")
    def test_process_valid_values_enum(self, mock_update_or_create):
        meta_data_def_mock = MagicMock()
        record = {
            "type": "ENUM",
            "list_values": [{"value": "A"}, {"value": "B"}]
        }

        process_valid_values(meta_data_def_mock, record)
        self.assertEqual(mock_update_or_create.call_count, 2)  # Should be called twice for A and B


class UpdateMetadataTestCase(unittest.TestCase):
    @patch("my_app.tasks.fetch_metadata")
    @patch("my_app.tasks.process_metadata_definition")
    @patch("my_app.tasks.process_valid_values")
    def test_update_metadata_success(self, mock_process_values, mock_process_definition, mock_fetch_metadata):
        mock_fetch_metadata.return_value = [{"meta_data_definition_id": 1, "name": "Test", "type": "ENUM"}]
        mock_process_definition.return_value = MagicMock()

        result = update_metadata()

        self.assertEqual(result, "Success")
        self.assertTrue(mock_fetch_metadata.called)
        self.assertTrue(mock_process_definition.called)
