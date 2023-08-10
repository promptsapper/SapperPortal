import json
import datetime
import flask
import openai
import sys
import traceback
import re
from .JsonSelfDifin import JsonFile

users_file = JsonFile('../forms/users_pwd_tokens.json')
history_file = JsonFile('../forms/history.json')
role_use_count_file = JsonFile('../forms/role_use_count.json')
role_prompt_file = JsonFile('../forms/role_system_prompt.json')
api_key_file = JsonFile('../forms/api_key.json')
users_pass_work_file = JsonFile('../forms/users_pass_work.json')


def Answer(from_font, session_user, role_id):

    balance_tokens = 0
    users = users_file.read_json()
    username = session_user
    for user in users:
        if user["user"] == username:
            balance_tokens = user["tokens"]
            if balance_tokens < 0:
                return "使用次数不足"

    data_dict = role_prompt_file.read_json()
    system_prompt = ''
    for key, value in data_dict.items():
        if key == role_id:
            system_prompt = value["prompt"]
            chineseName = value["chineseName"]
            break
    system_prompt = [
        {"role": "system", "content": system_prompt}
    ]
    prompt_chat_history = merge_prompt(from_font, username, role_id)
    try:
        system_prompt.extend(prompt_chat_history)

        def stream():
            response = chatgpt(system_prompt)
            answer = ''
            for chunk in response:
                if chunk["choices"][0]["finish_reason"] is not None:
                    print("GPT回答结束")
                    data = "[DONE]"

                    write_role_count(role_id, username)
                    write_balance_tokens(username, balance_tokens)
                    write_bill(username, role_id, chineseName)
                    write_history(prompt_chat_history, username, role_id, from_font, answer)

                else:
                    data = chunk["choices"][0]["delta"].get("content", "")
                    answer += data
                yield "data: %s\n\n" % data.replace("\n", "<br>")

        stream()
        return flask.Response(stream(), mimetype='text/event-stream')

    except:
        return "Error"


def chatgpt(system_prompt):
    key_json = api_key_file.read_json()
    openai.api_key = key_json["api_key"]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=system_prompt,
        stream=True
    )
    return response


def write_history(prompt_file, username, role_id, from_font, answer):
    # 查找历史文件中的用户,找到对应的历史记录，将新的记录覆盖旧的记录
    current_history = prompt_file
    current_history.extend([{"role": "assistant", "content": answer}])  # 这就是加上这次模型回答的历史记录
    has_user_role = False
    has_history_id = False
    history = history_file.read_json()
    for user in history:
        if user["user"] == username and user["role"] == role_id:
            has_user_role = True
            # 如果user["history" ]为空，直接赋值
            if not user["history"]:
                user["history"].append(
                    {"history_id": from_font["history_id"], "content": current_history})
                history_file.write_json(history)
            else:  # 用户有历史记录，覆盖旧的记录
                for record in user["history"]:
                    if record["history_id"] == from_font["history_id"]:
                        has_history_id = True
                        record["content"] = current_history
                        history_file.write_json(history)
                        break
                if not has_history_id:
                    user["history"].append(
                        {"history_id": from_font["history_id"], "content": current_history})
                    history_file.write_json(history)
    # 如果没找到，将用户和对应角色加入历史记录
    if not has_user_role:
        new_user = {"user": username, "role": role_id, "history": [
            {"history_id": from_font["history_id"], "content": current_history}]}
        # 把new_history加入history
        history.append(new_user)
        # 保存历史记录到文件
        history_file.write_json(history)


def merge_prompt(from_font, username, role_id):
    prompt_file = []
    if from_font["new_old"] == 'new':
        # 如果是新的对话，将from_font["query"]写入prompt
        prompt_file.extend([{"role": "user", "content": from_font["query"]}])
    else:
        # 如果是旧的对话，将history_prompt写入prompt
        # 根据session_user找history.json中的user；
        history = history_file.read_json()
        history_prompt = []
        for user in history:
            if user["user"] == username and user["role"] == role_id:
                # 找到对应from_font['history_id']在文件中的历史记录
                for history_id in user["history"]:
                    if history_id["history_id"] == from_font["history_id"]:
                        history_prompt = history_id["content"]
        prompt_file.extend(history_prompt)
        prompt_file.extend([{"role": "user", "content": from_font["query"]}])
    return prompt_file


def write_role_count(role_id, username):
    role_use_count = role_use_count_file.read_json()
    for role_count in role_use_count:
        if role_count["role_id"] == role_id:
            role_count["count"] = role_count["count"] + 1
            role_use_count_file.write_json(role_use_count)
            break

    # users_pass_work_file写入角色使用次数加一,为了实现奖励机制
    users_pass_work = users_pass_work_file.read_json()
    for user in users_pass_work:
        if user == username:
            for user_role in users_pass_work[user]:
                if user_role["role_id"] == role_id:
                    user_role["count"] = str(int(user_role["count"]) + 1)
                    users_pass_work_file.write_json(users_pass_work)
                    break


def write_balance_tokens(username, balance_tokens):
    # 从这里开始存聊天内容等存文件操作
    # 用户的balance_tokens减去当前聊天消耗的tokens，写入文件
    users = users_file.read_json()
    for _user in users:
        if _user["user"] == username:
            _user["tokens"] = balance_tokens - 1
            # print("user_tokens:", _user["tokens"])
            users_file.write_json(users)


def write_bill(username, role_id, chineseName):
    # 存入用户账单，'portal_services/forms/users_bill/{username}_bill.json'
    with open(f'portal_services/forms/users_bill/{username}_bill.json', 'r', encoding='utf-8') as f:
        user_bill = json.load(f)
    # 判断今天是否有值
    today = datetime.date.today()
    today = str(today)
    if today in user_bill:
        # 判断今天是否有role
        if role_id in user_bill[today]:
            user_bill[today]["chineseName"] = user_bill[today]["chineseName"] + 1
        else:
            user_bill[today] = {"chineseName": 1}
    else:
        user_bill[today] = {"chineseName": 1}
    # 写入用户账单
    with open(f'portal_services/forms/users_bill/{username}_bill.json', 'w', encoding='utf-8') as f:
        json.dump(user_bill, f, ensure_ascii=False)
