import json
import random
import string

from flask import request, session, Blueprint, render_template

from ..services.JsonSelfDifin import JsonFile
from ..services import sapperRequire2json
from ..services import sapperSpl2nl
from ..services import sapperNl2spl
from ..services import sapperForm
from portal_services.services.authentic_login import auth

createUrl = Blueprint('createUrl', __name__)
role_prompt_file = JsonFile('../forms/role_system_prompt.json')
users_work_status_file = JsonFile('../forms/users_work_status.json')
spl_role_prompt_data_file = JsonFile('../forms/spl_role_prompt_data.json')
users_pass_work_file = JsonFile('../forms/users_pass_work.json')
for_roleSelect_file = JsonFile('../forms/for_roleSelection_show.json')


@createUrl.route('/create', methods=['POST', 'GET'])
# @auth
def create():
    # 查询用户作品状态
    username = session.get('username')
    if username:
        users_work_status = users_work_status_file.read_json()
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
        # 遍历查询用户作品状态status
        for user in users_work_status:
            if user == username:
                status = users_work_status[user]['status']
                if status == '审核已经通过，请在导航栏的角色选择页面中进行查看!':
                    # 删除users_work_status中的用户
                    del users_work_status[user]
                    users_work_status_file.write_json(users_work_status)
                    return render_template('users_create_spl_role.html', status=status, login_status=True)
                statement = users_work_status[user]['statement']
                return render_template('users_create_spl_role.html', status=status, statement=statement,
                                       login_status=True)
        return render_template('users_create_spl_role.html', login_status=True)
    else:
        return render_template('users_create_spl_role.html', login_status=False)


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

    # form表单post
    file = request.files['file']
    prompt = request.form['prompt']
    category = request.form['category']
    helloWord = request.form['helloWord']
    chineseName = request.form['chineseName']

    # 判断角色是否已经存在，如果存在，返回错误信息
    role_prompt = role_prompt_file.read_json()
    for key, value in role_prompt.items():
        if value['chineseName'] == chineseName:
            return render_template('users_create.html', error='The AI name already exists')
    role_id = ''.join(random.sample(string.ascii_letters + string.digits, 15))
    role_prompt[role_id] = {'chineseName': chineseName, 'prompt': prompt, 'helloWord': helloWord}
    role_prompt_file.write_json(role_prompt)

    # 前端通过form表单传照片文件，<input type="file" name="file">，将照片新建保存到static/images/目录下
    file.filename = role_id + '.png'
    file.save('portal_services/static/images/role/' + file.filename)

    # 将图片路径存入photo_path
    photo_path = '../static/images/role/' + file.filename

    # 判断user_work_status中是否有role，如果有，返回错误信息
    for user in users_work_status:
        if chineseName == users_work_status[user]['chineseName']:
            return render_template('users_create.html', error='您已经提交过该角色的作品，请等待管理员审核！')

    # 将role,category和chineseName存入user_work_status
    users_work_status[username] = {'role_id': role_id, 'chineseName': chineseName, "category": category,
                                   'status': '您的作品在审核中！', 'statement': '', 'photo_path': photo_path}
    users_work_status_file.write_json(users_work_status)
    return render_template('users_create.html', success='您的作品已经提交成功！请等待管理员审核。')


@createUrl.route('/user_add_spl_role', methods=['POST', 'GET'])
def user_add_spl_role():
    # 判断用户是否已经提交过作品，查询用户作品状态，如果已经提交过作品，返回错误信息
    username = session.get('username')
    # 如果没有username
    if not username:
        return render_template('login.html', register=False, login_status=False)

    # 用户登录了的，有提交作品在审核就返回信息
    users_work_status = users_work_status_file.read_json()
    for user in users_work_status:
        if user == username:
            status = users_work_status[user]['status']
            statement = users_work_status[user]['statement']
            return render_template('users_create_spl_role.html', status=status, statement=statement)

    chineseName = request.form['chineseName']
    spl_id = request.form['spl_id']
    prompt = request.form['prompt']
    category = request.form['category']
    helloWord = request.form['helloWord']

    # 将角色与用户和spl_id对应起来
    if spl_id == '' or spl_id is None:
        return render_template('users_create_spl_role.html',
                               error='您必须前往SapperSpl创建prompt后才能提交Spl角色作品！网址:https://www.promptsapper.tech/sappercommunity/workspace')

    spl_role_prompt_data = spl_role_prompt_data_file.read_json()
    # spl_role_prompt_data = {"3124124": {"spl_prompt": "nihfas","spl_data": "fasfa","username": "", "role": ""}}
    # 将spl_role_prompt_data中键为spl_id的值的username设置为username
    spl_role_prompt_data[spl_id]["username"] = username
    # 用random为用户创建的角色随机生成一个role_id
    role_id = ''.join(random.sample(string.ascii_letters + string.digits, 15))
    spl_role_prompt_data[spl_id]["role_id"] = role_id
    spl_role_prompt_data_file.write_json(spl_role_prompt_data)

    # 判断角色是否已经存在，如果存在，返回错误信息
    role_prompt = role_prompt_file.read_json()
    for key, value in role_prompt.items():
        if value['chineseName'] == chineseName:
            return render_template('users_create_spl_role.html', error='AI's name has been registered, please submit another one!')

    # 判断user_work_status中是否有chineseName，如果有，返回错误信息
    for user in users_work_status:
        if chineseName == users_work_status[user]['chineseName']:
            return render_template('users_create_spl_role.html', error='AI's name has been registered, please submit another one!')

    # 保存图片,保存为role_id.png
    file = request.files['file']
    file.filename = role_id + '.png'
    file.save('portal_services/static/images/role/' + file.filename)

    # 保存prompt和图片
    role_prompt[role_id] = {'chineseName': chineseName, 'prompt': prompt, 'helloWord': helloWord}
    role_prompt_file.write_json(role_prompt)

    # 将图片路径存入photo_path
    photo_path = '../static/images/role/' + file.filename
    # 将role,category和chineseName存入user_work_status

    users_work_status[username] = {'role_id': role_id, 'chineseName': chineseName, "category": category,
                                   'status': '您的作品在审核中！', 'statement': '', 'photo_path': photo_path}
    users_work_status_file.write_json(users_work_status)
    return render_template('users_create_spl_role.html', success='您的作品已经提交成功！请等待管理员审核。')


@createUrl.route('/sapper_spl', methods=['POST', 'GET'])
def sapper_spl():
    # print('sapper_spl')
    # data = request.form
    data = request.get_json()
    if data['SPLId'] == '':  # 新建SPL_role
        spl_prompt = data['spl_prompt']
        spl_data = data['spl_data']
        spl_id = ''.join(random.sample(string.ascii_letters + string.digits, 15))
        spl_role_prompt_data = spl_role_prompt_data_file.read_json()
        # spl_role_prompt_data = {"3124124": {"spl_prompt": "nihfas","spl_data": "fasfa","username": "", "role": ""}}
        spl_role_prompt_data[spl_id] = {'spl_prompt': spl_prompt, 'spl_data': spl_data,
                                        'username': session.get('username'), "role_id": ""}
        # print(spl_role_prompt_data)
        spl_role_prompt_data_file.write_json(spl_role_prompt_data)
        return json.dumps({'url': 'https://www.aichain.store/sapper_spl_create?spl_id=' + spl_id})
    else:  # 修改SPL_role
        # 修改spl_role_prompt_data_file中spl_id对应的spl_prompt和spl_data
        spl_id = data['SPLId']
        spl_role_prompt_data = spl_role_prompt_data_file.read_json()
        spl_prompt = data['spl_prompt']
        spl_data = data['spl_data']
        spl_role_prompt_data[spl_id]['spl_prompt'] = spl_prompt
        spl_role_prompt_data[spl_id]['spl_data'] = spl_data
        role_id = spl_role_prompt_data[spl_id]['role_id']
        spl_role_prompt_data_file.write_json(spl_role_prompt_data)
        # 如果spl_id对应的role是否为“”，则说明是修改表单中的spl_prompt和spl_data，用户还没提交作品，不修改role_prompt_file
        if role_id == '':
            return json.dumps({'url': 'https://www.aichain.store/sapper_spl_create?spl_id=' + spl_id})
        else:
            # role不为空，代表AI角色已经创建过了，修改role_prompt_file中role对应的prompt，
            # 这是发布后的作品，需要修改role_prompt_file
            spl_role_prompt_data_file.write_json(spl_role_prompt_data)
            role_prompt = role_prompt_file.read_json()
            for key, value in role_prompt.items():
                if key == role_id:
                    value['prompt'] = spl_prompt
            role_prompt_file.write_json(role_prompt)
            return json.dumps({'code': 200})


@createUrl.route('/sapper_spl_create', methods=['POST', 'GET'])
def sapper_spl_create():
    # 获取url中的spl_prompt和spl_data
    spl_id = request.args.get('spl_id')
    spl_role_prompt_data = spl_role_prompt_data_file.read_json()
    spl_prompt = spl_role_prompt_data[spl_id]['spl_prompt']
    try:
        SPLName = spl_role_prompt_data[spl_id]['spl_data']['SPLName']
        SPLPreInfo = spl_role_prompt_data[spl_id]['spl_data']['SPLPreInfo']
        print('SPLPreInfo:\n', SPLPreInfo)
    except:
        SPLName = ''
        SPLPreInfo = ''
    username = session.get('username')
    if username is None:
        return render_template('users_create_spl_role.html', SPLName=SPLName, spl_prompt=spl_prompt, login_status=False,
                               spl_id=spl_id, SPLPreInfo=SPLPreInfo)
    else:
        return render_template('users_create_spl_role.html', SPLName=SPLName, spl_prompt=spl_prompt, login_status=True,
                               spl_id=spl_id, SPLPreInfo=SPLPreInfo)


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
                all_pass_roles.append(role['role_id'])
    # print('all_pass_roles:', all_pass_roles)
    # all_pass_roles = [{'role': 'translator', 'count': 0, 'count_to_money': 200, 'reward_money': 4.8}, {'role': 'qwe', 'count': 0, 'count_to_money': 200, 'reward_money': 4.8}, {'role': 'rabbit', 'count': 200, 'count_to_money': 0, 'reward_money': 0}]
    spl_role_prompt_data = spl_role_prompt_data_file.read_json()
    spl_pass_roles = {}
    for spl_id in spl_role_prompt_data:
        if spl_role_prompt_data[spl_id]['role_id'] in all_pass_roles:
            spl_pass_roles[spl_id] = spl_role_prompt_data[spl_id]
            # 从for_roleSelect中读取role_id对应的chineseName
            for_roleSelect = for_roleSelect_file.read_json()
            for role_id in for_roleSelect:
                if role_id == spl_role_prompt_data[spl_id]['role_id']:
                    spl_pass_roles[spl_id]['role_id'] = for_roleSelect[role_id]['chineseName']
            # spl_pass_roles = {"3124124": {"spl_prompt": "nihfas", "spl_data": "fasfa","username": "18270182496", "role_id": "zwx"},"31241234": {"spl_prompt": "nihfas","spl_data": "fasfa","username": "18270182496", "role": "qwe"}}
    # 如果spl_pass_roles为空，返回错误信息
    # print('spl_pass_roles:', spl_pass_roles)
    if spl_pass_roles == {}:
        return 'NULL'
    else:
        return spl_pass_roles


@createUrl.route('/sapper_get_spl', methods=['POST', 'GET'])
def sapper_get_spl():
    # print('sapper_get_spl')
    data = request.get_json()
    # print(data)
    spl_id = data['SPLId']
    spl_role_prompt_data = spl_role_prompt_data_file.read_json()
    spl_prompt = spl_role_prompt_data[spl_id]['spl_prompt']
    spl_data = spl_role_prompt_data[spl_id]['spl_data']
    # 将{“spl_prompt”：spl_prompt，“spl_data”：spl_data} return给前端
    return json.dumps({'spl_prompt': spl_prompt, 'spl_data': spl_data})


@createUrl.route('/require2json', methods=['POST', 'GET'])
def Require2Json():
    data = request.get_json()
    print(data)
    jsonData = sapperRequire2json.require2json(data['requirement'])

    return json.dumps({'data': jsonData})


@createUrl.route('/spl2nl', methods=['POST', 'GET'])
def SPL2NL():
    data = request.get_json()
    print(data)
    jsonData = sapperSpl2nl.spl2nl(data['NL'], data['oldSPL'], data['newSPL'])
    return json.dumps({'data': jsonData})

@createUrl.route('/nl2spl',methods = ['POST','GET'])
def NL2SPL():
    data = request.get_json()
    print(data)
    jsonData = sapperNl2spl.nl2spl(data['oldNL'], data['newNL'], data['oldSPL'])
    return json.dumps({'data': jsonData})

@createUrl.route('/formFiller',methods = ['POST','GET'])
def FormFiller():
    data = request.get_json()
    print(data)
    jsonData = sapperForm.form_assit(data['query'], data['form'], data['flag'])
    return json.dumps({'data': jsonData})
