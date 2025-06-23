import os
import csv
import json
import yaml

def get_latest_origin_dates(filepath):
    """
    Estrae gli origin_date dei record in cui is_latest è True dal file CSV specificato.
    """
    origin_dates = set()

    with open(filepath, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row.get("is_latest", "").strip().lower() == "true":
                origin_dates.add(row.get("origin_date"))

    return list(origin_dates)

# Esempio d'uso
file_path = "forecasting_weeks.csv"
latest_dates = get_latest_origin_dates(file_path)
print("Origin date(s) con is_latest = true:", latest_dates)

# -------

# Using example:
# file_path = "Ensemble-members.json"
# print("Numero massimo di modelli:", max_model_count_from_file(file_path))

def suitable_for_ensemble ():
    return true if max_model_count () >= 3 : false

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



# Using example
# if __name__ == "__main__":
#     db_path = ".github/data-storage/changes_db.json"
#     metadata_dir = "model-metadata"

#     changes = load_changes_db(db_path)
#     count = count_submitted_models(changes, metadata_dir)
#     print(f"Numero di modelli 'primary' o 'secondary' sottomessi: {count}")

def load_changes_db(filepath):
    """
    Carica il file JSON contenente le informazioni sui cambiamenti dei modelli.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_team_model_metadata(team, model, metadata_folder):
    """
    Legge il file YAML corrispondente a <team>-<model>.yml e restituisce il valore del campo
    'team_model_designation'.
    """
    filename = f"{team}-{model}.yml"
    filepath = os.path.join(metadata_folder, filename)

    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"File di metadata non trovato: {filepath}")

    with open(filepath, 'r', encoding='utf-8') as f:
        metadata = yaml.safe_load(f)

    return metadata.get("team_model_designation", "").lower()

def count_submitted_models(changes_db, metadata_folder):
    """
    Conta quanti modelli hanno un 'team_model_designation' pari a 'primary' o 'secondary'.
    """
    submitted_models_count = 0

    for team, models in changes_db.items():
        for model_entry in models:
            model_name = model_entry.get("model")
            if not model_name:
                continue  # Skippa se manca il nome del modello

            try:
                designation = get_team_model_metadata(team, model_name, metadata_folder)
                if designation in {"primary", "secondary"}:
                    submitted_models_count += 1
            except FileNotFoundError as e:
                print(f"[AVVISO] {e}")
                continue  # Se manca il file, prosegue con gli altri

    return submitted_models_count
