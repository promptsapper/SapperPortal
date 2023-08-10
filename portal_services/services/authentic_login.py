import functools

from flask import session, render_template, request, redirect


def auth(func):
    @functools.wraps(func)  # 保留原函数的元信息, 如函数名, 参数列表等
    def inner(*args, **kwargs):
        # 判断session中是否有username
        username = session.get('username')

        # print(username)
        if username:
            return func(*args, **kwargs)
        else:
            return redirect('/login')

    return inner


def get_spl(func):
    @functools.wraps(func)  # 保留原函数的元信息, 如函数名, 参数列表等
    def inner(*args, **kwargs):
        # 前端传过来的数据
        # data = request.form
        data = request.get_json()
        print('data', data)
        spl_prompt = data['spl_prompt']
        spl_data = data['spl_data']
        # 将spl_prompt和spl_data存入session
        session['spl_prompt'] = spl_prompt
        session['spl_data'] = spl_data
        # 取出session中的spl_prompt和spl_data
        session_spl_prompt = session.get('spl_prompt')
        session_spl_data = session.get('spl_data')
        print("session", session_spl_prompt, session_spl_data)
        return func(*args, **kwargs)
    return inner
