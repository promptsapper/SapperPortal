import random
import string

from flask import Blueprint, render_template, request, flash, redirect, get_flashed_messages, session
from ..services.JsonSelfDifin import JsonFile
import functools
import os
adminUrl = Blueprint('adminUrl', __name__)

users_file = JsonFile('../forms/users_pwd_tokens.json')
role_use_count_file = JsonFile('../forms/role_use_count.json')
role_prompt_file = JsonFile('../forms/role_system_prompt.json')
api_key_file = JsonFile('../forms/api_key.json')
for_roleSelect_show_file = JsonFile('../forms/for_roleSelection_show.json')
users_work_status_file = JsonFile('../forms/users_work_status.json')
users_pass_work_file = JsonFile('../forms/users_pass_work.json')
users_pwd_tokens_file = JsonFile('../forms/users_pwd_tokens.json')


def auth(func):
    @functools.wraps(func)  # 保留原函数的元信息, 如函数名, 参数列表等
    def inner(*args, **kwargs):
        # 判断session中是否有username
        username = session.get('admin')
        # print(username)
        if username:
            return func(*args, **kwargs)
        else:
            return render_template("admin_login.html")

    return inner


@adminUrl.route('/admin', methods=['POST', 'GET'])
def admin():
    # 取出flash消息
    flash_error = get_flashed_messages()
    error = ""
    if flash_error:
        error = flash_error[0]
    return render_template('admin_login.html', error=error)


@adminUrl.route('/adminCheck', methods=['POST', 'GET'])
def adminCheck():
    username = request.form['username']
    password = request.form['password']
    if username == '88888888' and password == '123':
        session['admin'] = username
        return render_template('admin_index.html')
    else:
        # 设置flash消息
        flash('Invalid username or password')
        return redirect('/admin')
# '1q2s3c4f5t'


@adminUrl.route('/admin_login_out', methods=['POST', 'GET'])
def login_out():
    session.pop('admin', None)
    return render_template('admin_login.html')


@adminUrl.route('/show_user', methods=['POST', 'GET'])
@auth
def show_user():

    users = users_file.read_json()
    show_users = True
    return render_template('admin_index.html', users=users, show_users=show_users)


@adminUrl.route('/show_prompt', methods=['POST', 'GET'])
@auth
def show_prompt():
    prompt = role_prompt_file.read_json()
    show_prompts = True
    return render_template('admin_index.html', prompt=prompt, show_prompts=show_prompts)


@adminUrl.route('/show_count', methods=['POST', 'GET'])
@auth
def show_count():
    count = role_use_count_file.read_json()
    show_counts = True
    return render_template('admin_index.html', count=count, show_counts=show_counts)


@adminUrl.route('/show_rewards', methods=['POST', 'GET'])
@auth
def show_rewards():
    rewards = users_pass_work_file.read_json()
    return render_template('admin_index.html', rewards=rewards, show_rewards=True)


@adminUrl.route('/show_users_work_status', methods=['POST', 'GET'])
@auth
def show_users_work_status():
    users_work_status = users_work_status_file.read_json()
    return render_template('admin_index.html', users_work_status=users_work_status, show_users_work_status=True)


@adminUrl.route('/show_key', methods=['POST', 'GET'])
@auth
def show_key():
    key = api_key_file.read_json()
    # print(key["api_key"])
    api_key = key["api_key"]
    show_keys = True
    return render_template('admin_index.html', api_key=api_key, show_keys=show_keys)


@adminUrl.route('/del_user/<user>', methods=['POST', 'GET'])
@auth
def del_user(user):
    users = users_file.read_json()
    for i in range(len(users)):
        if users[i]['user'] == user:
            del users[i]
            break
    users_file.write_json(users)
    return redirect('/show_user')


@adminUrl.route('/edit_user', methods=['POST', 'GET'])
@auth
def edit_user():
    data = request.get_json()
    user = data['user']
    password = data['password']
    tokens = int(data['tokens'])
    # print(user, password, tokens)
    has_user = False
    users = users_file.read_json()
    for i in range(len(users)):
        if users[i]['user'] == user:
            has_user = True
            # print('找到用户')
            users[i]['password'] = password
            users[i]['tokens'] = tokens
            break
    if not has_user:
        # print('没有找到用户')
        users.append(data)
    users_file.write_json(users)
    return {'code': '200'}


@adminUrl.route('/edit_key', methods=['POST', 'GET'])
@auth
def edit_key():
    data = request.get_json()
    api_key = data['api_key']
    # print(api_key)
    api_key_file.write_json({"api_key": api_key})
    return {'code': 200}


@adminUrl.route('/delete_role', methods=['POST', 'GET'])
@auth
def delete_role():
    data = request.get_json()
    role = data['role']
    print(role)

    # 删除文件role_prompt_file中key为role的键值对
    # 删除role_prompt_file中key为role的键值对
    role_prompt = role_prompt_file.read_json()
    if role in role_prompt:
        del role_prompt[role]
    role_prompt_file.write_json(role_prompt)

    # 删除for_roleSelect_show_file中key为role的键值对
    for_roleSelect_show = for_roleSelect_show_file.read_json()
    if role in for_roleSelect_show:
        del for_roleSelect_show[role]
    for_roleSelect_show_file.write_json(for_roleSelect_show)

    # 删除role+'.png'的图片
    os.remove('portal_services/static/images/role/'+role+'.png')

    # 删除文件users_work_status_file中key为role的键值对
    users_work_status = users_work_status_file.read_json()
    # 如果role在users_work_status中，删除整个键值对
    for key, value in users_work_status.copy().items():
        if value['role_id'] == role:
            del users_work_status[key]
    users_work_status_file.write_json(users_work_status)

    # 删除users_pass_work.json中role的键值对
    # 遍历users_pass_work_file，如果role在value中，判断value的长度，如果长度为1，删除整个键值对，如果长度大于1，删除value中role的键值对
    users_pass_work = users_pass_work_file.read_json()
    for key, value in users_pass_work.copy().items():
        for i in range(len(value)):
            if value[i]['role_id'] == role:
                if len(value) == 1:
                    del users_pass_work[key]
                else:
                    del value[i]
                break
    users_pass_work_file.write_json(users_pass_work)
    return {'code': 200}


@adminUrl.route('/add_role', methods=['POST', 'GET'])
@auth
def add_role():
    if request.method == 'GET':
        return render_template('admin_add_role.html')
    else:
        # POST:接收文件
        file = request.files['file']
        prompt = request.form['prompt']
        category = request.form['category']
        helloWord = request.form['helloWord']
        chineseName = request.form['chineseName']

        # 判断角色是否已经存在，如果存在，返回错误信息
        role_prompt = role_prompt_file.read_json()
        for key, value in role_prompt.items():
            if value['chineseName'] == chineseName:
                return render_template('admin_add_role.html', error='角色名已存在')
        role_id = ''.join(random.sample(string.ascii_letters + string.digits, 15))
        role_prompt[role_id] = {'chineseName': chineseName, 'prompt': prompt}
        role_prompt_file.write_json(role_prompt)

        # 前端通过form表单传照片文件，<input type="file" name="file">，将照片新建保存到static/images/目录下
        file.filename = role_id + '.png'
        file.save('portal_services/static/images/role/' + file.filename)

        # 将角色信息保存到for_roleSelect_show.json文件中
        for_roleSelect_show = for_roleSelect_show_file.read_json()
        for_roleSelect_show[role_id] = {'chineseName': chineseName, 'category': category, 'helloWord': helloWord}
        for_roleSelect_show_file.write_json(for_roleSelect_show)

        return render_template('admin_add_role.html', success='添加成功')


@adminUrl.route('/pass_work', methods=['POST', 'GET'])
@auth
def pass_work():
    # url获取参数
    role_id = request.args.get('role_id')
    username = request.args.get('username')
    chineseName = request.args.get('chineseName')
    category = request.args.get('category')

    role_prompt = role_prompt_file.read_json()
    # {"wanneng": {"chineseName": "万能助手", "prompt": "You are a versatile assistant, helping to answer all kinds of questions.", "helloWord": "你好，我是你的万能助手。"}, "poet": {"chineseName": "诗人", "prompt": "你是一名专业的诗人，不管我说什么，你都用诗句回答！你只能用诗句回答我的问题！只能是古诗！", "helloWord": "你好，我会用诗句回答你的问题。"}}
    # 获取helloWord
    helloWord = role_prompt[role_id]['helloWord']
    # 读取users_work_status.json文件，将status的值改为"审核已经通过，请正在导航栏的角色选择页面中进行查看!"
    # <a href="/pass_work?username={{ key }}&role={{ value.role }}">通过</a>
    users_work_status = users_work_status_file.read_json()
    # 找到username对应的键，将status的值改为"审核已经通过，请正在导航栏的角色选择页面中进行查看!"
    # print(username)
    for key, value in users_work_status.items():
        if key == username:
            value['status'] = "审核已经通过，请在导航栏的角色选择页面中进行查看!"
            break
    users_work_status_file.write_json(users_work_status)

    # 在role_use_count.json文件中，新建键值对，键为role，值为0。role_use_count.json文件格式[{"role": "wanneng", "count": 50}, {"role": "xingzuo", "count": 3}]
    role_use_count = role_use_count_file.read_json()
    # 判断role_use_count中是否存在role，如果存在，不做任何操作，如果不存在，新建键值对，键为role，值为0
    for role_use_count_item in role_use_count:
        if role_use_count_item['role_id'] == role_id:
            break
    else:
        role_use_count.append({'role_id': role_id, "chineseName": chineseName, 'count': 0})
        role_use_count_file.write_json(role_use_count)

    # 将角色role和chinese_name保存到for_roleSelect_show.json文件中
    for_roleSelect_show = for_roleSelect_show_file.read_json()
    for_roleSelect_show[role_id] = {'chineseName': chineseName, 'category': category, 'helloWord': helloWord}
    print(for_roleSelect_show)
    for_roleSelect_show_file.write_json(for_roleSelect_show)
    # 记录下作品对应的创作者用户，users_pass_work_file,如果用户存在则追加，否则新建
    users_pass_work = users_pass_work_file.read_json()
    if username in users_pass_work:
        # 判断role_id是否存在，如果存在，不做任何操作，如果不存在，追加
        for user_pass_work in users_pass_work[username]:
            if user_pass_work['role_id'] == role_id:
                break
        else:
            users_pass_work[username].append({'role_id': role_id, 'chineseName': chineseName, 'count': 0, 'count_to_money': 0, 'reward_money': 0})
    else:# 否则新建
        users_pass_work[username] = [{'role_id': role_id, 'chineseName': chineseName, 'count': 0, 'count_to_money': 0, 'reward_money': 0}]
    users_pass_work_file.write_json(users_pass_work)
    return render_template('admin_index.html', show_users_work_status=True, users_work_status=users_work_status)


@adminUrl.route('/edit_rewards', methods=['POST', 'GET'])
@auth
def edit_rewards():
    # 读取users_pass_work_file文件，将用户对应的角色的count_to_money和reward_money改为前端传过来的值
    data = request.get_json()

    username = data['username']
    role = data['role']
    count = int(data['count'])
    count_to_money = int(data['count_to_money'])
    if data['reward_money'] == '0':
        reward_money = int(data['reward_money'])
    else: # 因为字符串0转浮点数会报错，所以这里用int转0，float转其他
        reward_money = float(data['reward_money'])
    exchange_count = int(data['exchange_count'])
    if exchange_count == '' or exchange_count == 0:
        return {'code': 201, 'msg': '兑换次数不能为0！'}
    # 判断exchange_count是否小于count，如果小于则提示管理员“角色使用次数不足”
    if exchange_count > count:
        return {'code': 201, 'msg': '角色使用次数不足！'}
    # 否则代表角色使用次数够，进行角色使用次数到金币的转换，exchange_money = exchange_count * 0.024
    exchange_money = exchange_count * 0.024
    count = count - exchange_count
    count_to_money = count_to_money + exchange_count
    reward_money = reward_money + exchange_money
    # 读取users_pass_work_file文件
    users_pass_work = users_pass_work_file.read_json()
    # 找到username对应的键，再找到role对应的键，将count，count_to_money和reward_money改为前端传过来的值
    for user, value in users_pass_work.items():
        if user == username:
            for role_dict in value:
                if role_dict['role'] == role:
                    role_dict['count'] = count
                    role_dict['count_to_money'] = count_to_money
                    role_dict['reward_money'] = reward_money
                    break
            break
    users_pass_work_file.write_json(users_pass_work)
    return {'code': 200, 'exchange_count': exchange_count, 'exchange_money': exchange_money}
