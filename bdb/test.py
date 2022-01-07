from decouple import config

url1 = config('webhookurl',default='')
url2 = config('logWebHookurl',default='')

print(url1)
print(url2)