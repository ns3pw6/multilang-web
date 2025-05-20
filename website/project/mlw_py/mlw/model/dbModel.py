from server import db

class UserDB(db.Model):
    __tablename__ = 'user'
    __tablename__ = 'user'
    u_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    deleted = db.Column(db.Boolean, default=False, nullable=False)

    
    def __init__(self, name, password, deleted=0):
        self.name = name
        self.password = password
        self.deleted = deleted
    

class Platform(db.Model):
    __tablename__ = 'platform'
    p_id = db.Column(db.Integer, primary_key=True)
    p_name = db.Column(db.String(255), nullable=False, unique=True)
    
    db_platform_application = db.relationship("ApplicationDB", backref="platform")
    

class Separator(db.Model):
    __tablename__ = 'separator'
    sep_id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(15), nullable=False, unique=True) 
    
    db_separator_application = db.relationship("ApplicationDB", backref="separator")


class ApplicationDB(db.Model):
    __tablename__ = 'application'
    app_id = db.Column(db.Integer, primary_key=True)
    p_id = db.Column(db.Integer, db.ForeignKey('platform.p_id'), nullable=False)
    sep_id = db.Column(db.Integer, db.ForeignKey('separator.sep_id'), nullable=False)
    app_name = db.Column(db.String(32), nullable=False)
    svn_file = db.Column(db.String(255), nullable=False)
    template = db.Column(db.String(63), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.u_id'), nullable=False)
    create_time = db.Column(db.Date, default=db.func.current_timestamp(), nullable=False)
    update_time = db.Column(db.DateTime, nullable=False, default='0000-00-00 00:00:00')
    
    db_application_asn = db.relationship("AppString_Namespace", backref="application")
    
    def __init__(self, p_id, sep_id, app_name, svn_file, template, owner_id=6):
        self.p_id = p_id
        self.sep_id = sep_id
        self.app_name = app_name
        self.svn_file = svn_file
        self.template = template
        self.owner_id = owner_id    

class Namespace(db.Model):
    __tablename__ = 'namespace'
    namespace_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True, nullable=False)
    
    db_namespace_asn = db.relationship("AppString_Namespace", backref="namespace")

    def __init__(self, name):
        self.name = name


class LanguageDB(db.Model):
    __tablename__ = 'language'
    lang_id = db.Column(db.Integer, primary_key=True)
    lang_tag = db.Column(db.String(15), nullable=False)
    lang_name = db.Column(db.String(31), nullable=False, unique=True)
    chinese_name = db.Column(db.String(64), nullable=False)
    
    db_language_stringLanguage = db.relationship("StringLanguage", backref="language")
    db_language_string_update_log = db.relationship("String_Update_Log", backref="language")


class String(db.Model):
    __tablename__ = 'string'
    str_id = db.Column(db.Integer, primary_key=True)
    postfix = db.Column(db.String(255), nullable=False)
    note = db.Column(db.String, default=None)
    
    db_string_stringLanguage = db.relationship("StringLanguage", backref="string")
    db_string_namespace = db.relationship("AppString_Namespace", backref="string")
    db_string_update_log = db.relationship("String_Update_Log", backref="string")


class StringLanguage(db.Model):
    __tablename__ = 'string_language'
    sl_id = db.Column(db.Integer, primary_key=True)
    str_id = db.Column(db.Integer, db.ForeignKey('string.str_id'), nullable=False)
    lang_id = db.Column(db.Integer, db.ForeignKey('language.lang_id'), nullable=False)
    content = db.Column(db.String)
    
    def __init__(self, str_id, lang_id, content):
        self.str_id = str_id
        self.lang_id = lang_id
        self.content = content


class AppString_Namespace(db.Model):
    __tablename__ = 'appstring_namespace'
    asn_id = db.Column(db.Integer, primary_key=True)
    app_id = db.Column(db.Integer, db.ForeignKey('application.app_id'), nullable=False)
    str_id = db.Column(db.Integer, db.ForeignKey('string.str_id'), nullable=False)
    namespace_id = db.Column(db.Integer, db.ForeignKey('namespace.namespace_id'), nullable=False)
    deleted = db.Column(db.Boolean, default=0, nullable=False)

    def __init__(self, app_id, str_id, namespace_id):
        self.app_id = app_id
        self.str_id = str_id
        self.namespace_id = namespace_id
        

class String_Update_Log(db.Model):
    __tablename__ = 'string_update_log'
    l_id = db.Column(db.Integer, primary_key=True)
    lang_id = db.Column(db.Integer, db.ForeignKey('language.lang_id'), nullable=False)
    str_id = db.Column(db.Integer, db.ForeignKey('string.str_id'), nullable=False)
    old_value = db.Column(db.String)
    new_value = db.Column(db.String)
    deleted = db.Column(db.Integer, nullable=False, default=0)
    updated_time = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    
    def __init__(self, lang_id, str_id, old_value, new_value):
        self.lang_id = lang_id
        self.str_id = str_id
        self.old_value = old_value
        self.new_value = new_value


class Action_Type(db.Model):
    __tablename__ = 'action_type'
    type_id = db.Column(db.Integer, primary_key=True)
    type_name = db.Column(db.String(200), nullable=False, unique=True)

    db_ACTION_LOG = db.relationship("LogDB", backref="action_type")


class LogDB(db.Model):
    __tablename__ = 'log'
    log_id = db.Column(db.Integer, primary_key=True)
    u_id = db.Column(db.Integer, db.ForeignKey('user.u_id'))
    type_id = db.Column(db.Integer, db.ForeignKey('action_type.type_id'))
    log = db.Column(db.String, nullable=False)
    time = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    
    def __init__(self, u_id, type_id, log):
        self.u_id = u_id
        self.type_id = type_id
        self.log = log
        
class ProofreadProject(db.Model):
    __tablename__ = 'proofread_project'

    project_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    project_name = db.Column(db.Text, nullable=False)
    spec_link = db.Column(db.Text, nullable=False)
    person_in_charge = db.Column(db.Integer, db.ForeignKey('user.u_id'), nullable=False)
    reviewer = db.Column(db.Integer, db.ForeignKey('user.u_id'), default=None)
    deleted = db.Column(db.Integer, default=0)
    
    db_proofread_progject_string = db.relationship("ProofreadString", backref="proofread_project")
    
    person_in_charge_user = db.relationship("UserDB", backref=db.backref('person_in_charge_user', lazy=True), foreign_keys=[person_in_charge])
    reviewer_user = db.relationship("UserDB", backref=db.backref('reviewer_projects', lazy=True), foreign_keys=[reviewer])

    def __init__(self, project_name, spec_link, person_in_charge):
        self.project_name = project_name
        self.spec_link = spec_link
        self.person_in_charge = person_in_charge


class ProofreadString(db.Model):
    __tablename__ = 'proofread_string'

    ps_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    project_id = db.Column(db.Integer, db.ForeignKey('proofread_project.project_id'), nullable=False)
    string = db.Column(db.Text, nullable=False)
    deleted = db.Column(db.Integer, default=0)
    
    def __init__(self, project_id, string):
        self.project_id = project_id
        self.string = string
    

class ProofreadLog(db.Model):
    __tablename__ = 'proofread_log'

    log_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    u_id = db.Column(db.Integer, db.ForeignKey('user.u_id'), nullable=False)
    action = db.Column(db.Integer, db.ForeignKey('action_type.type_id'), nullable=False)
    ps_id = db.Column(db.Integer, db.ForeignKey('proofread_string.ps_id'), nullable=False)
    old_string = db.Column(db.Text, default=None)
    new_string = db.Column(db.Text, default=None)
    time = db.Column(db.TIMESTAMP, nullable=False, default=db.func.current_timestamp())
    
    proofread_string = db.relationship("ProofreadString", backref=db.backref('proofread_logs', lazy=True), foreign_keys=[ps_id])
    log_type = db.relationship("Action_Type", backref=db.backref('action_types', lazy=True), foreign_keys=[action])
    person_recorded = db.relationship("UserDB", backref=db.backref('person_recorded', lazy=True), foreign_keys=[u_id])


class Updated(db.Model):
    __tablename__ = 'updated'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    string_update_time = db.Column(db.TIMESTAMP, nullable=False, default=db.func.current_timestamp())
    still_caching = db.Column(db.Integer, nullable=False, default=0)
