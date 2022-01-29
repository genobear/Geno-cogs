from dotenv import load_dotenv
import os 

load_dotenv()
print(os.environ.get('webhookurl'))
print(os.environ.get('logWebHookurl'))

