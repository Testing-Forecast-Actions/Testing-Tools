import json
from os import path

filename = 'changes_db.json'
jsonContent = None
listObj = []

# check if the file exists
if path.isfile(filename) is False:
  raise Exception("changes db file not found")

# Read the json file content
with open (filename) as fdb:
  jsonContent = json.load(fdb)

# DEBUG - trace
print (f'Json file content: {jsonContent}") 
