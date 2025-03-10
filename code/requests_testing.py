import requests
import os

t_out = int(os.getenv("time_out"))
rt_out = os.getenv("r_time_out")


print ("Python Requests - Code test start")

# url = 'https://djgleam.isi.it/sleepy/' + rt_out + '/'
url = 'http://chimera.isi.it:8000/test'
data = {"delay": int(rt_out)}

print(f"calling url: {url} with timeout: {t_out}")

try:
  response = requests.post(url, json=data, timeout=t_out)
  
  print("Response headers:", response.headers)
  print(response.json())

except requests.exceptions.RequestException as e:
  print("Errore nella richiesta:", e)
except: 
  print("Errore non gestito")

print("Python Requests - Code test completed")
