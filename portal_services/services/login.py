from flask import render_template, session, redirect
from portal_services.services.JsonSelfDifin import JsonFile
import json
import urllib.parse
import urllib.request

user_info = JsonFile('../forms/users_pwd_tokens.json')


def login_check(username, password):
    for user in user_info.read_json():
        # 判断用户名是否存在
        if user['user'] == username:
            # 判断密码是否匹配
            if user['password'] == password:
                session['username'] = username
                session['password'] = password
                return redirect('/')
            else:
                return render_template("login.html", error='密码错误', register=False, username=username)
    # 用户名不存在
    return render_template("login.html", error='输入账号不存在', register=False, username=username)


def register_check(verification_code, username, password, input_code):
    # 判断用户名是否已经注册
    for user in user_info.read_json():
        if user['user'] == username:
            return render_template('login.html', register=True, error='用户名已注册', reg_username=username)
    # print('注册验证', username, password, input_code, verification_code)
    # 验证码正确
    if input_code == verification_code:
        # 将用户名和密码存入文件，并配置初始token15次免费使用
        data = user_info.read_json()
        data.append({'user': username, 'password': password, 'tokens': 15})
        user_info.write_json(data)
        # print('注册成功', username, password)
        session['username'] = username
        session['password'] = password
        # 删除session中的验证码
        session.pop('verification_code')
        # 新建用户账单文件"{username}_bill.json"
        with open(f'portal_services/forms/users_bill/{username}_bill.json', 'w', encoding='utf-8') as f:
            json.dump({}, f, ensure_ascii=False)
        return render_template('login.html', register=False, username=username, password=password)
    else:# 验证码错误
        return render_template('login.html', register=True, error='验证码错误', reg_username=username, reg_password=password)


# 互亿无线返回的是一个字典，里面有一个code，如果code为2，表明发送成功
def send_code(phone, random_code):
    # print('send_code', phone)
    # 接口地址
    url = 'http://106.ihuyi.com/webservice/sms.php?method=Submit'

    # 定义请求的数据
    values = {
        'account': 'your account',
        'password': 'your password',
        'mobile': phone,
        'content': '您的验证码是：' + random_code + '。请不要把验证码泄露给其他人。',
        'format': 'json',
    }

    # 将数据进行编码
    data = urllib.parse.urlencode(values).encode(encoding='UTF8')

    # 发起请求
    req = urllib.request.Request(url, data)
    response = urllib.request.urlopen(req)
    res = response.read().decode("utf8")

    code_msg = json.loads(res)
    return code_msg
