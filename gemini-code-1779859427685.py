import os
import time
import json
from curl_cffi import requests as browser

# This looks for the variable you will set in Railway
WEBHOOK_URL = os.environ.get("WEBHOOK_URL") 
# ... rest of your code ...