import os
import json
import sys


#
def getInputFromOutput():
    env_file = os.getenv('GITHUB_OUTPUT')

    local_var = os.getenv("local_test_var")
    actor_from_steps = os.getenv("calling_actor")
    changed_list = os.getenv("changed_files")

    print ("### LOCAL VAR: {}".format(local_var))
    print ("### Actor: {}".format(actor_from_steps))
    print ("### Changed List: {}".format(changed_list))
    
    with open (env_file, 'r') as gh_env_file:
        print ("### OUTPUT content read START>>>>>>>>>> ")
        print (gh_env_file.read())
        print ("### OUTPUT content read STOP >>>>>>>>>> ")
    


#
def run (jsonInputFile):

    getInputFromOutput()

    with open(jsonInputFile) as f_json_input:
        j_in = json.load(f_json_input)
        if j_in == None :
            print("### Failed to open input file")
        else :
            print("### Input file opened: {}".format(j_in))

        teams = j_in['mapping']['teams']

        for team in teams:
            print ("### Team content: {}".format(team))



if __name__ == "__main__":
    print ("### Testing tools_verify script")

    # if len(sys.argv) <= 1 :
    #   print ("Missing input. Abort!")
    #   exit(0)

    # input_data_json = sys.argv[1]
    # print ("Input data: \n {}".format(input_data_json))

    runningPath = os.path.dirname(__file__)
    jsonInputFile = os.path.join(runningPath, '..', 'assets', 'authenticate-mapping.json')

    print ("### Running path: {0}, file: {1}".format(runningPath, jsonInputFile))
    run(jsonInputFile)
