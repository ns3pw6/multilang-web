from flask import jsonify, Response, session
from server import db, logger
from .cache_service import CacheService
from model.dbModel import String_Update_Log, StringLanguage, String, Action_Type, AppString_Namespace, Namespace
from model.language import Language
from model.log import Log
from model.application import Application
from model.user import User
from utility.verify_utils import process_special_char, compare_special_char
from sqlalchemy import text
from typing import Dict, Tuple
from functools import lru_cache

class UpdateService(CacheService):
    
    def __init__(self) -> None:
        super().__init__()
        self.language_service = Language()
        
    @lru_cache(maxsize=1000)
    def __get_english_source(self, str_id: int) -> str:
        """Cache English source strings"""
        return StringLanguage.query.filter_by(lang_id=1, str_id=str_id) \
                                   .first() \
                                   .content
        
    @staticmethod
    def __set_trigger(action: str) -> None:
        """Set or drop the update_string trigger in the database."""
        if action == "drop":
            db.session.execute(text("DROP TRIGGER IF EXISTS update_string;"))
        elif action == "create":
            db.session.execute(text("""
                CREATE TRIGGER update_string
                AFTER UPDATE ON string_language
                FOR EACH ROW
                BEGIN
                    INSERT INTO `string_update_log` (`lang_id`, `str_id`, `old_value`, `new_value`, `update_by`) 
                    VALUES (new.lang_id, new.str_id, old.content, new.content, 'system');
                END;
            """))
            
        db.session.commit()

    def __build_log(self, type_name: str, data: Dict) -> Tuple[int, str]:
        """get log type_id and format log content"""
        log_content = ''
        if type_name == 'Recover':
            lang = Language.get(data['lang_id'])['en']
            log_content = f'StringID: {data['str_id']} <br>Lang: {lang} <br>Before_recover: {data['old_content']} <br>After_recover: {data["content"]}'
        elif type_name == 'Remove':
            log_content = f'Asn_id: {data['asn_id']}<br>App: {data['app']} <br>String: {data['string']} <br>Namespace: {data['namespace']}'
            pass
        else: 
            lang = Language.get_lang_by_tag(data['lang_tag'])
            log_content = f'StringID: {data['str_id']} <br>Language: {lang} <br>Old_content: {data['old_content']} <br>New_content: {data['content']}'
        type_id = Action_Type.query.filter_by(type_name=type_name).first().type_id
        
        return type_id, log_content

    def __compare_special_char(self, str_id: int, updated_content) -> str:
        """Compare special characters between English source string and updated content."""
        en = self.__get_english_source(str_id)
                                    
        en_pattern = process_special_char(en)
        updated_pattern = process_special_char(updated_content)
        result = compare_special_char(en_pattern, updated_pattern)
        
        if result:
            return result
        return None

    def __invalidate_related_caches(self) -> None:
        """Invalidate all related caches after an update"""
        try:
            patterns = [
                f"query_cache:string_search:*",
                f"query_cache:stringid_search:*",
                f"query_cache:app_search:*",
                f"query_cache:namespace_search:*"
            ]
            for pattern in patterns:
                self.invalidate_by_pattern(pattern)
        except Exception as e:
            logger.error(f"Cache invalidation failed: {str(e)}")
    
    def __handle_test_mode(self, action: str, data: Dict) -> Response:
        """Handle test mode for string update."""
        preview = f'測試模式預覽{action}資訊如下:<br>'
        for key, value in data.items():
            preview += f'{key}: {value}<br>'
        
        return jsonify({
            'msg': preview,
            'test_mode': True,
        }), 200
    
    def update_note(self, data: Dict) -> Response:
        """
        Update a note in the database.

        Args:
            data (Dict): Dictionary containing 'lang_tag', 'str_id', and 'content'.

        Returns:
            Response: JSON response with status code.
        """
        try:
            query = String.query.filter_by(str_id=data['str_id']).first()
            if query:
                test_mode = session.get('test_mode')
                if test_mode:
                    return self.__handle_test_mode('更新note', data)
                
                query.note = data['content']
                db.session.commit()
                self.__invalidate_related_caches()
                
                return jsonify({
                    'msg': 'Note Update successful',
                    'test_mode': test_mode,
                }), 200
            
            return jsonify({'msg': 'String not found'}), 404
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating note for str_id {data.get('str_id', 'unknown')}: {e}", exc_info=True)
            return jsonify({'msg': 'Internal server error: ' + str(e)}), 500

    def update_string(self, data: Dict) -> Response:
        """
        Update a string in the database.

        Args:
            data (Dict): Dictionary containing 'lang_tag', 'str_id', and 'content'.

        Returns:
            Response: JSON response with status code.
        """
        lang_id = self.language_service.get_lang_id_by_tag(data['lang_tag'])
        try:
            user_id = User.get_user_id(session.get('username'))
            
            check_special_char = self.__compare_special_char(data['str_id'], data['content'])
            if check_special_char:
                return jsonify({'msg': check_special_char}), 200
            
            query = StringLanguage.query.filter_by(lang_id=lang_id, str_id=data['str_id']) \
                                        .first()
            if query:
                data['old_content'] = query.content
                
                test_mode = session.get('test_mode')
                if test_mode:
                    return self.__handle_test_mode('更新字串', data)
                
                type_id, log = self.__build_log(type_name='Update', data=data)
                result = Log.insert(u_id=user_id, type_id=type_id, log=log)
                if result:
                    return jsonify({'msg': result}), 500
                
                query.content = data['content']
                db.session.commit()
                
                self.__invalidate_related_caches()
                app_ids = self.query_effected_apps([data['str_id']])
                self.signal_cache_service(app_ids)
                
                return jsonify({'msg': 'Update successful'}), 200
            return jsonify({'msg': 'String not found'}), 404
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating string for str_id {data.get('str_id', 'unknown')} in language {data.get('lang_tag', 'unknown')}: {str(e)}", exc_info=True)
            return jsonify({'msg': 'Internal server error: ' + str(e)}), 500
    
    def recover_string(self, data: Dict) -> Response:
        """
        Recover a string to its previous state.

        Args:
            data (Dict): Dictionary containing 'str_id' and 'lang_id'.

        Returns:
            Response: JSON response with status code.
        """
        try:
            user_id = User.get_user_id(session.get('username'))
            
            string_update_log = String_Update_Log.query.filter_by(str_id=data['str_id'], lang_id=data['lang_id'], deleted=0) \
                                                       .order_by(String_Update_Log.l_id.desc()) \
                                                       .first()
            
            if string_update_log:
                data['content'] = string_update_log.old_value
                data['old_content'] = string_update_log.new_value
                
                test_mode = session.get('test_mode')
                if test_mode:
                    return self.__handle_test_mode('恢復字串', data)
                
                type_id, log = self.__build_log(type_name='Recover', data=data)
                result = Log.insert(u_id=user_id, type_id=type_id, log=log)
                if result:
                    return jsonify({'msg': result}), 500
                
                string_update_log.deleted = 1
                self.__set_trigger("drop")
                
                old_value = string_update_log.old_value
                string_content = StringLanguage.query.filter_by(str_id=data['str_id'], lang_id=data['lang_id']) \
                                                     .first()
                if string_content:
                    string_content.content = old_value
                    db.session.commit()
                    
                    self.__set_trigger("create")
                    self.__invalidate_related_caches()
                    app_ids = self.query_effected_apps([data['str_id']])
                    self.signal_cache_service(app_ids)
                    
                    return jsonify({
                        'msg': 'success',
                        'old_content': old_value,
                    }), 200

            return jsonify({'msg': 'log not found'}), 404
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error recovering string {data.get('str_id', 'unknown')} in language {data.get('lang_id', 'unknown')}: {str(e)}", exc_info=True)
            return jsonify({'msg': 'Internal server error: ' + str(e)}), 500
        
    def remove_string(self, asn_id: int) -> Response:
        try:
            info = db.session.query(AppString_Namespace.asn_id, Application.app_name, StringLanguage.content, Namespace.name) \
                             .join(Application, Application.app_id==AppString_Namespace.app_id) \
                             .join(StringLanguage, StringLanguage.str_id==AppString_Namespace.str_id) \
                             .join(Namespace, Namespace.namespace_id==AppString_Namespace.namespace_id) \
                             .filter(AppString_Namespace.asn_id==asn_id) \
                             .first()
            
            asn = AppString_Namespace.query.filter_by(asn_id=asn_id, deleted=0) \
                                           .first()
            if asn:
                asn.deleted = 1
                data = {
                    'asn_id': info.asn_id,
                    'app': info.app_name,
                    'string_id': asn.str_id,
                    'string': info.content,
                    'namespace': info.name,
                }
                
                test_mode = session.get('test_mode')
                if test_mode:
                    return self.__handle_test_mode('刪除字串', data)
                
                user_id = User.get_user_id(session.get('username'))
                type_id, log = self.__build_log('Remove', data)
                result = Log.insert(u_id=user_id, type_id=type_id, log=log)
                if result:
                    return jsonify({'msg': result}), 500
                
                db.session.commit()
                self.__invalidate_related_caches()
                app_ids = self.query_effected_apps([data['str_id']])
                self.signal_cache_service(app_ids)
                
                return jsonify({'msg': 'Remove successful'}), 200
            
            return jsonify({'msg': 'App string not found'}), 404
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error removing string with asn_id {asn_id}: {str(e)}", exc_info=True)
            return jsonify({'msg': 'Internal server error: ' + str(e)}), 500
