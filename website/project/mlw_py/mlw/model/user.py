from model.dbModel import UserDB

class User(UserDB):
    
    @classmethod
    def check_user_auth(cls, username):
        user = cls.query.filter_by(name=username, deleted=0).first()
        return user
    
    @classmethod
    def get_user_id(cls, username):
        query = cls.query.filter_by(name=username).first()
        if not query:
            return False
        user_id = query.u_id
        return user_id
    
    @classmethod
    def get_user_pwd(cls, username):
        query = cls.query.filter_by(name=username).first()
        if not query:
            return False
        return query.password