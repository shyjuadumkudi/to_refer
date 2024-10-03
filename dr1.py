import json

def compare_configs(baseline, current):
    differing_keys = {}
    missing_in_baseline = {}
    missing_in_current = {}

    # Compare all keys in both baseline and current configurations
    for key in baseline:
        if key in current:
            if baseline[key] != current[key]:
                differing_keys[key] = {
                    "baseline_value": baseline[key],
                    "current_value": current[key]
                }
        else:
            missing_in_current[key] = baseline[key]

    for key in current:
        if key not in baseline:
            missing_in_baseline[key] = current[key]

    return differing_keys, missing_in_baseline, missing_in_current

# Load baseline and current configurations from JSON files
def load_json_file(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

# Example usage
if __name__ == "__main__":
    baseline_file = 'baseline_config.json'
    current_file = 'current_config.json'

    # Load configurations
    baseline_config = load_json_file(baseline_file)
    current_config = load_json_file(current_file)

    # Compare configurations
    differing, missing_in_baseline, missing_in_current = compare_configs(baseline_config, current_config)

    # Print results
    print("Differing Keys:")
    print(json.dumps(differing, indent=4))

    print("\nMissing in Baseline:")
    print(json.dumps(missing_in_baseline, indent=4))

    print("\nMissing in Current:")
    print(json.dumps(missing_in_current, indent=4))