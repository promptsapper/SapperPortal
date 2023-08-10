from flask import Blueprint, render_template, session, request
from ..services.JsonSelfDifin import JsonFile
from portal_services.services.authentic_login import auth

selectUrl = Blueprint('selectUrl', __name__)
for_roleSelect_show_file = JsonFile('../forms/for_roleSelection_show.json')
users_pass_work_file = JsonFile('../forms/users_pass_work.json')


@selectUrl.route('/roleSelect/', methods=['GET', 'POST'])
@auth
def roleSelect():
    return render_template('roleSelection.html', login_status=True)


@selectUrl.route('/select/show', methods=['GET', 'POST'])
def show():
    category = request.form.get('category')
    all_roles = for_roleSelect_show_file.read_json()
    for_roleSelect_show = {}
    if category == 'all':
        for key, value in all_roles.items():
            for_roleSelect_show[key] = value['chineseName']
    else:
        for key, value in all_roles.items():
            if value['category'] == category:
                for_roleSelect_show[key] = value['chineseName']
    return for_roleSelect_show


@selectUrl.route('/select/<role_id>', methods=['GET', 'POST'])
@auth
def select(role_id):
    for_roleSelect_show = for_roleSelect_show_file.read_json()
    chineseName = ''
    for key, value in for_roleSelect_show.items():
        if key == role_id:
            chineseName = value['chineseName']
            break
    username = session.get('username')
    for_roleSelect_show = for_roleSelect_show_file.read_json()
    helloWord = for_roleSelect_show[role_id]['helloWord']
    return render_template('chat.html', role_id=role_id, chineseName=chineseName, username=username, login_status=True, helloWord=helloWord)


@selectUrl.route('/user_view_own_roles', methods=['GET', 'POST'])
@auth
def user_view_own_roles():
    username = session.get('username')
    # print('username', username)
    users_pass_work = users_pass_work_file.read_json()
    # print('users_pass_work', users_pass_work)
    user_roles = "NULL"
    for user in users_pass_work:
        if user == username:
            user_roles = users_pass_work[user]
            # print('user_roles', user_roles)
            # user_roles = [{"role": "test", "count": 10, "count_to_money": 200, "reward_money": 5}]
            break
    # print('user_roles', user_roles)
    return user_roles
