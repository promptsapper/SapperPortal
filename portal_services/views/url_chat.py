from flask import request, session, Blueprint

from portal_services.services.response import Answer

from portal_services.services.authentic_login import auth

chatUrl = Blueprint('chatUrl', __name__)


@chatUrl.route('/chat/<role_id>', methods=['POST', 'GET'])
@auth
def chat(role_id):
    '''
    role在路由传
    ajax——data:{
                'query': "你好"
                'history_id': 'history_1',
                'new_old': 'new'
            }
    return:"你好，请问能帮助你什么" 或者 “[DONE]”
    '''
    session_user = session.get('username')
    from_font = request.args  # 获取前端传来的数据,get
    # print("query", from_font['query'])
    print("接收到用户输入:", from_font["query"])
    response = Answer(from_font, session_user, role_id)
    print("GPT回答:", response)
    return response
