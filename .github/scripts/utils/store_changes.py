import os
import json


# Update is executed for one team at a time
def update_json_db (json_file_path, new_data):

  json_data = None

  team_name = new_data.get("team")
  models_changes = new_data.get("models")
  
  if not team_name:
     raise Exception(f"invalid input data  {new_data}\n")
  

  # Step 1: Read the existing data from the JSON file
  try:
    with open (json_file_path, 'r') as fdb:
      json_data = json.load(fdb)
      print(f"JSON CONTENT: \n{json_data}")
    
  except FileNotFoundError:
    # If the file doesn't exist, handle error
    raise Exception(f"Json file not found {json_file_path}\n")


  # Check if the "team" key exists and is a list
  if team_name not in json_data:
    # if brand new, just save commits
    json_data[team_name] = models_changes

  else:
    team_commits = json_data[team_name]

    for change in models_changes:
      
      for commit in team_commits :
        
        commit_md = commit.get("model")
        change_md = change.get("model")

        if isinstance (commit_md, (list, dict)):
          print("Commit is list or dict")
        elif isinstance(commit_md, str):
          print("Commit is string")
        else:
          print("Commit is unknown")

        if isinstance (change_md, (list, dict)):
          print("change_md is list or dict")
        elif isinstance(change_md, str):
          print("change_md is string")
        else:
          print("change_md is unknown")
        
      
      committed_model = [commit for commit in team_commits if commit.get("model") == change.get("model")]
      if committed_model == [] :
        team_commits.append(change)
        print("NOT FOUND! Add new team to the backup")
      else:
        committed_model[0]["changes"] += set(change["changes"]).difference (committed_model[0]["changes"])

  print(f"Saving json: \n{json_data}")

  with open(json_file_path, 'w') as fdb:
    json.dump(json_data, fdb, indent=4)

  print(f"JOB DONE >>>>>>>>")



# Main
if __name__ == "__main__":

  # Config
  db_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "changes_db.json")

  updated_json_data = os.getenv("data")
  print ("### Data: {}".format(updated_json_data))
  
  jobj = json.loads(updated_json_data)
  update_json_db (db_path, jobj)
