import json

def max_model_count_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    max_models = 0

    for target in data:
        for country in target.get("countries", []):
            for member in country.get("members", []):
                models = member.get("models", [])
                max_models = max(max_models, len(models))

    return max_models


