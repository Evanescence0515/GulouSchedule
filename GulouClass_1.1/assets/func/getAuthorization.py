from . import urllib_request, re, ssl 


def getAuthorization(url):
    try:
        url="https://cloud.seatable.cn/external-apps/42a2a20c-53ee-4817-8caa-2024044c770f/"
        # 不需要证书
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        # 创建请求对象
        with urllib_request.urlopen(url,context=context) as response:
            data = response.read()
            raw_html_data=data.decode('utf-8')
        match = re.search(r"accessToken: '([^']+)'", raw_html_data)
        if match:
            access_token = match.group(1)
            return access_token
        else:
            return "Error, can't find authorization"
    except:
        return "Authorization获取失败"