from flask import Blueprint, session, render_template
from portal_services.services.JsonSelfDifin import JsonFile
from portal_services.services.authentic_login import auth

balance = Blueprint('balance', __name__)


@balance.route('/get_tokens', methods=['POST', 'GET'])
def get_tokens():
    username = session.get('username')
    user_tokens = JsonFile('../forms/users_pwd_tokens.json')
    tokens = user_tokens.read_json()
    for user in tokens:
        if user['user'] == username:
            return {'tokens': user['tokens']}


@balance.route('/get_bill', methods=['POST', 'GET'])
def get_bill():
    # print('get-bill')
    username = session.get('username')
    user_bill = JsonFile(f'../forms/users_bill/{username}_bill.json')
    bill = user_bill.read_json()
    # print(bill)
    return {"bill": bill}


@balance.route('/recharge', methods=['POST', 'GET'])
@auth
def recharge():
    return render_template('recharge.html', login_status=True)
