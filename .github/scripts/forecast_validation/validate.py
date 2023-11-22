# main
import os
import re
import json
import sys

import validate_forecasts as v


def run ():

    validated = True


    env_file = os.getenv('GITHUB_OUTPUT')    
    to_validate = os.getenv("changed_files")

    to_validate = to_validate.split(" ")

    for elem in to_validate:
        print ("Validating {}".format(elem))
        try:
            v.validate_csv_files("influcast_flu_forecast", elem)
        except:
            validated = False
            break
    
    
    
    with open(env_file, "a") as outenv:
        print(f"Writing to out: validate: {validated}")
        outenv.write (f"validation={validated}")

    return validated

if __name__ == "__main__":
    print ("### Testing tools_validate script")

    valid_run = run()
    if not valid_run:
        sys.exit(1)
