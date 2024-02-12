import urllib3
from urllib3.exceptions import MaxRetryError
try:
    http = urllib3.PoolManager()
    response = http.request('GET', f"http://172.22.132.35/getLinha/172.22.132.35")
    print(response.responseJson)

except MaxRetryError:
    print("a")