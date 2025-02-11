import requests
from django.conf import settings
from myapp.models import MetaDataDefinition, MetaDataValidValue

def fetch_ea_data_from_infoblox():
    url = f"{settings.INFOBLOX_BASE_URL}/wapi/v2.11/extattr"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Token {settings.INFOBLOX_API_TOKEN}"
    }
    
    response = requests.get(url, headers=headers, verify=False)
    
    if response.status_code == 200:
        ea_data = response.json()
        
        for ea_name, attributes in ea_data.items():
            meta_data, created = MetaDataDefinition.objects.update_or_create(
                name=ea_name,
                defaults={
                    "type": attributes.get("type", ""),
                    "allowed_object_type": attributes.get("allowed_object_types", ""),
                    "comment": attributes.get("comment", ""),
                    "gui_default_value": attributes.get("gui_default", ""),
                    "value_syntax": attributes.get("syntax", ""),
                    "flags": attributes.get("flags", ""),
                }
            )
            
            if "values" in attributes and isinstance(attributes["values"], list):
                for value in attributes["values"]:
                    MetaDataValidValue.objects.update_or_create(
                        meta_data_definition=meta_data,
                        valid_value=value
                    )
    else:
        print(f"Failed to fetch EA data: {response.status_code} - {response.text}")

if __name__ == "__main__":
    fetch_ea_data_from_infoblox()
