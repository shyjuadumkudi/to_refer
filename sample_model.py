from django.db import models

class MetaDataDefinition(models.Model):
    meta_data_definition_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=255)
    allowed_object_type = models.TextField()
    comment = models.TextField(blank=True, null=True)
    gui_default_value = models.TextField(blank=True, null=True)
    value_syntax = models.CharField(max_length=255, blank=True, null=True)
    flags = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name

class MetaDataValidValue(models.Model):
    meta_data_valid_value_id = models.BigAutoField(primary_key=True)
    meta_data_definition = models.ForeignKey(MetaDataDefinition, on_delete=models.CASCADE, related_name='valid_values')
    valid_value = models.TextField()

    def __str__(self):
        return f"{self.meta_data_definition.name}: {self.valid_value}"
