from server import db

class Old_String(db.Model):
    __tablename__ = 'String'
    
    str_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    postfix = db.Column(db.String(200), nullable=True)
    note = db.Column(db.Text, nullable=False)
    
    def __repr__(self):
        return f'<String {self.str_id}>'
    
class Old_String_Language(db.Model):
    __tablename__ = 'String_Language'

    str_id = db.Column(db.Integer, primary_key=True)
    lan_id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    
    def __repr__(self):
        return f'<StringLanguage {self.str_id}, {self.lan_id}>'
    
class Old_Namespace(db.Model):
    __tablename__ = 'Namespace'
    
    namespace_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    app_id = db.Column(db.Integer, nullable=False)
    official_filename = db.Column(db.String(255), nullable=True)
    name = db.Column(db.String(200), nullable=True)
    str_id = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<Namespace {self.namespace_id}, {self.name}>'

class OldApplication(db.Model):
    __tablename__ = 'Application'
    
    app_id = db.Column(db.Integer, primary_key=True)
    platform_id = db.Column(db.Integer, index=True)
    name = db.Column(db.String(32), nullable=False)
    separator = db.Column(db.String(5), nullable=False)
    template = db.Column(db.String(50), nullable=False)
    svn_file = db.Column(db.String(200), nullable=True)
    owner_by = db.Column(db.String(32), nullable=False)
    create_time = db.Column(db.TIMESTAMP, default=db.func.current_timestamp(), nullable=False)
    