from functools import wraps
from flask import session, redirect, url_for, jsonify
from model.user import User

def check_permission():
    """Decorator to check user permission."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            username = session.get('username')
            if not username:
                return redirect(url_for('login_bp.login'))
            user = User.check_user_auth(username=username)
            if user is None:
                return jsonify({'error': f'目前使用者{username}無權限，請通知管理員需要修改權限!'}), 403
            return func(*args, **kwargs)
        return wrapper
    return decorator