from model.dbModel import String, StringLanguage, Namespace, AppString_Namespace, ApplicationDB
from model.old_dbModel import Old_String, Old_String_Language, Old_Namespace, OldApplication
from model.separator import SeparatorModel
from server import db
from flask import jsonify
import sys

class StringMigrate():
    def __init__(self):
        pass
    
    def transferString(self):
        try:
            print('Start to transfer string table.', file=sys.stderr)
            self.migrate_string()
            print('End of transferring string table.', file=sys.stderr)
            
            print('Start to transfer string language table.', file=sys.stderr)
            self.migrate_string_language()
            print('End of transferring string language table.', file=sys.stderr)
            
            print('Start to transfer application table.', file=sys.stderr)
            new_app_ids = self.migrate_app()
            print('End of transferring application table.', file=sys.stderr)

            print('Start to transfer old namespace table to new namespace and appstring_namespace table.', file=sys.stderr)
            self.migrate_namespace(new_app_ids)
            print('End of transferring old namespace table to new namespace and appstring_namespace table.', file=sys.stderr)

            return jsonify({"status": "success", "message": "字串搬移成功"}), 200

        except Exception as e:
            print(e, file=sys.stderr)
            db.session.rollback()
            return jsonify({"status": "error", "message": "字串搬移失敗"}), 500

    def migrate_string(self):
        new_string_list = []

        query_old_String = Old_String.query.all()
        for item in query_old_String:
            if item.postfix == None:
                continue
            new_string = String(item.str_id, item.postfix) if item.note is '' else String(item.str_id, item.postfix, item.note)
            new_string_list.append(new_string)

        db.session.bulk_save_objects(new_string_list)
        db.session.commit()

    def migrate_string_language(self):
        new_string_language_list = []

        query_old_String_Language = Old_String_Language.query.all()
        for item in query_old_String_Language:
            string_language = StringLanguage(item.str_id, item.lan_id, item.content)
            new_string_language_list.append(string_language)
            
        db.session.bulk_save_objects(new_string_language_list)
        db.session.commit()

    def migrate_app(self):
        new_app_ids = {}
        
        query_old_application = OldApplication.query.all()
        for old_application in query_old_application:
            # skip official app
            if not old_application.template:
                continue
            
            svn_file = None if not old_application.svn_file or old_application.svn_file == '' else old_application.svn_file
            template = old_application.template
            create_date = (old_application.create_time).date()
            if old_application.svn_file:
                path = old_application.svn_file + old_application.template
                file_format = old_application.template.rsplit('.', 1)[-1]
                svn_file, template = path.rsplit('/', 1)
                svn_file += '/'
            new_app = ApplicationDB(
                p_id=old_application.platform_id,
                sep_id=SeparatorModel().get_sep_type(old_application.platform_id, file_format),
                app_name=old_application.name,
                svn_file=svn_file,
                template=template,
                owner_id=6,
                create_time=create_date
            )
            db.session.add(new_app)
            db.session.flush()
            new_app_ids[old_application.app_id] = new_app.app_id
            
        db.session.commit()
        return new_app_ids

    def migrate_namespace(self, new_app_ids):
        new_namespace_ids = {}
        seen_names = set()
        new_appstring_namespace = []
        
        query_old_Namespace = Old_Namespace().query.all()
        for old_namespace in query_old_Namespace:
            if old_namespace.app_id not in new_app_ids:
                continue
            
            if old_namespace.name not in seen_names:
                new_namespace = Namespace(
                    name=old_namespace.name
                )
                db.session.add(new_namespace)
                db.session.flush()
                
                new_namespace_ids[old_namespace.name] = new_namespace.namespace_id
                seen_names.add(old_namespace.name)
                
            appstring_entry = AppString_Namespace(
                app_id=new_app_ids[old_namespace.app_id],
                str_id=old_namespace.str_id,
                namespace_id=new_namespace_ids[old_namespace.name],
            )
            
            new_appstring_namespace.append(appstring_entry)

        db.session.bulk_save_objects(new_appstring_namespace)
        db.session.commit()
