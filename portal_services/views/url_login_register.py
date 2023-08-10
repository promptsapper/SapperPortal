import json
import random
from flask import Blueprint, render_template, request, session
from portal_services.services.JsonSelfDifin import JsonFile
from portal_services.services.login import login_check, register_check, send_code

login_register = Blueprint('login_register', __name__)


user_info = JsonFile('../forms/users_pwd_tokens.json')


@login_register.route('/login', methods=['GET'])
def show_login_page():
    return render_template("login.html", register=False, login_status=False)


@login_register.route('/lg_register', methods=['GET'])
def show_login_register_page():
    return render_template("login.html", register=True, login_status=False)


@login_register.route('/login', methods=['POST'])
def login():
    username = request.form.get('userName')
    password = request.form.get('passWord')
    # 判断是否登录成功:login_check()返回的是一个重定向对象或者回到登录页面
    return login_check(username, password)


@login_register.route('/register', methods=['POST', 'GET'])
def register():
    # 如果是GET请求请求，表明是获取验证码
    if request.method == 'GET':
        phone = request.args.get('phone')
        # 判断是否已经发送过验证码，如果已经发送过，就不再发送
        if session.get('verification_code'):
            # sc = session.get('verification_code')
            # print('已经发送过验证码了', sc)
            # session.pop('verification_code')
            return json.dumps({'code': 4000, 'msg': '验证码已发送过了，请注意查收，如果未接收到请检查手机号码是否正确。'}, ensure_ascii=False)
        # 判断手机号是否已经注册
        for user in user_info.read_json():
            if user['user'] == phone:
                return json.dumps({'code': 4000, 'msg': '手机号已注册'}, ensure_ascii=False)
        else:
            random_code = str(random.randint(1000, 9999))
            session['verification_code'] = random_code
            code_msg = send_code(phone, random_code)
            # 如果status不为False，表明验证码发送成功
            return json.dumps(code_msg, ensure_ascii=False)

    # 如果是POST请求，表明是注册，点击注册按钮了。
    if request.method == 'POST':
        verification_code = session.get('verification_code')
        username = request.form.get('userName')
        password = request.form.get('passWord')
        input_code = request.form.get('code')

        return register_check(verification_code, username, password, input_code)


@login_register.route('/user_login_out', methods=['GET', 'POST'])
def login_out():
    session.pop('username', None)
    session.pop('password', None)
    return render_template('login.html', register=False, login_status=False)


@login_register.route('/return_login', methods=['GET', 'POST'])
def return_login():
    # 对应login.html中的register=true的返回登录按钮，设置register为false，返回登录页面
    username = session.get('username')
    password = session.get('password')
    return render_template('login.html', register=False, username=username, password=password, login_status=False)


