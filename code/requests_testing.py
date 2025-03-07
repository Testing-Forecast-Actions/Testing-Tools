import requests
import os

t_out = os.getenv("time_out")

print ("Python Requests - Code test start")

url = 'https://djgleam.isi.it/sleepy/' + t_out + '/'

print(f"calling url: {url}")

try:
  response = requests.get(url, timeout=600)
  
  print("Response headers:", response.headers)
  print(response.json())

except requests.exceptions.RequestException as e:
    print("Errore nella richiesta:", e)

print("Python Requests - Code test completed")
