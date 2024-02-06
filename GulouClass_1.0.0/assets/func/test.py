import json
import urllib.request as urllib_request
from urllib.parse import urlencode
from urllib.error import URLError
import ssl

def justify_douhao(x):
    x=str(x)
    x=x.replace(",",'、')
    return x
    
university="南京大学"
grade="2021临床医学"
url="https://cloud.seatable.cn/external-apps/42a2a20c-53ee-4817-8caa-2024044c770f/"
try:
    url_list = url.split('/')
    for i in url_list:
        if i=='':
            url_list.remove(i)

    url = 'https://cloud.seatable.cn/api/v2.1/dtable-apps/data-search/'+url_list[-1]+"/query/"
    # url_t = "https://cloud.seatable.cn/api/v2.1/dtable-apps/data-search/42a2a20c-53ee-4817-8caa-2024044c770f/query/"

    data = {"filters":[{"column_name":"学校","is_required":False,"enable_fuzzy_query":True,"case_sensitive":False,"column_key":"0000","filter_predicate":"contains","filter_term":university,"id":"HX94"},
                        {"column_name":"班级","is_required":False,"enable_fuzzy_query":True,"case_sensitive":False,"column_key":"2nCB","filter_predicate":"contains","filter_term":grade,"id":"DW7a"},
                        {"column_name":"科目","is_required":False,"enable_fuzzy_query":True,"case_sensitive":False,"column_key":"g4n1","filter_predicate":"contains","filter_term":"","id":"IaQL"},
                        {"column_name":"日期","is_required":False,"enable_fuzzy_query":True,"case_sensitive":False,"column_key":"r764","filter_predicate":"is","filter_term":'',"filter_term_modifier":"exact_date","id":"exsZ"},
                        {"column_name":"教师（理论课）","is_required":False,"enable_fuzzy_query":True,"case_sensitive":False,"column_key":"w2Cw","filter_predicate":"contains","filter_term":"","id":"Pd53"},
                        {"column_name":"教师（见习课）","is_required":False,"enable_fuzzy_query":True,"case_sensitive":False,"column_key":"tuHc","filter_predicate":"contains","filter_term":"","id":"ebYx"}],
            "start":0,
            "limit":500}  # Post请求发送的数据，字典格式

    headers = {'Origin':'https://cloud.seatable.cn',
            'Referer':'https://cloud.seatable.cn/external-apps/42a2a20c-53ee-4817-8caa-2024044c770f/',
            'Content-Type':'application/json',
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0',
            'Accept':'application/json, text/plain, */*',
            'Authorization':'Token eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE3MDczMDA0MjIsImFwcF91dWlkIjoiNDJhMmEyMGMtNTNlZS00ODE3LThjYWEtMjAyNDA0NGM3NzBmIiwidXNlcm5hbWUiOiIiLCJwZXJtaXNzaW9uIjoicncifQ.RkZXWaX2DbyiK1f_xAvnJ6k19mdQmC6U1GNy0hzLE9s'}
    response_code=0
    # 将数据编码为 JSON 格式
    json_data = json.dumps(data).encode('utf-8')
    response_code=1
    print(response_code)
    # 创建请求对象
    request = urllib_request.Request(url, data=json_data, headers=headers)
    response_code=2
    # 不需要证书
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    print(response_code)
    # 发送 POST 请求
    with urllib_request.urlopen(request,context=context) as response:
        # 读取响应内容
        response_code=response.getcode()
        content = response.read().decode('utf-8')
        j = json.loads(content)
        print(response_code)
        result_data = [i for i in j['results']]

    # 现在 result_data 包含了你想要的结果
    result_data = [i for i in j['results']]

    # 现在 result_data 包含了你想要的结果

    # 将结果写入文件
    with open('assets/conf/internetData.txt', 'w', encoding='utf-8') as file:
        for item in result_data:
            # 将每个信息的内容用逗号隔开，然后写入文件
            file.write(','.join(map(justify_douhao, item.values())) + '\n')

except URLError as e:
    response_code=e

print(response_code)


    