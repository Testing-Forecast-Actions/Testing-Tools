import requests

print ("Python Requests - Code test start")
url = 'https://djgleam.isi.it/sleepy/400/'
test_session = requests.Session()
test_session.headers.update({ "Connection":"keep-alive" })
x = test_session.get(url, timeout=500)
# x = requests.get(url)

print("Python Requests - Code test completed")
