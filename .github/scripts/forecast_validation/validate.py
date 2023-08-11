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

    # test only
    if not isinstance(toValidate, (list, tuple)):
        print ("to validate is not a list")
        toValidate = [toValidate]

    for elem in toValidate:
        print ("Validating {}".format(elem))
        v.validate_csv_files("influcast_flu_forecast", elem)

    validated = True

    
    with open(env_file, "a") as outenv:
        outenv.write ("authentication={}".format(validated))

if __name__ == "__main__":
    print ("### Testing tools_validate script")
    run()
