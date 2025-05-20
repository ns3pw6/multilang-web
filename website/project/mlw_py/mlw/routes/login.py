from flask import render_template, session, redirect, request, url_for
from server import app, logger
from model.user import User
from utility.session_utils import check_session, remove_session
from flask_bcrypt import Bcrypt
from . import login_bp

@login_bp.route('/login/', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        error = None
        username = request.form['username']
        password = request.form['password'].encode('utf-8')
        bcrypt = Bcrypt()
        # hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        # logger.error(f"hashed_pw: {hashed_pw}")
        if not username:
            error = "請輸入帳號!"
        elif not password:
            error = "請輸入密碼!"

        if error is not None:
            return render_template('pages/login.html', error = error)
        
        hashed_pwd = User.get_user_pwd(username)
        if not hashed_pwd:
            return render_template('pages/login.html', error = "帳號或密碼錯誤!!")
        
        if bcrypt.check_password_hash(hashed_pwd, password):
            session['username'] = username
            return redirect(app.config['BASE_URL'])
        else:
            return render_template('pages/login.html', error = "帳號或密碼錯誤!!")
    else:
        if check_session():
            return redirect(app.config['BASE_URL'])
        
    return render_template('pages/login.html')


@login_bp.route('/logout/', methods=['GET'])
def logout():
    remove_session()
    return redirect(url_for('login_bp.login'))
