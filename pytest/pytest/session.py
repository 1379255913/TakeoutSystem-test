import requests

url_headers='http://127.0.0.1:5000'
def session1():
    s = requests.Session()
    data = {'email': '1379255913@qq.com', 'password': '123456'}
    rps = s.post(url_headers + '/login', data=data)
    # print(rps.cookies.get_dict())
    return s

def session2():
    s = requests.Session()
    data = {'email': '1234@qq.com', 'password': '123456'}
    rps = s.post(url_headers + '/login', data=data)
    # print(rps.cookies.get_dict())
    return s


def session3():
    s = requests.Session()
    data = {'email': 'e@qq.com', 'password': '123456'}
    rps = s.post(url_headers + '/login', data=data)
    # print(rps.cookies.get_dict())
    return s

def session4():
    s = requests.Session()
    data = {'email': 'test@qq.com', 'password': '123456'}
    rps = s.post(url_headers + '/login', data=data)
    # print(rps.cookies.get_dict())
    return s

def session5():
    s = requests.Session()
    data = {'email': 'test2@qq.com', 'password': '123456'}
    rps = s.post(url_headers + '/login', data=data)
    # print(rps.cookies.get_dict())
    return s