from server import db, logger, app as current_app
from flask import send_file, jsonify, Response
from config.directory_config import (
    SOURCE_IN_DIRECTORY, 
    SOURCE_OUT_DIRECTORY, 
    CACHE_FILE_DIRECTORY, 
)
from config.parser_config import (
    LANGUAGE_LIST, 
    LANGUAGE_DATA, 
    LANGUAGE_ENCODINGS
)
from .parser_service import ParserService
from .cache_service import CacheService
from model.dbModel import Platform, Updated
from model.application import Application
from utility.file_utils import (
    generate_excel, 
    cleanup_files, 
    generate_svn_file, 
    archive_files, 
)
from utility.svn_utils import checkout_svn_file
from sqlalchemy import text
from collections import defaultdict
from typing import Tuple, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
import os, datetime

class DownloadService(CacheService):
    
    def __init__(self) -> None:
        self.language_mapping = {
            i: lang for i, lang in enumerate(
                LANGUAGE_LIST, start=1
            )
        }
        self.files_to_move = []
  
    def __zip_cache_files(self, base_dir: str, data: Dict) -> str:
        """Zips the cache files for the specified application."""
        p_id = data.get('p_id', '-1')
        if p_id == '-1':
            return self.__archive_and_send(base_dir)
        app_id = data.get('app_id', '-1')
        platform = Platform.query.filter_by(p_id=p_id).first().p_name
        base_dir = os.path.join(base_dir, platform)
        if app_id == '-1':
            return self.__archive_and_send(base_dir)
        else:
            app = Application.get_app_info(app_id).app_name
            base_dir = os.path.join(base_dir, app)
            return self.__archive_and_send(base_dir)

    def __archive_and_send(self, base_dir) -> str:
        try:
            zip_file_path = archive_files(base_dir, 'excel')
            return send_file(zip_file_path, as_attachment=True)
        except Exception as e:
            logger.error(f"Error while zipping and sending files: {e}", exc_info=True)
            return jsonify({'msg': str(e)}), 500
        finally:
            last_slash_index = zip_file_path.rfind('/')
            zip_file_path = zip_file_path[:last_slash_index]
            cleanup_files(zip_file_path)
 
    def __build_query(self, data: Dict = {}) -> str:
        """Constructs an SQL query string dynamically based on the input filtering data."""
        raw_sql = """SELECT * FROM string_mapping WHERE 1=1"""
        app_id = data.get('app_id', '-1')
        if app_id != '-1':
            tmp_app_id = [app_id] if isinstance(app_id, str) else app_id
            raw_sql += f"  AND app_id IN ({','.join(map(str, tmp_app_id))})"
        raw_sql += " AND p_id NOT IN (8, 9)"

        with current_app.app_context():
            base_query = db.session.execute(text(raw_sql))
        return base_query
    
    def __format_result(self, results: tuple, type: str = '', target_lang_id: int = -1) -> Dict:
        """Formats the query results into a structured dictionary based on the given 'type'."""
        formatted_results = defaultdict(lambda: defaultdict(lambda: defaultdict(str)))
        untranslated = defaultdict(lambda: defaultdict(set))
        eng_strings = {} 

        for _, p_name, _, app_name, _, namespace, str_id, *lang_contents in results:
            key = (p_name, app_name)
            
            if type == 'svn_result':
                formatted_results[key][namespace] = dict(zip(self.language_mapping.values(), lang_contents))
            elif type == 'untranslate':
                for lang_id, content in zip(self.language_mapping.keys(), lang_contents):
                    if not content:
                        untranslated[key][self.language_mapping[lang_id]].add(str_id)
                    elif lang_id == 1:
                        eng_strings[str_id] = content
            else:
                string_mapping = dict(zip(self.language_mapping.keys(), lang_contents))
                
                if target_lang_id != -1:
                    formatted_results[key][str_id].update({
                        self.language_mapping[1]: string_mapping[1],
                        self.language_mapping[target_lang_id]: string_mapping[target_lang_id],
                    })
                else:
                    formatted_results[key][str_id] = dict(zip(self.language_mapping.values(), lang_contents))

        return {
            'formatted_results': {k: dict(v) for k, v in formatted_results.items()},
            'untranslated': {k: dict(v) for k, v in untranslated.items()},
            'eng_strings': eng_strings
        }
    
    def __process_language(self, lang_code: str, data: Dict, input_file: str, translations: Dict) -> Tuple[bool, None | str]:
        """Processes the given language code and generates SVN files if necessary.

        Args:
            lang_code (str): The language code to process.
            data (dict): The data containing file information.
            input_file (str): The input file path.
            translations (dict): The dictionary of translations.

        Returns:
            tuple: A tuple containing a boolean indicating success and the output file path or None.
        """
        datas = {
            'p_id': data['p_id'],
            'lang_code': lang_code,
            'app_name': data['app_name'],
            'input_file': input_file,
            'translations': translations[(data['platform_name'], data['app_name'])],
        }
        
        response, new_content = ParserService().generate_svn_file_content(datas)
        if not response:
            if new_content == 'continue':
                if data['template_file'].endswith('.rc'):
                    return True, input_file
                return True, None
            raise Exception(new_content)

        output_dir = self.__get_output_dir(data['p_id'], lang_code, data['platform_name'], data['app_name'])
        file_name = self.__get_file_name(data['p_id'], data['template_file'], lang_code, data['app_name'])
        encoding = self.__determine_encoding(data['p_id'], data['template_file'], lang_code)


        for dir_path in output_dir:
            result, response = generate_svn_file(new_content, dir_path, file_name, encoding=encoding)
            if not result:
                raise RuntimeError('Failed to generate svn file')
        
        if data['template_file'].endswith('.rc'):
            return True, response
        return True, None

    def __generate_svn_files(self, data: Dict) -> Tuple[bool, None | str]:
        """Generate SVN file for a specific language."""
        input_file = os.path.join(SOURCE_IN_DIRECTORY, data['platform_name'], data['app_name'], data['template_file'])
        query = self.__build_query(data)
        results = query.all()
        translations = self.__format_result(results, 'svn_result')['formatted_results']
        if not translations:
            return False, 'No translations found'

        if data['template_file'].endswith('.rc'):
            for lang_code in self.language_mapping.values():
                result, response = self.__process_language(lang_code, data, input_file, translations)
                input_file = response
        else:
            with ThreadPoolExecutor() as executor:
                futures = {
                    executor.submit(self.__process_language, lang_code, data, input_file, translations): lang_code
                    for lang_code in self.language_mapping.values()
                }

                for future in as_completed(futures):
                    lang_code = futures[future]
                    try:
                        result, error = future.result()
                        if not result:
                            return False, f'Error processing {lang_code}: {error}'
                    except Exception as e:
                        logger.error("Exception occurred while processing language %s: %s", lang_code, str(e))
                        raise

        return True, None

    def __determine_encoding(self, p_id: str, template_file: str, lang_code: str) -> str:
        """Determine encoding based on project ID and file type."""
        if p_id == '2':
            if template_file.endswith('.rc'):
                return 'UTF-16LE'
            elif template_file.endswith('.isl'):
                return LANGUAGE_ENCODINGS.get(lang_code, 'UTF-8')
        return 'UTF-8'

    def __get_output_dir(self, p_id: str, lang_code: str, platform_name: str, app_name: str) -> str:
        """Get the output directory based on parameters."""
        if p_id == '3' or p_id == '5':
            dir_names = []
            for name in LANGUAGE_DATA[lang_code]['mac_dir']:
                dir_names.append(os.path.join(SOURCE_OUT_DIRECTORY, platform_name, app_name, name))
            return dir_names
        if p_id == '4':
            return [os.path.join(SOURCE_OUT_DIRECTORY, platform_name, app_name, LANGUAGE_DATA[lang_code]['android_dir'])]
        if p_id == '6':
            return [os.path.join(SOURCE_OUT_DIRECTORY, platform_name, app_name, LANGUAGE_DATA[lang_code]['chrome_dir'])]
        return [os.path.join(SOURCE_OUT_DIRECTORY, platform_name, app_name)]

    def __get_file_name(self, p_id: str, template_file: str, lang_code: str, app_name: str) -> str:
        """Get the file name based on parameters."""
        if p_id == '2' and template_file.endswith('.xaml'):
            return template_file.replace('en-us', LANGUAGE_DATA[lang_code].get('win_xaml', 'en-us'))
        if app_name == 'Win Setup All':
            return LANGUAGE_DATA[lang_code]['win_setup_all']
        return template_file.replace('en-US', lang_code)
    
    def __check_updated(self) -> bool:
        """Check if any string has been updated."""
        try:
            folder_path = CACHE_FILE_DIRECTORY
            folder_mtime = os.path.getmtime(folder_path)
            folder_mtime_readable = datetime.datetime.fromtimestamp(folder_mtime)
            
            query = Updated.query.first()
            update_time = query.string_update_time
            cache_status = query.still_caching
            if update_time:
                if cache_status == 0:
                    if update_time < folder_mtime_readable:
                        return False
            return True
        except Exception as e:
            logger.error(f"Unexpected error when checking updated strings: {e}", exc_info=True)
            return jsonify({'msg': "DB error!"}), 500
    
    def download_untranslate_excel(self, data: Dict) -> Response:
        """Download Excel files with untranslated strings."""
        try:
            updated = self.__check_updated()
            cache_dir = os.path.join(CACHE_FILE_DIRECTORY, 'due')
            unique_dir, zip_file_path = None, None
            if not updated:
                return self.__zip_cache_files(cache_dir, data)
            
            query = self.__build_query(data)
            results = query.all()
            
            result = self.__format_result(results, 'untranslate')
            eng_strings = result['eng_strings']
            untranslated = result['untranslated']
            
            response, msg, unique_dir = generate_excel(untranslated, 'due', eng_strings)
            if not response:
                return jsonify({'msg': msg}), 500
            
            zip_file_path = archive_files(unique_dir, 'excel')
            return send_file(zip_file_path, as_attachment=True)
        except Exception as e:
            logger.error(f"Unexpected error when download app_id ({data['app_id']}) untranslate excel: {e}", exc_info=True)
            return jsonify({'msg': str(e)}), 500
        finally:
            if zip_file_path:
                last_slash_index = zip_file_path.rfind('/')
                zip_file_path = zip_file_path[:last_slash_index]
            cleanup_files(unique_dir)
            cleanup_files(zip_file_path)
                
    def download_full_excel(self, data: Dict) -> Response:
        """Download a full Excel file with all translations."""
        try:
            lang_id = data.get('lang_id', -1)
            lang_tag = 'all' if lang_id == '-1' else self.language_mapping[int(lang_id)]
            cache_dir = os.path.join(CACHE_FILE_DIRECTORY, 'dfe', lang_tag)
            unique_dir, zip_file_path = None, None
            updated = self.__check_updated()
            if not updated:
                lang_id = data.get('lang_id', -1)
                lang_tag = 'all' if lang_id == '-1' else self.language_mapping[int(lang_id)]
                return self.__zip_cache_files(cache_dir, data)
                
            query = self.__build_query(data)
            results = query.all()

            formatted_results = self.__format_result(results, 'full', int(data['lang_id']))['formatted_results']
            
            response, msg, unique_dir = generate_excel(formatted_results, 'dfe')
            if not response:
                return jsonify({'msg': msg}), 500
            
            zip_file_path = archive_files(unique_dir, 'excel')
            return send_file(zip_file_path, as_attachment=True)
        except Exception as e:
            logger.error(f"Unexpected error when download app_id ({data['app_id']}) full excel: {e}", exc_info=True)
            return jsonify({'msg': str(e)}), 500
        finally:
            if zip_file_path:
                last_slash_index = zip_file_path.rfind('/')
                zip_file_path = zip_file_path[:last_slash_index]
            cleanup_files(unique_dir)
            cleanup_files(zip_file_path)
    
    def download_svn(self, data: Dict) -> Response:
        """Download SVN files for the specified application."""
        try:
            query = db.session.query(Platform.p_name, Application.app_name, Application.svn_file, Application.template) \
                              .join(Application, Platform.p_id == Application.p_id) \
                              .filter(Application.app_id == data['app_id'], Platform.p_id == data['p_id']) \
                              .first()
            if not query:
                return jsonify({'msg': 'Application not found'}), 404
            if not query.svn_file or not query.template:
                return jsonify({'msg': 'svn路徑錯誤，請先進行修正'}), 404
            
            platform_name, app_name, svn_path, template_file = query
            data.update({
                'platform_name': platform_name,
                'app_name': app_name,
                'template_file': template_file,
            })

            checkout_svn_file(svn_path, template_file, platform_name, app_name)
            response, error = self.__generate_svn_files(data)

            if not response:
                return jsonify({'msg': error}), 404
            
            zip_file_path = archive_files(os.path.join(SOURCE_OUT_DIRECTORY, platform_name), app_name)
            return send_file(zip_file_path, as_attachment=True)     
        except Exception as e:
            logger.error(f"Unexpected error when download app_id ({data['app_id']}) svn files: {e}", exc_info=True)
            return jsonify({'msg': str(e)}), 500
        finally:
            cleanup_files(SOURCE_OUT_DIRECTORY)
            cleanup_files(SOURCE_IN_DIRECTORY)

    def download_search(self, data: Dict) -> Response:
        """Download search results."""
        try:
            response, msg, unique_dir = generate_excel(data, 'dsr')
            if not response:
                return jsonify({'msg': msg}), 500
            
            return self.__archive_and_send(unique_dir)
        except Exception as e:
            logger.error(f"Unexpected error when download search string: {e}", exc_info=True)
            return jsonify({'msg': str(e)}), 500
        finally:
            cleanup_files(unique_dir)
            cleanup_files(SOURCE_OUT_DIRECTORY)

    def download_untranslate_by_time(self, data: Dict) -> Response:
        app_ids_by_create_time = Application.get_app_id(data['start_time'], data['end_time'])
        if not app_ids_by_create_time:
            return jsonify({'msg': 'Not found'}), 404
        
        data['app_id'] = app_ids_by_create_time
        data['p_id'] = '-1'
        return self.download_untranslate_excel(data)
