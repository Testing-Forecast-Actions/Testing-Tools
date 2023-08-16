# main
import os
import re
import json
import sys

import validate_forecasts as v


def run ():
    print (">>>>>>>>> Running validation main")

    env_file = os.getenv('GITHUB_OUTPUT')    
    to_validate = os.getenv("changed_files")

    to_validate = to_validate.split(" ")

    for elem in to_validate:
        print ("Validating {}".format(elem))
        v.validate_csv_files("influcast_flu_forecast", elem)

    validated = True
    
    with open(env_file, "a") as outenv:
        outenv.write ("validation={}".format(authenticated))


if __name__ == "__main__":
    print ("### Testing tools_validate script")
    run()
