import os
import json


def storeMultiTargetData(target_data):
    
    out_data = {}

    for target in target_data:
        
        target_name = os.path.splitext(os.path.basename(target))[0].split('-')[-1].replace("_", " ")

        print (f'OutputData Before: {out_data}')

        # Look for target in out_data
        if target_name in out_data:  

            # if already present, just add changes                      

            print(f'Target {target_name} already in the list. Add data')

            out_data[target_name]["changes"] = list(set(out_data[target_name]["changes"] + target))
        
        else:        
            # if not in the list, just add changes                      
            print(f'New target {target_name}. Adding data')        
            out_data[target_name] = { "changes" : [target] }

    if out_data:
        db_path = os.path.join(os.getcwd(), "./repo/.github/data-storage/target_db.json")
        print(f"DB path: {db_path}")
        print (f'Out-data: {out_data}')
        updateMultiTargetJson(db_path, out_data)
 


def updateMultiTargetJson (json_file_path, out_data):

    json_data = None

    # Step 1: Read the existing data from the JSON file
    try:
        with open (json_file_path, 'r') as fdb:
            json_data = json.load(fdb)            
    except FileNotFoundError:
        # If the file doesn't exist, handle error
        raise Exception(f"Json file not found {json_file_path}\n")


    for target in out_data:

        if target not in json_data:
            json_data[target] = out_data[target]
        else:
            json_data[target]['changes'] = list(set(json_data[target]['changes'] + out_data[target]['changes']))
        
    try:
        with open(json_file_path, 'w') as fdb:
            json.dump(json_data, fdb, indent=4)
    except:
        # If the file doesn't exist, handle error
        raise Exception(f"Error writing  {json_data} \n to json file: {json_file_path}\n")    





def storeTargetData (target_data):
    # get the target name from path 
    
    target_name = os.path.splitext(os.path.basename(target_data[0]))[0].split('-')[-1]

    out_data = {}    
    out_data['target'] = target_name.replace("_", " ") 
    out_data['changes'] = target_data
        
    if out_data["changes"]:
        db_path = os.path.join(os.getcwd(), "./repo/.github/data-storage/target_db.json")
        print(f"DB path: {db_path}")
        updateTargetJson(db_path, out_data)


def updateTargetJson (json_file_path, out_data):

    json_data = None
    target = out_data.get("target")
    
    # Step 1: Read the existing data from the JSON file
    try:
        with open (json_file_path, 'r') as fdb:
            json_data = json.load(fdb)            
    except FileNotFoundError:
        # If the file doesn't exist, handle error
        raise Exception(f"Json file not found {json_file_path}\n")

    if target not in json_data:
        json_data[target] = {'changes': out_data['changes']}
    else:
        json_data[target]['changes'] = list(set(json_data[target]['changes'] + out_data['changes']))
    
    try:
        with open(json_file_path, 'w') as fdb:
            json.dump(json_data, fdb, indent=4)
    except:
        # If the file doesn't exist, handle error
        raise Exception(f"Error writing  {json_data} \n to json file: {json_file_path}\n")    


def storeForecasts (forecasts, isEnsemble = False):

    team = os.path.basename(os.path.split(forecasts[0])[0]).split('-')[0]
    if not team:
     raise Exception(f"invalid input data  {forecasts}\n")

    out_data = {}    
    out_data['team'] = team
    out_data['models'] = []

    for forecast in forecasts:

        #get the model name from path
        model = tuple(os.path.basename(os.path.split(forecast)[0]).split('-'))[1]

        model_entry = next((item for item in out_data['models'] if item["model"] == model), None)
        if model_entry is None:
            out_data['models'].append({"model" : model, "changes": [forecast]})
        else:
            model_entry["changes"].append(forecast)

    if out_data['models']:        
        db_path = os.path.join(os.getcwd(), "repo/.github/data-storage" + os.path.sep + ("ensemble_db.json" if isEnsemble else "changes_db.json"))
        print(f"DB path: {db_path}")
        updateForecastsJson(db_path, out_data)
    

def updateForecastsJson(json_file_path, changes):

    json_data = None

    team = changes.get("team")
    n_entries = changes.get("models")

    # Step 1: Read the existing data from the JSON file
    try:
        with open (json_file_path, 'r') as fdb:
            json_data = json.load(fdb)            
    except FileNotFoundError:
        # If the file doesn't exist, handle error
        raise Exception(f"Json file not found {json_file_path}\n")

    # Check if the "team" key exists and is a list
    if team not in json_data:
        # if brand new, just save commits
        json_data[team] = n_entries

    else:
        #get the list of previous saved data for this team
        j_records = json_data[team]

        for entry in n_entries:
                
            j_model = [j_record for j_record in j_records if j_record.get("model") == entry.get("model")]
            if j_model == [] :
                j_records.append(entry)
            else:
                j_model[0]["changes"] += set(entry["changes"]).difference (j_model[0]["changes"])

    try:
        with open(json_file_path, 'w') as fdb:
            json.dump(json_data, fdb, indent=4)
    except:
        # If the file doesn't exist, handle error
        raise Exception(f"Error writing  {json_data} \n to json file: {json_file_path}\n")
        

def storeStdData (data, db_file):
    print ("Storing data")
    #"/home/runner/work/the-hub/the-hub/./repo/.github/data-storage/" + db_file
    db_path = os.path.join(os.getcwd(), "./repo/.github/data-storage/", db_file)
    print(f"DB path: {db_path}")
    updateJsonData(db_path, data)


def updateJsonData (json_file_path, changes):

    json_data = None

    # Step 1: Read the existing data from the JSON file
    try:
        with open (json_file_path, 'r') as fdb:
            json_data = json.load(fdb)
            print(f"JSON DB CONTENT: \n{json_data}")
            
    except FileNotFoundError:
        # If the file doesn't exist, handle error
        raise Exception(f"Json file not found {json_file_path}\n")

    json_data["changes"] = changes if "changes" not in json_data else list(set(json_data["changes"] + changes))

    try:
        with open(json_file_path, 'w') as fdb:
            json.dump(json_data, fdb, indent=4)
    except:
        # If the file doesn't exist, handle error
        raise Exception(f"Error writing  {json_data} \n to json file: {json_file_path}\n")


def store(to_store):

    # Make a list out of the changed files
    fchanges = to_store.split(" ")

    # List should not be empty
    if not fchanges:
        raise Exception(f"Empty commit")
    

    model_changes = []
    ensemble_changes = []
    metadata_changes = []
    targetdata_changes = []
    evaluation_changes = []

    
    # 
    for fchanged in fchanges:
                
        # needed for different deepness of paths
        if  fchanged.startswith("model-output" + os.path.sep + "respicast-hubEnsemble"  + os.path.sep) or \
            fchanged.startswith("model-output" + os.path.sep + "respicast-quantileBaseline"  + os.path.sep) or \
            fchanged.startswith("model-output" + os.path.sep + "respicast-hubEnsemble"  + os.path.sep) or \
            fchanged.startswith("model-output" + os.path.sep + "respicast-quantileBaseline"  + os.path.sep) :
            # add to ensemble
            ensemble_changes.append(fchanged)
        elif fchanged.startswith("model-output"):
            # save model output
            model_changes.append(fchanged)
        elif fchanged.startswith("model-metadata"):
            # save meta-data
            metadata_changes.append(fchanged)
        elif fchanged.startswith("target-data") and not 'latest-' in fchanged:
            # save target-data
            targetdata_changes.append(fchanged)
        elif fchanged.startswith("model-evaluation") and not 'latest-' in fchanged:
            # save evaluation-data
            evaluation_changes.append(fchanged)
        else :
            # unknown just discard
            print (f'Unkown file submitted {fchanged}! Skip it')


    if model_changes:
        print (f"{len(model_changes)} changes in model-output")
        storeForecasts(model_changes)

    if ensemble_changes:
        print (f"{len(ensemble_changes)} changes in hub ensemble")
        storeForecasts(ensemble_changes, isEnsemble = True)
    
    if metadata_changes:
        print (f"{len(metadata_changes)} changes in model-metadata")
        storeStdData(metadata_changes, "metadata_db.json")

    if targetdata_changes:
        print (f"{len(targetdata_changes)} changes in targetdata")
        # storeTargetData(targetdata_changes)
        storeMultiTargetData(targetdata_changes)

    if evaluation_changes:
        print (f"{len(evaluation_changes)} changes in targetdata")
        storeStdData(evaluation_changes, "evaluation_db.json")


if __name__ == "__main__":

    store_data = os.getenv("data")        
    store(store_data)
