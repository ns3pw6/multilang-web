from flask import session

def check_session() -> bool:
    return 'username' in session

def remove_session() -> None:
    session.pop('username', None)