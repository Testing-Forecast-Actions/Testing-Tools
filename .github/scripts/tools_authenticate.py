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
# TODO DO -> Move to an external config file
default_saving_path = 'previsioni'
default_mapping_folder = 'assests'
default_mapping_file = 'authenticate-mapping.json'


# class authenticator 
class Authenticator () :

    def __init__(self, user, changes):
        self.user = user
        self.changes = changes
        self.mappings = self._defaultMappings()

        self.team = None
        self.models = None


    def authenticate (self): 
        # verify user
        if not self._authenticateUser():
            # handle invalid user
            return False
        
        if not self._verifyPaths():
            # handle invalid paths
            return False
        
        # everything look ok from an authentication point of view
        return True

    #
    #
    def _verifyPaths (self):

        matching_list = []
        for model in self.models :
            matching_list.append(os.path.join(default_saving_path, self.team + '_' + model))

        invalid_forcast_paths = [changed_file for changed_file in self.changes if not os.path.split(changed_file)[0] in matching_list]
        if invalid_forcast_paths:
            # handle trying to save an unauthorised path 
            print ("trying to save in unauthorised path")
            return False
        
        print ("Paths look ok, check file name")

        # Pattern that matches a forecast file added to the data-processed folder.
        # Test this regex usiing this link: https://regex101.com/r/wmajJA/1
        forecast_fname_matching = re.compile(r"^previsioni/(.+)/\d\d\d\d_\d\d.csv$")    
        invalid_forcast_names = [changed_file for changed_file in self.changes if forecast_fname_matching.match(changed_file) is None]

        if invalid_forcast_names:
            # handle trying to save an unauthorised path 
            print ("trying to save with an invalid file name")
            return False

        print ("Names look ok, go on")

        return True
    

    # 
    # Verify that the actor of the PR is currently in the authorised db and 
    # map it back to its Team and Models
    def _authenticateUser (self):
        j_in = None
        
        # load mappings file
        with open(self.mappings) as f_json_input:
            j_in = json.load(f_json_input)
            
        if j_in is None :
            print("### Failed to open input file")
            return False

        # loop over teams to find current user
        teams = j_in['teams']

        for team in teams:
            if self.user in team['users']:
                #found
                self.team = team['name']
                self.models = team['models']
                return True

        # nothing found 
        return False
    
    def _defaultMappings (self):
        return os.path.join(os.path.dirname(__file__), '..', default_mapping_folder, default_mapping_file)


#
def run ():

    actor = os.getenv("calling_actor")
    changes = os.getenv("changed_files")

    if actor is None or changes is None:
        return False
    
    # debug only, to be removed
    print ("### Actor: {}".format(actor))
    print ("### Changed List: {}".format(changes))

    authenticateObj = Authenticator(actor, changes)
    authenticateObj.authenticate()

    return True
    



if __name__ == "__main__":
    print ("### Testing tools_authenticate script")

    passed = run()
