import os
import re
import json
import sys
import requests
import hmac
import hashlib



class BodyDigestSignature(object):
    def __init__(self, secret, header='Sign', algorithm=hashlib.sha512):
        self.secret = secret
        self.header = header
        self.algorithm = algorithm

    def __call__(self, request):
        body = request.body
        if not isinstance(body, bytes):   # Python 3
            body = body.encode('latin1')  # standard encoding for HTTP
        signature = hmac.new(self.secret, body, digestmod=self.algorithm)
        request.headers[self.header] = signature.hexdigest()
        return request



class Sender () :
  def __init__(self, webhook_url):
    
    self.webhook_url = webhook_url


  def send (self, payload, signature):
    # x-hub-signature-256" in request.headers

    r = requests.post(self.webhook_url, json=payload, headers = headers, auth=BodyDigestSignature(secret))
    
    print(f"Status Code: {r.status_code}, Response: {r.json()}")


#
def run ():
  # get env parameters
  env_file = os.getenv('GITHUB_OUTPUT')
    
  wh_url = os.getenv("webhook_url")
  wh_secret = os.getenv("webhook_secret")
  custom_json_data = os.getenv("data")

  # debug only, to be removed
  print ("### Url: {}".format(wh_url))
  print ("### Secret: {}".format(wh_secret))
  print ("### Data: {}".format(custom_json_data))
  # debug only, to be removed


  if wh_url is None or wh_secret is None or custom_json_data is None:
      return False
  

  return True




if __name__ == "__main__":
    print ("### Testing WebHook tool script")

    passed = run()

    if passed : 
        print ("### >>>>>>>>>> SENT")
    else:
        print ('### >>>>>>>>>> INVALID')
