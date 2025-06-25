import os
import csv
import json
import yaml
<<<<<<< HEAD
import os
import csv
=======

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
>>>>>>> refs/remotes/origin/main

# Using example:
# file_path = "Ensemble-members.json"
# print("Numero massimo di modelli:", max_model_count_from_file(file_path))

def suitable_for_models (repo_path):
    db_path = repo_path + '.github/data-storage/changes_db.json'
    metadata_folder =  repo_path + 'model-metadata/'

    changes = load_changes_db(db_path)
    return True if count_submitted_models(changes, metadata_folder) >= 3 else False


def suitable_for_ensemble (repo_path):

    filename = f"{get_latest_origin_dates(repo_path)}-respicast-hubEnsemble-ensemble_models.json"

    file_path = os.path.join(repo_path, f".github/logs/{filename}")
    return True if max_model_count_from_file(file_path) >= 3 else False



def max_model_count_from_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return 0

    max_models = 0

    
    for target in data:
        for country in target.get("countries", []):
            for member in country.get("members", []):
                models = member.get("models", [])
                max_models = max(max_models, len(models))

    return max_models


def get_latest_origin_dates(repo_path):
    """ 
    Estrae gli origin_date dei record in cui is_latest è True dal file CSV specificato. 
    """ 
    filepath = os.path.join(repo_path, 'supporting-files/forecasting_weeks.csv')
    origin_dates = set() 

    with open(filepath, newline='', encoding='utf-8') as csvfile: 
        reader = csv.DictReader(csvfile) 
        for row in reader: 
            if row.get("is_latest", "").strip().lower() == "true": 
                origin_dates.add(row.get("origin_date")) 

    return list(origin_dates)[0] 


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
                    print (f"Model name: {model_name} is primary or secondary")
                    submitted_models_count += 1
                else:
                    print (f"Model name: {model_name} is not primary or secondary")
            except FileNotFoundError as e:
                print(f"[AVVISO] {e}")
                continue  # Se manca il file, prosegue con gli altri

    return submitted_models_count


if __name__ == "__main__":
    print ('RespiCastUtils')

