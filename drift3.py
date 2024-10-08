import json

def compare_json(baseline, current, path=""):
    differences = []

    for key in baseline:
        if key not in current:
            differences.append(f"Missing key '{key}' in current config at path: {path}")
        else:
            if isinstance(baseline[key], dict) and isinstance(current[key], dict):
                # Recursively compare nested dictionaries
                differences += compare_json(baseline[key], current[key], path + f".{key}")
            elif baseline[key] != current[key]:
                differences.append(f"Value mismatch for key '{key}' at path: {path} - Baseline: {baseline[key]}, Current: {current[key]}")

    for key in current:
        if key not in baseline:
            differences.append(f"Extra key '{key}' in current config at path: {path}")

    return differences

def load_json(filename):
    with open(filename, "r") as f:
        return json.load(f)

if __name__ == "__main__":
    baseline_file = "baseline_config.json"  # Path to the baseline JSON
    current_file = "current_config.json"    # Path to the current JSON

    # Load JSON files
    baseline_config = load_json(baseline_file)
    current_config = load_json(current_file)

    # Compare JSON files
    drift = compare_json(baseline_config, current_config)

    if drift:
        print("Drift found:")
        for diff in drift:
            print(diff)
    else:
        print("No drift found, configurations match.")
