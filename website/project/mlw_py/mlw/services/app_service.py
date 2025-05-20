from flask import jsonify, Response, session
from server import db, logger
from utility.svn_utils import check_svn_correctness
from model.separator import SeparatorModel
from model.application import Application
from model.dbModel import Action_Type, Platform
from model.log import Log
from model.user import User
from typing import Tuple, Dict
from sqlalchemy.exc import SQLAlchemyError

class AppService():
    
    def __init__(self) -> None:
        pass
    
    @staticmethod
    def __validate_app_data(data: Dict) -> Tuple[bool, str | None]:
        """Validate if all required fields are present in the request data."""
        required_fields = ['platform_id', 'app_name', 'svn_file', 'template']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return False, f'Missing fields: {", ".join(missing_fields)}'
        return True, None

    @staticmethod
    def __check_svn_path(svn_file: str, template: str, app_id: int) -> Tuple[bool, str | None, str | None]:
        """Check if the svn_file and template combination already exists in the database."""
        correctness = check_svn_correctness(svn_file, template)
        if correctness != True:
            return True, 'svn path error', None
        
        exists = Application.check_svn_path(svn_file=svn_file, template=template, app_id=app_id)
        if exists:
            return True, 'svn_file + template duplicate', exists.app_name
        return False, None, None

    @staticmethod
    def __get_sep_id(platform_id: int, template: str) -> int:
        """Get the separator ID based on platform ID and template file format."""
        file_format = template.rsplit('.', 1)[-1]
        return SeparatorModel().get_sep_type(platform_id, file_format)

    def __build_log(self, type_name: str, data: Dict):
        """get log type_id and format log content"""
        platform = Platform.query.filter_by(p_id=data['platform_id']).first().p_name
        log_content = f'App: {data['app_name']} <br> Platform: {platform} <br> Svn_file: {data['svn_file']} <br> Template: {data['template']}'
        type_id = Action_Type.query.filter_by(type_name=type_name).first().type_id
        
        return type_id, log_content

    def __handle_request_errors(self, data: Dict, app_id: int = None) -> Tuple:
        """Handle errors related to app data validation, SVN path check, and user authentication."""
        is_valid, error_message = self.__validate_app_data(data)
        if not is_valid:
            return jsonify({'msg': error_message}), 400

        svn_error, error_message, app_name = self.__check_svn_path(data['svn_file'], data['template'], app_id)
        if svn_error:
            return jsonify({'msg': error_message, 'app_name': app_name}), 400

        return None, 200
    
    def __handle_test_mode(self, action: str, data: Dict) -> Response:
        """Handle test mode for app creation and update."""
        return jsonify({
            'msg': 'success',
            'test_msg': f'測試模式預覽{action}資訊如下:<br>App: {data["app_name"]}<br>svn路徑: {data["svn_file"]}<br>template: {data["template"]}',
            'test_mode': True,
        }), 200
    
    def get_all_apps(self, p_id) -> Response:
        """Get apps by selected platform."""
        data = {}
        
        try:
            apps = Application.get_all_apps(p_id)
            if not apps:
                return jsonify({'msg': 'No Apps!'}), 404
            for app in apps:
                data[app.app_id] = app.app_name
            
            return jsonify(data), 200
        except Exception as e:
            logger.error(f"Error fetching apps for platform ID {p_id}: {e}")
            return jsonify(str(e)), 500
        
    def get_app_info(self, app_id: int) -> Response:
        """Get app SVN path and template."""
        app = Application.get_app_info(app_id)
        if not app:
            return jsonify({'msg': 'App not found'}), 404

        data = {
            'app_id': app.app_id,
            'app_name': app.app_name,
            'svn_file': app.svn_file,
            'template': app.template,
        }

        return jsonify(data), 200
    
    def update_app(self, data: Dict) -> Response:
        """Update app info in the database."""
        error_response, status_code = self.__handle_request_errors(data, data['app_id'])
        if error_response:
            return error_response, status_code

        sep_id = self.__get_sep_id(data['platform_id'], data['template'])
        test_mode = session.get('test_mode')
        if test_mode:
            return self.__handle_test_mode("更新", data)

        try:
            app = Application.get_app_info(data['app_id'])
            if app is None:
                return jsonify({'msg': 'App not found'}), 404

            app.p_id = data['platform_id']
            app.sep_id = sep_id
            app.app_name = data['app_name']
            app.svn_file = data['svn_file']
            app.template = data['template']
            
            type_id, log = self.__build_log('Update', data)
            user_id = User.get_user_id(session.get('username'))
            result = Log.insert(u_id=user_id, type_id=type_id, log=log)
            if result:
                return jsonify({
                    'msg': result, 
                    'test_mode': session.get('test_mode'),
                }), 500
            
            db.session.commit()
            return jsonify({'msg': 'success'}), 200
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Database error occurred while updating app: {e}")
            return jsonify({'msg': 'Database error occurred, please try again later.'}), 500
        
        except Exception as e:
            db.session.rollback()
            logger.error(f"Unexpected error occurred: {e}")
            return jsonify({'msg': 'An unexpected error occurred, please try again later.'}), 500
        
    def create_app(self, data: Dict) -> Response:
        """Insert a new app into the database."""
        error_response, status_code = self.__handle_request_errors(data)
        if error_response:
            return error_response, status_code
        
        sep_id = self.__get_sep_id(data['platform_id'], data['template'])
        user_id = User.get_user_id(session.get('username'))
        
        test_mode = session.get('test_mode')
        if test_mode:
            return self.__handle_test_mode("新增", data)
        
        try:
            app = Application(
                p_id=data['platform_id'],
                sep_id=sep_id,
                app_name=data['app_name'],
                svn_file=data['svn_file'],
                template=data['template'],
                owner_id=user_id,
            )
            
            type_id, log = self.__build_log('New', data)
            result = Log.insert(u_id=user_id, type_id=type_id, log=log)
            if result:
                return jsonify({'msg': result}), 500
            
            db.session.add(app)
            db.session.commit()
            return jsonify({'msg': 'success' if app.app_id else 'failure'}), 200
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Database error occurred while creating the app: {e}")
            return jsonify({'msg': 'Database error occurred, please try again later.'}), 500
        
        except Exception as e:
            db.session.rollback()
            logger.error(f"Unexpected error occurred: {e}")
            return jsonify({'msg': 'An unexpected error occurred, please try again later.'}), 500
