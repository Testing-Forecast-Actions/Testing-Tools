import requests

print ("Python Requests - Code test start")
url = 'https://djgleam.isi.it/sleepy/400/'
test_session = requests.Session()
x = test_session.get(url)
# x = requests.get(url)

print("Python Requests - Code test completed")
