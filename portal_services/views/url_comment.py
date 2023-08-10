import json

from flask import request, session, Blueprint, render_template, Response
from portal_services.services.authentic_login import auth
from portal_services.services.JsonSelfDifin import JsonFile

commentUrl = Blueprint('commentUrl', __name__)
role_comment_list_file = JsonFile('../forms/role_comments_list.json')
for_roleSelect_show_file = JsonFile('../forms/for_roleSelection_show.json')

@commentUrl.route('/chatComment/<role_id>', methods=['POST', 'GET'])
@auth
def chatcomment(role_id):
    session_user = session.get('username')
    from_font = request.args
    print("query", from_font['comments'])
    write_comment(from_font['comments'], session_user, role_id)
    return Response("success", content_type='text/event-stream')


def write_comment(newComment, username, role_id):
    comment_list = role_comment_list_file.read_json()
    has_user_role = False
    if role_id in comment_list:
        has_user_role = True
        comment_list[role_id].append({"user": username, "comment": newComment, "likes": 0, "reply": []})
        role_comment_list_file.write_json(comment_list)
    if not has_user_role:
        newUserComment = {
            role_id: [{"user": username, "comment": newComment, "likes": 0, "reply": []}]
        }
        print("newUserComment:", newUserComment)
        comment_list.update(newUserComment)
        role_comment_list_file.write_json(comment_list)


@commentUrl.route('/comments/show', methods=['POST', 'GET'])
def commentshow():
    role_comments_list = role_comment_list_file.read_json()
    role = request.form['role']
    print("role:", role)
    # 如果role_comments_list[role]存在，返回role_comments_list[role]，否则返回空列表
    if role in role_comments_list:
        response = {"comments": role_comments_list[role]}
        print("response:", response)
        return json.dumps(response)
    else:
        response = {"comments": []}
        return json.dumps(response)

@commentUrl.route('/comment/<role_id>', methods=['GET', 'POST'])
@auth
def comment(role_id):
    for_roleSelect_show = for_roleSelect_show_file.read_json()
    chineseName = ''
    for key, value in for_roleSelect_show.items():
        if key == role_id:
            chineseName = value['chineseName']
            break
    username = session.get('username')
    return render_template('comment.html', role_id=role_id, chineseName=chineseName, username=username, login_status=True)

@commentUrl.route('/comment_edit/<role_id>', methods=['GET', 'POST'])
@auth
def comment_edit(role_id):
    from_font = request.args
    print("likes:", from_font['likes'], "who:", from_font['who'])
    write_likes(from_font['likes'], from_font['who'], role_id, from_font['comment'])
    return Response("success", content_type='text/event-stream')

def write_likes(newLikes, username, role_id,comment):
    comment_list = role_comment_list_file.read_json()
    for user in comment_list[role_id]:
        if user['user'] == username and user['comment'] == comment:
            user['likes'] = newLikes
            print("user:", user, "newLikes:", newLikes)
            break
    role_comment_list_file.write_json(comment_list)
    print("write_likes success")

@commentUrl.route('/comment_delete/<role_id>', methods=['GET', 'POST'])
@auth
def comment_delete(role_id):
    from_font = request.args
    print("comment:", from_font['comment'], "who:", from_font['who'])
    write_delete(from_font['comment'], from_font['who'], role_id)
    return Response("success", content_type='text/event-stream')

def write_delete(newDelete, username, role_id):
    comment_list = role_comment_list_file.read_json()
    for user in comment_list[role_id]:
        if user['user'] == username and user['comment'] == newDelete:
            comment_list[role_id].remove(user)
            break
    role_comment_list_file.write_json(comment_list)
    print("write_delete success")