import requests

print ("Python Requests - Code test start")

url = 'https://djgleam.isi.it/sleepy/400/'
try:
  response = requests.get(url, timeout=600)
  
  print("Response headers:", response.headers)
  print(response.json())

except requests.exceptions.RequestException as e:
    print("Errore nella richiesta:", e)

print("Python Requests - Code test completed")
