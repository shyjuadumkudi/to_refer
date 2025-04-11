from django.test import TestCase
from meta_data.models import MetaDataDefinition, MetaDataValidValues
from meta_data.metadata_utils import insert_hardcoded_countries

class InsertHardcodedCountriesTest(TestCase):

    def test_country_metadata_created(self):
        insert_hardcoded_countries()

        # Check that the MetaDataDefinition with name "country" is created
        self.assertTrue(MetaDataDefinition.objects.filter(name="country").exists())

        meta_def = MetaDataDefinition.objects.get(name="country")
        self.assertEqual(meta_def.type, "String")
        self.assertEqual(meta_def.allowed_object_type, "global")
        self.assertEqual(meta_def.comment, "Country code metadata")

    def test_country_codes_inserted(self):
        insert_hardcoded_countries()

        meta_def = MetaDataDefinition.objects.get(name="country")
        valid_values = MetaDataValidValues.objects.filter(meta_data_definition=meta_def)

        # Check that a reasonable number of country codes were inserted
        self.assertGreaterEqual(valid_values.count(), 200)

        # Check a few specific country codes
        expected_codes = ["IN", "US", "DE", "FR", "BR"]
        inserted_codes = list(valid_values.values_list("valid_value", flat=True))

        for code in expected_codes:
            self.assertIn(code, inserted_codes)
