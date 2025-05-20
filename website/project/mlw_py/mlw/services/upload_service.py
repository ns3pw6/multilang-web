from flask import jsonify, Response, session
from server import db, app, logger
from config.directory_config import EXCEL_IN_DIRECTORY, SOURCE_IN_DIRECTORY
from .parser_service import ParserService
from .cache_service import CacheService
from model.dbModel import String, Namespace, Separator, StringLanguage, AppString_Namespace, Action_Type
from model.application import Application
from model.language import Language
from model.log import Log
from model.user import User
from utility.svn_utils import checkout_svn_file
from utility.file_utils import check_directory_exists, cleanup_files, move_file
from utility.verify_utils import process_special_char, compare_special_char
from sqlalchemy import and_
from typing import Tuple, Dict, List
import threading
import os
import html

class UploadService(CacheService):
    
    def __init__(self) -> None:
        super().__init__()
        self.parser_model = ParserService()
        self.error_messages = []

    def __query_exist_string(self, contents: list) -> Tuple:
        """Query existing strings in the database."""
        subquery_eng = db.session.query(StringLanguage.str_id, StringLanguage.content, String.postfix) \
                                 .join(String, StringLanguage.str_id == String.str_id) \
                                 .filter(db.func.lower(StringLanguage.content).in_([c.lower() for c in contents]),
                                         StringLanguage.lang_id == 1) \
                                 .subquery()

        result = db.session.query(subquery_eng, StringLanguage.content.label('zh_content')) \
                           .outerjoin(StringLanguage, and_(subquery_eng.c.str_id == StringLanguage.str_id,
                                                           StringLanguage.lang_id == 2)) \
                           .all()

        return result
    
    @staticmethod
    def escape_html(text):
        return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    
    def __build_options_bulk(self, contents: str | List) -> Dict:
        """Create existing string options for bulk processing."""
        options = {}
        if isinstance(contents, str):
            contents = [contents]

        result = self.__query_exist_string(contents)
        for row in result:
            options.setdefault((row[1]).lower(), []).append({
                'str_id': row[0],
                'formatted_string': f'{html.escape(row[1])}({row[3]}) (note: {row[2]})'
            })

        return options
    
    def __get_postfix(self, namespace: str, app_id: int) -> str:
        """Get the postfix from the namespace based on the separator."""
        separator = db.session.query(Separator.type) \
                              .join(Application, Separator.sep_id == Application.sep_id) \
                              .filter(Application.app_id == app_id) \
                              .scalar()
            
        return namespace.split(separator)[-1]

    def __create_app_string_namespace(self, app_id: int, namespace_map: Dict, string_map: Dict, datas: Dict) -> None:
        """Create AppString_Namespace entries for bulk insertion."""
        new_app_string_namespaces = []

        for key in datas.keys():
            str_id = string_map[key].str_id if isinstance(string_map[key], String) else string_map[key]
            namespace_id = namespace_map[key].namespace_id if isinstance(namespace_map[key], Namespace) else namespace_map[key]
            new_app_string_namespaces.append(AppString_Namespace(
                app_id=app_id,
                namespace_id=namespace_id,
                str_id=str_id
            ))

        db.session.add_all(new_app_string_namespaces)

    def __create_string_languages(self, string_map: Dict, datas: Dict) -> None:
        """Create StringLanguage entries for bulk insertion."""
        new_string_languages = []

        for key, value in datas.items():
            if value['str_id'] == '-1':
                str_id = string_map[key].str_id
                lang_ids = range(1, 23)
                new_string_languages.extend([
                    StringLanguage(
                        str_id=str_id, 
                        lang_id=lang_id, 
                        content=value.get('en' if lang_id == 1 else 'zh-TW' if lang_id == 2 else None)
                    )
                    for lang_id in lang_ids
                ])

        db.session.add_all(new_string_languages)

    def __build_log(self, user_id: int, app_id: str, type_name: str, datas: Dict, namespace_map: Dict = None, string_map: Dict = None) -> None :
        """Builds logs based on the action type and provided data."""
        new_log = []
        app_name = None
        if app_id != -1:
            app_name = Application.get_app_info(app_id).app_name
        type_id = Action_Type.query.filter_by(type_name=type_name).first().type_id
        
        str_ids = set()
        
        for key in datas.keys():
            log = f'App: {app_name} <br>'
            
            if type_id == 3: # Insert
                str_id = string_map[key].str_id if isinstance(string_map[key], String) else string_map[key]
                str_ids.add(str_id)
                namespace_id = namespace_map[key].namespace_id if isinstance(namespace_map[key], Namespace) else namespace_map[key]
                log += f'Namespace_id: {namespace_id} <br>Namespace: {key} <br>StringID: {str_id}'
            elif type_id == 4:  # Remove
                log += f'Namespace_id: {key} <br>Namespace: {datas[key]}' 
            elif type_id == 5: #Update
                str_id = string_map[key]['string_id']
                str_ids.add(str_id)
                old_eng = string_map[key]['old_eng']
                new_eng = string_map[key]['new_eng']
                log += f'StringID: {str_id} <br>Old_eng: {old_eng} <br>New_eng: {new_eng}'
                
            new_log.append(Log(
                u_id=user_id,
                type_id=type_id,
                log=log
            ))

        db.session.add_all(new_log)
        return str_ids

    def __build_excel_upload_log(self, log_info: Dict):
        """Builds logs based on the excel(s) and provided data."""
        new_log = []

        for lang_id, data in log_info['datas'].items():
            lang = Language.get(int(lang_id))['en']
            for str_id, value in data.items():
                type_id = Action_Type.query.filter_by(type_name=value['type_name']).first().type_id
                log = f'StringID: {str_id} <br>Lang: {lang} <br>'
                if type_id == 5:
                    log += f'Old_content: {value['old_content']} <br>New_content: {value['new_content']}'
                else:
                    log += f'Content: {value['content']}'  
                
                new_log.append(Log(
                    u_id=log_info['user_id'],
                    type_id=type_id,
                    log=log
                ))

        db.session.add_all(new_log)

    def __update_excel_note(self, note: str, str_id: str) -> Tuple[bool, str | None]:
        """Update the note for a string."""
        query = db.session.query(String).filter_by(str_id=str_id).first()
        if query:
            test_mode = session.get('test_mode')
            if test_mode:
                return False, f'測試模式無法更新note! | note: <strong>{note}</strong>'
            query.note = note
            try:
                db.session.commit()
                return True, None
            except Exception as e:
                db.session.rollback()
                logger.error(f"Failed to update note for StringID {str_id}: {str(e)}")
                return False, str(e)
        else:
            return False, '找不到stringID!!'
    
    def __move_and_parse_excel(self, upload_file_name_array: List) -> Dict:
        """Move and parse the excel file."""
        datas = {}
        
        for filename in upload_file_name_array:
            file = os.path.join(EXCEL_IN_DIRECTORY, filename)
            try:
                move_file(file, destination_path=SOURCE_IN_DIRECTORY, name=filename)
            except Exception as e:
                logger.error(f"Failed to move file {filename}: {str(e)}")
                continue
            
            target_file = os.path.join(SOURCE_IN_DIRECTORY, filename)
            try:
                df = self.parser_model.parse_excel_file(target_file)
                datas.update(self.parser_model.process_excel_data(df))
            except Exception as e:
                logger.error(f"Failed to parse file {filename}: {str(e)}")
                continue

        return datas

    def __fetch_existing_namespaces(self, app_id: int):
        """Fetch namespace in database."""
        return db.session.query(Namespace.namespace_id, Namespace.name) \
                         .join(AppString_Namespace,
                               Namespace.namespace_id == AppString_Namespace.namespace_id) \
                         .filter(AppString_Namespace.app_id == app_id,
                                 AppString_Namespace.deleted == 0) \
                         .all()

    def __fetch_all_strings(self, app_id: int):
        """Fetch the equal strings in database."""
        return db.session.query(String.str_id, String.postfix, StringLanguage.content,
                                AppString_Namespace.namespace_id) \
                         .join(StringLanguage, String.str_id == StringLanguage.str_id) \
                         .join(AppString_Namespace, AppString_Namespace.str_id == String.str_id) \
                         .filter(AppString_Namespace.app_id == app_id,
                                 StringLanguage.lang_id == 1,
                                 AppString_Namespace.deleted == 0) \
                         .all()

    def __skip_eng_and_update_note(self, str_id: int, lang_tag: str, content: str) -> bool:
        """Skip English and update note if applicable."""
        if lang_tag == 'en-US':
            return True
                
        if lang_tag == 'note':
            response, msg = self.__update_excel_note(content, str_id)
            if not response:
                self.error_messages.append(f'StringID: <strong>{str_id}</strong> | <strong>{lang_tag}</strong> | <strong>{msg}</strong>')
                return True
        
        return False
    
    def __compoare_special_char(self, en_pattern: Dict, content: str) -> str:
        """Compare special characters in English and content."""
        tmp_pattern = process_special_char(content)
        compare_result = compare_special_char(en_pattern, tmp_pattern)
        
        if compare_result:
            return f'與英文版特殊字元不同! <strong>{compare_result}</strong>'
        
        return ''

    def __force_update_check(self, force_update: bool) -> str:
        """Check if force update is enabled."""
        if not force_update:
            return '<strong>如要更新字串請勾選強制覆蓋!</strong>'

        return ''    

    def __process_string(self, user_id: int, data: Dict, force_update: bool, test_mode: bool) -> List:
        """Process string with language/note to update data."""
        string_ids = list(data.keys())
        
        existing_strings = db.session.query(String).filter(String.str_id.in_(string_ids)).all()
        existing_languages = db.session.query(StringLanguage).filter(StringLanguage.str_id.in_(string_ids)).all()
        query = Language.query.all()
        languages = {language.lang_tag: language.lang_id for language in query}
        
        string_map = {str(s.str_id): s for s in existing_strings}
        lang_map = {(sl.str_id, sl.lang_id): sl for sl in existing_languages}
        log_info = {
            'user_id': user_id,
            'datas': {},
        }

        counter = 0
        str_ids = set()
        for str_id, lang_contents in data.items():
            str_ids.add(str_id)
            base_msg = f'StringID: <strong>{str_id}</strong> | '
            
            if str_id not in string_map:
                self.error_messages.append(f'{base_msg}<strong>StringID不存在!</strong>')
                continue
            
            en_key = (int(str_id), 1)
            en = lang_map.get(en_key)
            en_pattern = process_special_char(en.content)
            
            for lang_tag, content in lang_contents.items():
                lang_msg = f'<strong>{lang_tag}</strong> | '
                
                if self.__skip_eng_and_update_note(str_id, lang_tag, content):
                    continue
                
                if lang_tag not in languages:
                    if lang_tag != 'note':
                        self.error_messages.append(f'{base_msg}{lang_msg}<strong>語言不存在!</strong>')
                    continue

                lang_id = languages[lang_tag]
                key = (int(str_id), int(lang_id))
                string_lang = lang_map.get(key)
                
                if not content:
                    self.error_messages.append(f'{base_msg}{lang_msg}<strong>內容為空!</strong>')
                else:
                    content = content.strip()
                    
                    comapare_result = self.__compoare_special_char(en_pattern, content)
                    if comapare_result:
                        self.error_messages.append(f'{base_msg}{lang_msg}{comapare_result}')
                        continue

                    check_result = self.__force_update_check(force_update)
                    if check_result:
                        self.error_messages.append(f'{base_msg}{lang_msg}{check_result}')
                        continue

                    log_info['datas'].setdefault(lang_id, {})
                    
                    if not string_lang:
                        if str_id not in log_info['datas'][lang_id]:
                            if test_mode:
                                tmp_data = {
                                    'content': content.strip(),
                                }
                                self.__handle_excel_upload_test_mode('新增', tmp_data)
                                continue
                            
                            log_info['datas'][lang_id][str_id] = {
                                'type_name': 'Create',
                                'content': content.strip(),
                            }
                            new_string_lang = StringLanguage(str_id=str_id, lang_id=lang_id, content=content)
                            db.session.add(new_string_lang)
                            counter += 1
                            
                        continue
                            
                    if content != (string_lang.content).strip():
                        if str_id not in log_info['datas'][lang_id]:
                            if test_mode:
                                tmp_data = {
                                    'content': content.strip(),
                                }
                                msg = self.__handle_excel_upload_test_mode('更新', tmp_data)
                                self.error_messages.append(f'{base_msg}{lang_msg}{msg}')
                                continue

                            old_content = string_lang.content
                            log_info['datas'][lang_id][str_id] = {
                                'type_name': 'Update',
                                'old_content': old_content or 'None',
                                'new_content': content,
                            }
                        counter += 1
                        string_lang.content = content
        if not test_mode:
            self.__build_excel_upload_log(log_info)
            db.session.commit()
            
            app_ids = self.query_effected_apps(list(str_ids))
            self.signal_cache_service(app_ids)

        return counter

    def __get_svn_file(self, p_id: int, app_id: int, platform: str) -> Tuple[bool, str|None]:
        """Get svn file to parse"""
        query = Application.query.filter_by(p_id=p_id, app_id=app_id).first()
        if not query:
            logger.error('An error occured: %s', 'Application not found', exc_info=True)
            return False, 'Application not found!'
            
        if not query.svn_file:
            logger.error('An error occured: %s', 'SVN file path not found!', exc_info=True)
            return False, 'Svn file path not found!'
            
        get_svn_file_success = checkout_svn_file(
            svn_file=query.svn_file,
            template=query.template,
            platform=platform,
            app_name=query.app_name
        )
        if not get_svn_file_success:
            logger.error('An error occured: %s', get_svn_file_success, exc_info=True)
            return False, '找不到Template!'
        
        return True, query.template

    def __get_required_data(self, app_id: int):
        """Get namespaces and strings"""
        existing_namespaces = []
        all_strings = []

        def thread_fetch_namespaces():
            with app.app_context():
                nonlocal existing_namespaces
                existing_namespaces = self.__fetch_existing_namespaces(app_id)

        def thread_fetch_strings():
            with app.app_context():
                nonlocal all_strings
                all_strings = self.__fetch_all_strings(app_id)

        thread_namespace = threading.Thread(target=thread_fetch_namespaces)
        thread_strings = threading.Thread(target=thread_fetch_strings)

        thread_namespace.start()
        thread_strings.start()
        thread_namespace.join()
        thread_strings.join()
            
        namespaces_by_app_id = {item.name: item.namespace_id for item in existing_namespaces}
        string_info = {row.namespace_id: {'str_id': row.str_id, 'content': row.content, 'postfix': row.postfix} 
                    for row in all_strings}
        
        return namespaces_by_app_id, string_info

    def __get_diff_data(self, svn_result, namespaces_by_app_id, string_info):
        """Process namespaces to identify inserts, removals and updates based on SVN results"""
        lock = threading.Lock()
        insert, update, remove = {}, {}, {}
        
        def process_namespace(name, namespace_id):
            with lock:  
                current_eng = string_info.get(namespace_id)
                escape_current_eng = html.escape(current_eng['content'])
                if current_eng and (current_eng['content'] != svn_result[name] and escape_current_eng != svn_result[name]):
                    update[name] = {
                        'namespace_id': namespace_id,
                        'current_eng': html.escape(current_eng['content']),
                        'new_eng': html.escape(svn_result[name]),
                        'str_id': current_eng['str_id']
                    }

        set_svn_namespace = set(svn_result.keys())
        set_db_namespace = set(namespaces_by_app_id.keys())
            
        remove_namespace = set_db_namespace - set_svn_namespace
        remove = {
            namespaces_by_app_id[namespace]: namespace
            for namespace in remove_namespace
        }
            
        threads = []
        update_namespace = set_db_namespace - remove_namespace
        for namespace in update_namespace:
            thread = threading.Thread(target=process_namespace, args=(namespace, namespaces_by_app_id[namespace]))
            threads.append(thread)
            thread.start()
            
        for thread in threads:
            thread.join()
            
        # Identify new namespaces and prepare the insert operations
        new_namespaces = set_svn_namespace - set_db_namespace
        new_contents = [svn_result[namespace] for namespace in new_namespaces]
        bulk_options = self.__build_options_bulk(new_contents)
            
        insert = {
            namespace: {
                'new_eng': html.escape(content),
                'options': bulk_options.get(content.lower(), [])
            }
            for namespace, content in svn_result.items()
            if namespace in new_namespaces
        }
        
        return insert, update, remove

    def __handle_excel_upload_test_mode(self, action: str, data: Dict) -> str:
        """Handle test mode for string upload."""
        preview = f'{action}字串預覽: '
        for key, value in data.items():
            preview += f'{key}: {value} '
        
        return preview

    def __handle_svn_test_mode(self, data: Dict) -> str:
        """Handle test mode for string upload."""
        preview = ''
        for key, value in data.items():
            preview += f'<br>{key}: {value} '
        
        return preview
    
    def upload_excel(self, file, filename) -> Response:
        """Update existing string from uploaded excel."""
        try:
            if file:
                directory = EXCEL_IN_DIRECTORY
                check_directory_exists(directory)
                
                file.save(os.path.join(directory, filename))
                return jsonify({'msg': 'success'}), 200
            else:
                logger.warning(f"Failed to get file: {filename}.")
                return jsonify({'msg': 'get file failed'}), 422
        except Exception as e:
            logger.error(f"An error occurred while uploading file {filename}: {str(e)}", exc_info=True)
            return jsonify({'msg': str(e)}), 500

    def upload_excel_content(self, data: dict) -> Response:
        """Upload string from uploaded excel."""
        force_update = data.get('force_update', False)
        try:
            user_id = User.get_user_id(session.get('username'))
            test_mode = session.get('test_mode')

            datas = {}
            self.error_messages = []
            datas = self.__move_and_parse_excel(data['uploadFileNameArray'])
            counter = self.__process_string(user_id, datas, force_update, test_mode)

            db.session.commit()
            return jsonify({
                'msg': self.error_messages if self.error_messages else 'success',
                'count': counter,
                'test_mode': test_mode
            }), 200
        except Exception as e:
            db.session.rollback()
            logger.error('An error occurred while uploading and processing excel content: %s', e, exc_info=True)
            return jsonify({'msg': 'Internal server error'}), 500
        finally:
            cleanup_files(SOURCE_IN_DIRECTORY)
            cleanup_files(EXCEL_IN_DIRECTORY)
            
    def upload_from_svn(self, p_id: int, app_id: int, data: Dict) -> Response:
        """Upload new/update/remove string and namespace from SVN.

        Args:
            p_id (int): Platform ID.
            app_id (int): Application ID.
            data (dict): Data containing platform and app information.

        Returns:
            jsonify: JSON response with insert, update, and remove actions.
        """
        platform = data[str(p_id)]
        app_name = data[str(app_id)]
        try:
            get_svn_file_success, result = self.__get_svn_file(p_id, app_id, platform)
            if not get_svn_file_success:
                return jsonify({'msg': result}), 404

            storage_path = os.path.join(SOURCE_IN_DIRECTORY, platform, app_name)
            check_directory_exists(storage_path)
            
            filepath = os.path.join(storage_path, result)
            svn_result = self.parser_model.parse_file(p_id, app_name, filepath)
            if 'parse_error_msg' in svn_result:
                logger.error('An error occured: %s', svn_result['parse_error_msg'], exc_info=True)
                return jsonify({'msg': svn_result['parse_error_msg']}), 422
            
            namespaces_by_app_id, string_info = self.__get_required_data(app_id)
            insert, update, remove = self.__get_diff_data(svn_result, namespaces_by_app_id, string_info)
            
            return jsonify({
                'insert': insert,
                'update': update,
                'remove': remove,
            }), 200
        except Exception as e:
            logger.error(f"An error occurred during SVN upload for app {app_name}: {str(e)}", exc_info=True)
            return jsonify({'msg': str(e)}), 500
        finally:
            cleanup_files(SOURCE_IN_DIRECTORY)

    def insert_string(self, data: Dict) -> Response:
        """Insert new namespaces, strings, and their associated language translations.

        Args:
            data (dict): Contains application ID and data for namespaces and strings.

        Returns:
            jsonify: JSON response with success or error message.
        """
        try:
            existing_namespaces = db.session.query(Namespace) \
                                            .filter(Namespace.name.in_(data['datas'].keys())) \
                                            .all()
            existing_namespace_dict = {ns.name: ns.namespace_id for ns in existing_namespaces}
            
            test_mode = session.get('test_mode')
            new_namespaces = []
            new_strings = []
            namespace_map, string_map = {}, {}
            test_msgs = []

            for key, value in data['datas'].items():
                if test_mode:
                    tmp_data = {
                        'namespace': key,
                        'string': value['en']
                    }
                    test_msgs.append(self.__handle_svn_test_mode(tmp_data))
                    continue

                if key not in existing_namespace_dict.keys():
                    new_namespace = Namespace(name=key)
                    new_namespaces.append(new_namespace)
                    namespace_map[key] = new_namespace
                else:
                    namespace_map[key] = existing_namespace_dict[key]

                if value['str_id'] == '-1':
                    postfix = self.__get_postfix(key, data['app_id'])
                    new_string = String(postfix=postfix)
                    new_strings.append(new_string)
                    string_map[key] = new_string
                else:
                    string_map[key] = value['str_id']

            if test_mode:
                res = f'<br>-'.join(test_msgs)
                return jsonify({
                    'msg': 'success',
                    'test_msg': f'新增app字串預覽: {res}',
                    'test_mode': test_mode
                }), 200
            
            db.session.add_all(new_namespaces)
            db.session.add_all(new_strings)
            db.session.flush()
            
            user_id = User.get_user_id(session.get('username'))

            # Create associations and language entries
            self.__create_app_string_namespace(data['app_id'], namespace_map, string_map, data['datas'])
            self.__create_string_languages(string_map, data['datas'])
            str_ids = self.__build_log(
                user_id=user_id, 
                app_id=data['app_id'], 
                type_name='Create', 
                datas=data['datas'], 
                namespace_map=namespace_map, 
                string_map=string_map
            )
            apps_id = self.query_effected_apps(str_ids)
            self.signal_cache_service(apps_id)
            
            db.session.commit()
            return jsonify({'msg': 'success'}), 200
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error occurred during string insertion for app_id={data['app_id']}: {str(e)}", exc_info=True)
            return jsonify({'msg': str(e)}), 500

    def update_string(self, data: Dict) -> Response:
        """Update app English string."""
        try:
            test_mode = session.get('test_mode')
            app_id = data['app_id']
            updates_data = data['datas']
            string_map = {}
            
            mappings = []
            for key, update_info in updates_data.items():
                current_eng = update_info['current_eng']
                new_eng = update_info['new_eng']
                str_id = update_info['str_id']
                
                query_string_eng = db.session.query(StringLanguage) \
                                             .join(AppString_Namespace, StringLanguage.str_id == AppString_Namespace.str_id) \
                                             .filter(AppString_Namespace.app_id == app_id,
                                                     AppString_Namespace.str_id == str_id,
                                                     AppString_Namespace.deleted == 0,
                                                     StringLanguage.lang_id == 1) \
                                             .first()
                                             
                # query_string_eng.content = new_eng
                mappings.append({
                    'sl_id': query_string_eng.sl_id,
                    'content': new_eng,
                })
                
                max_length = 50
                if len(current_eng) > max_length:
                    current_eng = f'{current_eng[:max_length]}...(字串太長下略)'
                if len(new_eng) > max_length:
                    new_eng = f'{new_eng[:max_length]}...(字串太長下略)'
                if key not in string_map.keys():
                    string_map[key] = {
                        'string_id': str_id,
                        'old_eng': current_eng,
                        'new_eng': new_eng,
                    }

            if mappings:
                if test_mode:
                    tmp_data = {}
                    test_msgs = []
                    for _, value in string_map.items():
                        tmp_data = {
                            'old_eng': value['old_eng'],
                            'new_eng': value['new_eng']
                        }
                        test_msgs.append(self.__handle_svn_test_mode(tmp_data))
                        
                    res = f'<br>-'.join(test_msgs)
                    return jsonify({
                        'msg': 'success',
                        'test_msg': f'更新app字串預覽: {res}',
                        'test_mode': test_mode
                    }), 200
                
                db.session.bulk_update_mappings(StringLanguage, mappings)
                
                user_id = User.get_user_id(session.get('username'))
                
                str_ids = self.__build_log(
                    user_id=user_id, 
                    app_id=app_id, 
                    type_name='Update', 
                    datas=data['datas'], 
                    string_map=string_map
                )
                db.session.commit()
                
                apps_id = self.query_effected_apps(str_ids)
                self.signal_cache_service(apps_id)
                
                return jsonify({'msg': 'success'}), 200
            else:
                return jsonify({'msg': 'No updates needed'}), 200
        except Exception as e:
            db.session.rollback()
            logger.error('An error occured: %s', e, exc_info=True)
            return jsonify({'msg': str(e)}), 500

    def remove_string(self, data: Dict) -> Response:
        """Remove app string."""
        namespace_ids = list(map(int, data['datas'].keys()))
        try:
            user_id = User.get_user_id(session.get('username'))
            test_mode = session.get('test_mode')
            
            query = AppString_Namespace.query.filter(AppString_Namespace.app_id == data['app_id'],
                                                     AppString_Namespace.namespace_id.in_(namespace_ids)) \
                                             .all()

            if not query:
                logger.error('找不到namespace!!')
                return jsonify({'msg': '找不到namespace!!'}), 404

            if test_mode:
                test_msgs = []
                for n_id, namespace in data['datas'].items():
                    tmp_data = {
                        'namespace': namespace
                    }
                    test_msgs.append(self.__handle_svn_test_mode(tmp_data))
                
                res = f'<br>-'.join(test_msgs)
                return jsonify({
                    'msg': 'success',
                    'test_msg': f'刪除app字串預覽: {res}',
                    'test_mode': test_mode
                }), 200

            for row in query:
                row.deleted = 1

            self.__build_log(
                user_id=user_id, 
                app_id=data['app_id'], 
                type_name='Remove', 
                datas=data['datas'], 
            )
            
            db.session.commit()
            self.signal_cache_service({data['app_id']})
            return jsonify({'msg': 'success'}), 200
        except Exception as e:
            db.session.rollback()
            logger.error('An error occured: %s', e, exc_info=True)
            return jsonify({'msg': 'Internal server error'}), 500
