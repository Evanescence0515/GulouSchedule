import json
import urllib.request as urllib_request
from urllib.parse import urlencode
from urllib.error import URLError
import ssl
import re

    

url="https://cloud.seatable.cn/external-apps/42a2a20c-53ee-4817-8caa-2024044c770f/"
    # 创建请求对象

with urllib_request.urlopen(url) as response:
    data = response.read()
    raw_html_data=data.decode('utf-8')

match = re.search(r"accessToken: '([^']+)'", raw_html_data)

if match:
    access_token = match.group(1)
    print("AccessToken:", access_token)
else:
    print("AccessToken not found")


