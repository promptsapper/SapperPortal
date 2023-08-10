import json
import random
from flask import request, session, Blueprint, render_template, redirect

from ..services.JsonSelfDifin import JsonFile
from portal_services.services.response import Answer

from portal_services.services.authentic_login import auth, get_spl

createUrl = Blueprint('createUrl', __name__)
role_prompt_file = JsonFile('../forms/role_system_prompt.json')
users_work_status_file = JsonFile('../forms/users_work_status.json')
spl_role_prompt_data_file = JsonFile('../forms/spl_role_prompt_data.json')
users_pass_work_file = JsonFile('../forms/users_pass_work.json')


@createUrl.route('/create', methods=['POST', 'GET'])
# @auth
def create():
    # 查询用户作品状态
    username = session.get('username')
    if username:
        users_work_status = users_work_status_file.read_json()
        # {
        #   "18270182496": {"status": "UnderReview","statement": ""}
        # }
        # 遍历查询用户作品状态status
        for user in users_work_status:
            if user == username:
                status = users_work_status[user]['status']
                if status == '审核已经通过，请在导航栏的角色选择页面中进行查看!':
                    # 删除users_work_status中的用户
                    del users_work_status[user]
                    users_work_status_file.write_json(users_work_status)
                    return render_template('users_create.html', status=status, login_status=True)
                statement = users_work_status[user]['statement']
                return render_template('users_create.html', status=status, statement=statement, login_status=True)
        return render_template('users_create.html', login_status=True)
    else:
        return render_template('users_create.html', login_status=False)


@createUrl.route('/create_spl_role', methods=['POST', 'GET'])
def create_spl_role():
    # 查询用户作品状态
    username = session.get('username')
    if username:
        users_work_status = users_work_status_file.read_json()
        # {
        #   "18270182496": {"status": "UnderReview","statement": ""}
        # }
        # 遍历查询用户作品状态status
        for user in users_work_status:
            if user == username:
                status = users_work_status[user]['status']
                if status == '审核已经通过，请在导航栏的角色选择页面中进行查看!':
                    # 删除users_work_status中的用户
                    del users_work_status[user]
                    users_work_status_file.write_json(users_work_status)
                    return render_template('users_creat_spl_role.html', status=status, login_status=True)
                statement = users_work_status[user]['statement']
                return render_template('users_creat_spl_role.html', status=status, statement=statement, login_status=True)
        return render_template('users_creat_spl_role.html', login_status=True)
    else:
        return render_template('users_creat_spl_role.html', login_status=False)


@createUrl.route('/user_add_role', methods=['POST', 'GET'])
def user_add_role():
    # 判断用户是否已经提交过作品，查询用户作品状态，如果已经提交过作品，返回错误信息
    username = session.get('username')
    # 如果没有username
    if not username:
        return render_template('login.html')
    users_work_status = users_work_status_file.read_json()
    for user in users_work_status:
        if user == username:
            status = users_work_status[user]['status']
            statement = users_work_status[user]['statement']
            return render_template('users_create.html', status=status, statement=statement)

    role = request.form['role']

    # 判断角色是否已经存在，如果存在，返回错误信息
    role_prompt = role_prompt_file.read_json()
    if role in role_prompt:
        return render_template('users_create.html', error='角色名已存在')
    # 判断user_work_status中是否有role，如果有，返回错误信息
    for user in users_work_status:
        if role == users_work_status[user]['role']:
            return render_template('users_create.html', error='您已经提交过该角色的作品，请等待管理员审核！')
    # 判断用户提交的图片名字file.filename.split('.')[0]是否等于角色名role
    file = request.files['file']
    # 强行将file.filename转换为png格式，且名字为role
    file.filename = role + '.png'

    # # 判断图片是否为png
    # if file.filename.split('.')[-1] != 'png':
    #     return render_template('users_create.html', error='图片格式必须为png')
    # if file.filename.split('.')[0] != role:
    #     return render_template('users_create.html', error='图片名字必须和角色英文名一致')

    # 保存prompt和图片
    prompt = request.form['prompt']
    role_prompt[role] = prompt
    role_prompt_file.write_json(role_prompt)
    file.save('portal_services/static/images/role/' + file.filename)

    # 将图片路径存入photo_path
    photo_path = '../static/images/role/' + file.filename
    # 将role和Chinese存入user_work_status
    Chinese_name = request.form['Chinese']
    users_work_status[username] = {'role': role, 'chinese': Chinese_name, 'status': '您的作品在审核中！', 'statement': '', 'photo_path': photo_path}
    users_work_status_file.write_json(users_work_status)
    # 将username,role，session中的session['spl_prompt']，session['spl_data']保存至文件spl_role_prompt_data_file
    # {"username":uername"role":role,"spl_prompt":session['spl_prompt'],"spl_data":session['spl_data']}
    return render_template('users_create.html', success='您的作品已经提交成功！请等待管理员审核。')


@createUrl.route('/user_add_spl_role', methods=['POST', 'GET'])
def user_add_spl_role():

    # 判断用户是否已经提交过作品，查询用户作品状态，如果已经提交过作品，返回错误信息
    username = session.get('username')
    # 如果没有username
    if not username:
        return render_template('login.html')

    users_work_status = users_work_status_file.read_json()
    for user in users_work_status:
        if user == username:
            status = users_work_status[user]['status']
            statement = users_work_status[user]['statement']
            return render_template('users_creat_spl_role.html', status=status, statement=statement)

    role = request.form['role']

    # 将角色与用户和spl_id对应起来
    spl_id = request.form['spl_id']
    print()
    if spl_id == '' or spl_id is None:
        return render_template('users_creat_spl_role.html', error='您必须前往SapperSpl创建prompt后才能提交Spl角色作品！网址:https://www.aichain.store:3000/')
    spl_role_prompt_data = spl_role_prompt_data_file.read_json()
    # spl_role_prompt_data = {"3124124": {"spl_prompt": "nihfas","spl_data": "fasfa","username": "", "role": ""}}
    # 将spl_role_prompt_data中键为spl_id的值的username设置为username
    spl_role_prompt_data[spl_id]["username"] = username
    spl_role_prompt_data[spl_id]["role"] = role
    spl_role_prompt_data_file.write_json(spl_role_prompt_data)

    # 判断角色是否已经存在，如果存在，返回错误信息
    role_prompt = role_prompt_file.read_json()
    if role in role_prompt:
        return render_template('users_create.html', error='角色名已存在')
    # 判断user_work_status中是否有role，如果有，返回错误信息
    for user in users_work_status:
        if role == users_work_status[user]['role']:
            return render_template('users_create.html', error='您已经提交过该角色的作品，请等待管理员审核！')
    # 判断用户提交的图片名字file.filename.split('.')[0]是否等于角色名role
    file = request.files['file']
    # 强行将file.filename转换为png格式，且名字为role
    file.filename = role + '.png'

    # # 判断图片是否为png
    # if file.filename.split('.')[-1] != 'png':
    #     return render_template('users_create.html', error='图片格式必须为png')
    # if file.filename.split('.')[0] != role:
    #     return render_template('users_create.html', error='图片名字必须和角色英文名一致')

    # 保存prompt和图片
    prompt = request.form['prompt']
    role_prompt[role] = prompt
    role_prompt_file.write_json(role_prompt)
    file.save('portal_services/static/images/role/' + file.filename)

    # 将图片路径存入photo_path
    photo_path = '../static/images/role/' + file.filename
    # 将role和Chinese存入user_work_status
    Chinese_name = request.form['Chinese']
    users_work_status[username] = {'role': role, 'chinese': Chinese_name, 'status': '您的作品在审核中！', 'statement': '', 'photo_path': photo_path}
    users_work_status_file.write_json(users_work_status)
    # 将username,role，session中的session['spl_prompt']，session['spl_data']保存至文件spl_role_prompt_data_file
    # {"username":uername"role":role,"spl_prompt":session['spl_prompt'],"spl_data":session['spl_data']}
    return render_template('users_creat_spl_role.html', success='您的作品已经提交成功！请等待管理员审核。')


@createUrl.route('/test', methods=['POST', 'GET'])
@auth
def test():
    return render_template('test.html')


@createUrl.route('/sapper_spl', methods=['POST', 'GET'])
def sapper_spl():
    print('sapper_spl')
    # data = request.form
    data = request.get_json()
    if data['SPLId'] == '': # 新建SPL_role
        spl_prompt = data['spl_prompt']
        spl_data = data['spl_data']
        spl_id = str(random.randint(1000000000, 9999999999))
        spl_role_prompt_data = spl_role_prompt_data_file.read_json()
        # spl_role_prompt_data = {"3124124": {"spl_prompt": "nihfas","spl_data": "fasfa","username": "", "role": ""}}
        spl_role_prompt_data[spl_id] = {'spl_prompt': spl_prompt, 'spl_data': spl_data,
                                        'username': session.get('username'), "role": ""}
        print(spl_role_prompt_data)
        spl_role_prompt_data_file.write_json(spl_role_prompt_data)
        return json.dumps({'url': 'https://www.aichain.store/sapper_spl_create?spl_id=' + spl_id})
    else: # 修改SPL_role
        # 修改spl_role_prompt_data_file中spl_id对应的spl_prompt和spl_data
        spl_id = data['SPLId']
        spl_prompt = data['spl_prompt']
        spl_data = data['spl_data']
        spl_role_prompt_data = spl_role_prompt_data_file.read_json()
        spl_role_prompt_data[spl_id]['spl_prompt'] = spl_prompt
        spl_role_prompt_data[spl_id]['spl_data'] = spl_data
        role = spl_role_prompt_data[spl_id]['role']
        spl_role_prompt_data_file.write_json(spl_role_prompt_data)

        # 修改role_prompt_file中role对应的prompt
        role_prompt = role_prompt_file.read_json()
        role_prompt[role] = spl_prompt
        role_prompt_file.write_json(role_prompt)
        return json.dumps({'code': 200})


@createUrl.route('/sapper_spl_create', methods=['POST', 'GET'])
def sapper_spl_create():
    # 获取url中的spl_prompt和spl_data
    spl_id = request.args.get('spl_id')
    # 存入session
    session['splId'] = spl_id
    print(spl_id)
    spl_role_prompt_data = spl_role_prompt_data_file.read_json()
    spl_prompt = spl_role_prompt_data[spl_id]['spl_prompt']
    username = spl_role_prompt_data[spl_id]['username']
    if username == "None":
        return render_template('users_creat_spl_role.html', spl_prompt=spl_prompt, login_status=False, spl_id=spl_id)
    else:
        return render_template('users_creat_spl_role.html', spl_prompt=spl_prompt, login_status=True, spl_id=spl_id)


@createUrl.route('/user_view_spl_roles', methods=['POST', 'GET'])
@auth
def user_view_spl_roles():
    # 先从users_pass_work中读取用户username所有的role，并存入all_pass_roles,再遍历spl_role_prompt_data，判断role是否在all_pass_roles,如果在则将role所在的键值对存入spl_pass_roles中，最后将spl_pass_roles return给前端
    username = session.get('username')
    users_pass_work = users_pass_work_file.read_json()
    all_pass_roles = []
    for user in users_pass_work:
        if user == username:
            for role in users_pass_work[user]:
                all_pass_roles.append(role['role'])
    print('all_pass_roles:', all_pass_roles)
    # all_pass_roles = [{'role': 'translator', 'count': 0, 'count_to_money': 200, 'reward_money': 4.8}, {'role': 'qwe', 'count': 0, 'count_to_money': 200, 'reward_money': 4.8}, {'role': 'rabbit', 'count': 200, 'count_to_money': 0, 'reward_money': 0}]
    spl_role_prompt_data = spl_role_prompt_data_file.read_json()
    spl_pass_roles = {}
    for spl_id in spl_role_prompt_data:
        if spl_role_prompt_data[spl_id]['role'] in all_pass_roles:
            spl_pass_roles[spl_id] = spl_role_prompt_data[spl_id]
    # 如果spl_pass_roles为空，返回错误信息
    print('spl_pass_roles:', spl_pass_roles)
    if spl_pass_roles == {}:
        return 'NULL'
    else:
        return spl_pass_roles


@createUrl.route('/sapper_get_spl', methods=['POST', 'GET'])
def sapper_get_spl():
    print('sapper_get_spl')
    data = request.get_json()
    print(data)
    spl_id = data['SPLId']
    spl_role_prompt_data = spl_role_prompt_data_file.read_json()
    spl_prompt = spl_role_prompt_data[spl_id]['spl_prompt']
    spl_data = spl_role_prompt_data[spl_id]['spl_data']
    # 将{“spl_prompt”：spl_prompt，“spl_data”：spl_data} return给前端
    return json.dumps({'spl_prompt': spl_prompt, 'spl_data': spl_data})

