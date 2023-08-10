from flask import request, session, Blueprint, render_template

from portal_services.services.JsonSelfDifin import JsonFile
from portal_services.services.authentic_login import auth

users_rolesUrl = Blueprint('users_rolesUrl', __name__)

spl_role_prompt_data_file = JsonFile('../forms/spl_role_prompt_data.json')
users_pass_work_file = JsonFile('../forms/users_pass_work.json')
for_roleSelect_file = JsonFile('../forms/for_roleSelection_show.json')


@users_rolesUrl.route('/showMyRoles', methods=['POST', 'GET'])
@auth
def showMyRoles():
    # {"fasfasfwe": { "chineseName": "助手", "helloWord": "你好" , "spl_prompt": "我是机器人", "role_id": "zwx"}, "fasfasfwe": { "chineseName": "助手", "helloWord": "你好" , "spl_prompt": "我是机器人"}}
    username = session.get('username')
    users_pass_work = users_pass_work_file.read_json()
    all_pass_roles = []
    for user in users_pass_work:
        if user == username:
            for role in users_pass_work[user]:
                all_pass_roles.append(role['role_id'])
    # print('all_pass_roles:', all_pass_roles)
    # all_pass_roles = [{'role_id': 'translator', "chineseName": "雅思口语", 'count': 0, 'count_to_money': 200, 'reward_money': 4.8}, {'role_id': 'qwe', 'count': 0, 'count_to_money': 200, 'reward_money': 4.8}, {'role': 'rabbit', 'count': 200, 'count_to_money': 0, 'reward_money': 0}]
    spl_role_prompt_data = spl_role_prompt_data_file.read_json()
    spl_pass_roles = {}
    for spl_id in spl_role_prompt_data:
        if spl_role_prompt_data[spl_id]['role_id'] in all_pass_roles: # 用户有通过的spl角色
            spl_pass_roles[spl_id] = spl_role_prompt_data[spl_id]
            # 从for_roleSelect中读取role_id对应的chineseName
            for_roleSelect = for_roleSelect_file.read_json()
            for role_id in for_roleSelect:
                if role_id == spl_role_prompt_data[spl_id]['role_id']:
                    spl_pass_roles[spl_id]['chineseName'] = for_roleSelect[role_id]['chineseName']
                    spl_pass_roles[spl_id]['helloWord'] = for_roleSelect[role_id]['helloWord']
                    spl_pass_roles[spl_id]['category'] = for_roleSelect[role_id]['category']
    # 如果spl_pass_roles为空，返回错误信息
    # 删除spl_pass_roles中的spl_data
    for spl_id in spl_pass_roles:
        spl_pass_roles[spl_id].pop('spl_data')
    if spl_pass_roles == {}:
        return render_template('users_roles.html', has_roles=False, login_status=True)
    else:
        return render_template('users_roles.html', has_roles=True, spl_pass_roles=spl_pass_roles, login_status=True)
