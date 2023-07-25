import os
import re
import json
import sys

#
# Receives as an input through the env :
# User: the github user that is requesting changes
# Files: the list of changed files 
# Mapping file: the file to match against to verify user, team and path. If none, default is used 

# matching file configuration
default_mapping_folder = 'assests'
default_mapping_file = 'authenticate-mapping.json'


# class authenticator 
class Authenticator () :

    def __init__(self, user, changes):
        self.user = user
        self.changes = changes
        self.mappings = _defaultMappings()

        self.team = None
        self.models = None


    #
    #
    def verifyPaths (self):

        for model in self.models :
            # Pattern that matches a forecast file added to the data-processed folder.
            # Test this regex usiing this link: https://regex101.com/r/wmajJA/1
            forecast_fname_matching = re.compile(r"^previsioni/(.+)/\d\d\d\d-\d\d.csv$")
        
            invalid_forcast_names = [filename for filename in self.changes if forecast_fname_matching.match(filename) is None]

    
    # 
    #
    def authenticateUser (self):
        j_in = None
        
        # load mappings file
        with open(self.mappings) as f_json_input:
            j_in = json.load(f_json_input)
            
        if j_in is None :
            print("### Failed to open input file")
            return false

        # loop over teams to find current user
        teams = j_in['teams']

        for team in teams:
            if self.user in team['users']:
                #found
                self.team = team['name']
                self.models = team['models']
                return true

        # nothing found 
        return false


    
    def _defaultMappings (self):
        return os.path.join(os.path.dirname(__file__), '..', default_mapping_folder, default_mapping_file)




    



#
def run (jsonInputFile):
    
    actor = os.getenv("calling_actor")
    changes = os.getenv("changed_files")

    if actor is None or changes is None:
        return false
    
    # debug only, to be removed
    print ("### Actor: {}".format(actor))
    print ("### Changed List: {}".format(changes))

    authenticateObj = Authenticator(actor, changes)
    authenticateObj.authenticateUser()
    



if __name__ == "__main__":
    print ("### Testing tools_authenticate script")
    passed = run()
    
    return passed
