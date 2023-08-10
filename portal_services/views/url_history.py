import json

from flask import request, session, Blueprint
from portal_services.services.history import show_history_list, find_single_history, single_history_delete


historyUrl = Blueprint('historyUrl', __name__)


@historyUrl.route('/history_list', methods=['GET', 'POST'])
def history():
    user = session.get('username')
    print("42行：user:", user)
    '''
    ajax——data: {”user“: ”666“}
    :return: {
                "history": [
                              {"1":[
                                          {"role": "user","content": "你好"},
                                          {"role": "assistant", "content": "你好，我是小助手，有什么可以帮到你的吗？"}
                              ]},
                              {"2": [
                                          {"role": "user","content": "你好"},
                                          {"role": "assistant", "content": "你好，我是小助手，有什么可以帮到你的吗？"}
                              ]}
                              ]
              }
    '''
    # user = request.form['user']
    role = request.form['role']
    # print("user:", user)
    response = show_history_list(user, role)
    return json.dumps(response)


@historyUrl.route('/single_history', methods=['GET', 'POST'])
def single_history():
    user = session.get('username')
    '''
    ajax——data: {”user“: ”666“, "history_id": "1"}
    :return:{ "single_history":
                [
                   {"role": "user","content": "你好"},
                    {"role": "assistant", "content": "你好，我是小助手，有什么可以帮到你的吗？"}
                 ]
            }
    '''
    # user = request.form['user']
    history_id = request.form['history_id']
    role = request.form['role']
    # print("user:", user)
    # print("history_id:", history_id)
    response = find_single_history(user, role, history_id)
    return json.dumps(response)


@historyUrl.route('/history_edit', methods=['POST', 'GET'])
def history_edit():
    data = request.form
    username = session.get('username')
    single_history_delete(username, data['role'], data['history_id'])
    return "success"
