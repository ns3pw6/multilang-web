from model.dbModel import ApplicationDB

class Application(ApplicationDB):
    
    @classmethod
    def get_all_apps(cls, p_id):
        return cls.query.filter_by(p_id = p_id).all()
    
    @classmethod
    def get_app_info(cls, app_id):
        app = cls.query.filter_by(app_id = app_id).first()
        return app

    @classmethod
    def check_svn_path(cls, svn_file, template, app_id = None):
        query = cls.query.filter_by(svn_file = svn_file, template = template) \
                         .filter(cls.app_id != app_id) \
                         .first()

        return query if query is not None else False
    
    @classmethod
    def get_app_id(cls, start_time, end_time):
        query = cls.query.filter(cls.create_time.between(start_time, end_time))
        
        return [item.app_id for item in query] if query else False
