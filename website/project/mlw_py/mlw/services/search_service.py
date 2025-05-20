from flask import jsonify, Response
from server import db, logger
from .cache_service import CacheService
from model.dbModel import String, Namespace, String_Update_Log, StringLanguage, AppString_Namespace, Platform, Action_Type
from model.language import Language
from model.application import Application
from model.user import User
from model.log import Log
from sqlalchemy.exc import SQLAlchemyError
from typing import Tuple, Dict, List
import html

class SearchService(CacheService):
    def __init__(self) -> None:
        super().__init__()
    
    @staticmethod
    def __get_apps_for_strings(str_ids: List[int]) -> Dict[int, List[str]]:
        """Retrieve a list of applications associated with given string IDs.

        Args:
            str_ids (List[int]): A list of string identifiers for which applications are being fetched.

        Returns:
            Dict[int, List[str]]: A dictionary mapping each string ID to a list of formatted strings 
                                combining platform and application names.
        """
        if not str_ids:
            return {}

        try:
        # Query applications for all provided string IDs in one go
            apps_query = db.session.query(Platform.p_name, Application.app_name, AppString_Namespace.str_id) \
                                   .join(AppString_Namespace, Application.app_id == AppString_Namespace.app_id) \
                                   .join(Platform, Application.p_id == Platform.p_id) \
                                   .filter(AppString_Namespace.str_id.in_(str_ids), AppString_Namespace.deleted == 0) \
                                   .all()

            # Organize the results into a dictionary
            apps_dict = {}
            for p_name, app_name, str_id in apps_query:
                if str_id not in apps_dict:
                    apps_dict[str_id] = set()
                apps_dict[str_id].add(f'{p_name}-{app_name}')

            return apps_dict

        except Exception as e:
            logger.error(f"Error fetching apps for string IDs {str_ids}: {str(e)}", exc_info=True)
            return {}
    
    @staticmethod
    def __format_result(query_results: Tuple, include_namespace: bool=True) -> Dict:
        """
        Format query results into a structured dictionary.

        Args:
            query_results (Tuple): Database query results containing string information.
            include_namespace (bool, optional): Whether to include namespace in the result. Defaults to True.

        Returns:
            Dict: Formatted result containing string data and status code.
        """
        result = {'status': 200, 'data': {}}
        str_ids = [row.str_id for row in query_results]

        for row in query_results:
            str_id = row.str_id
            if str_id not in result['data']:
                result['data'][str_id] = {
                    'note': row.note,
                    'translations': {},
                }

                if include_namespace:
                    result['data'][str_id]['namespace'] = row.namespace_name

        # Fetch applications for all string IDs at once
        apps_for_strings = SearchService.__get_apps_for_strings(str_ids)

        for row in query_results:
            str_id = row.str_id
            result['data'][str_id]['translations'][row.lang_tag] = html.escape(row.content) if row.content else row.content
            result['data'][str_id]['app'] = list(apps_for_strings.get(str_id, set()))
        
        result['status'] = 404 if not query_results else result['status']
        return result

    @staticmethod
    def __base_query():
        """Construct the base query for string searches."""
        return db.session.query(String.str_id, String.note, Language.lang_tag, StringLanguage.content,
                                Application.app_name, Platform.p_name.label('platform_name')) \
                         .join(StringLanguage, String.str_id==StringLanguage.str_id) \
                         .join(Language, StringLanguage.lang_id==Language.lang_id) \
                         .join(AppString_Namespace, String.str_id==AppString_Namespace.str_id) \
                         .join(Application, AppString_Namespace.app_id==Application.app_id) \
                         .join(Platform, Application.p_id==Platform.p_id)

    @staticmethod
    def __log_base_query():
        """Construct the base query for retrieving log entries."""
        return db.session.query(Log.log_id, User.name, Action_Type.type_name, Log.log, Log.time) \
                         .join(User, User.u_id==Log.u_id) \
                         .join(Action_Type, Action_Type.type_id==Log.type_id)
    
    @staticmethod
    def __build_logs_result(data: Tuple) -> Dict:
        """Transform the retrieved log data into a structured dictionary format."""
        return {
            row.log_id: {
                'username': row.name,
                'type': row.type_name,
                'log': row.log,
                'time': row.time.strftime('%Y/%m/%d %H:%M:%S'),
            } 
            for row in data
        }
    
    def __escape_characters(self, string: str) -> str:
        """Escape special characters in a string for SQL queries."""
        return string.strip().replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')

    @CacheService.cache_search_results(prefix='stringid_search', timeout=1800)
    def process_stringid_search(self, data: Dict) -> Response:
        """Process a search request based on string IDs."""
        try:
            stringids = [sid.strip() for sid in data['stringids'].replace(',', ' ').split() if sid.strip().isdigit()]
            if not stringids:
                return jsonify({'msg': '請提供有效的String ID(s)'}), 400
            
            query = self.__base_query().filter(StringLanguage.str_id.in_(stringids))
            result = self.__format_result(query.all(), False)

            return jsonify(result), result['status']
        except SQLAlchemyError as e:
            logger.error(f"Error in process_stringid_search: {str(e)}", exc_info=True)
            return jsonify({'msg': str(e)}), 500

    @CacheService.cache_search_results(prefix='string_search', timeout=1800)
    def process_string_search(self, data: Dict) -> Response:
        """Process a string search request with various filters and options."""
        try:
            search_string = self.__escape_characters(data['search_string'])
            if not search_string:
                return jsonify({'msg': 'Invalid Input'}), 400
            search_string = f'%{search_string.strip()}%' if data['fuzzy_search'] else search_string.strip()
            
            content_filter = (
                StringLanguage.content.ilike(search_string) 
                if not data['case_sensitive'] 
                else StringLanguage.content.like(search_string, escape='\\')
            )

            matching_str_ids = db.session.query(String.str_id).distinct() \
                                         .join(StringLanguage, String.str_id==StringLanguage.str_id) \
                                         .join(AppString_Namespace, String.str_id==AppString_Namespace.str_id) \
                                         .join(Application, AppString_Namespace.app_id==Application.app_id) \
                                         .filter(content_filter)
            
            filters = []
            if data['platform_id'] != '-1':
                filters.append(Application.p_id==data['platform_id'])
            if data['app_id'] != '-1':
                filters.append(Application.app_id==data['app_id'])
            if data['language_id']:
                filters.append(StringLanguage.lang_id==data['language_id'])
            
            matching_str_ids = matching_str_ids.filter(*filters) \
                                               .subquery()

            query = self.__base_query().join(matching_str_ids, String.str_id==matching_str_ids.c.str_id) \
                                       .yield_per(100)
                                       
            result = self.__format_result(query.all(), False)

            return jsonify(result), result['status']
        except SQLAlchemyError as e:
            logger.error(f"Error in process_string_search: {str(e)}", exc_info=True)
            return jsonify({'msg': str(e)}), 500

    @CacheService.cache_search_results(prefix='namespace_search', timeout=1800)
    def process_namespace_search(self, data: Dict) -> Response:
        """
        Process a namespace search request with fuzzy search option.

        Args:
            data (Dict): A dictionary containing search parameters including 'namespace' and 'fuzzy_search'.

        Returns:
            Response: JSON response with search results or error message.
        """
        try:
            search_namespace = self.__escape_characters(data['namespace'])
            if not search_namespace:
                return jsonify({'msg': 'Invalid Input'}), 400
            search_namespace = f'%{search_namespace.strip()}%' if data['fuzzy_search'] else search_namespace.strip()
            
            matching_namespace_ids = db.session.query(Namespace.namespace_id).distinct() \
                                               .filter(Namespace.name.like(search_namespace)) \
                                               .subquery()

            query = self.__base_query() \
                        .add_columns(Namespace.name.label('namespace_name')) \
                        .join(matching_namespace_ids, AppString_Namespace.namespace_id==matching_namespace_ids.c.namespace_id) \
                        .join(Namespace, AppString_Namespace.namespace_id==Namespace.namespace_id) \
                        .yield_per(100)
                        
            result = self.__format_result(query.all())

            return jsonify(result), result['status']
        except SQLAlchemyError as e:
            logger.error(f"Error in process_namespace_search: {str(e)}", exc_info=True)
            return jsonify({'msg': str(e)}), 500

    @CacheService.cache_search_results(prefix='app_search', timeout=1800)
    def process_app_search(self, data: Dict) -> Response:
        """
        Process an application search request with various filters.

        Args:
            data (Dict): A dictionary containing search parameters including 'platform_id', 'app_id', 
                        'not_fill', and 'language_id'.

        Returns:
            Response: JSON response with search results or error message.
        """
        try:
            # Generate cache key from query parameters
            query_args = {
                'platform_id': data.get('platform_id'),
                'app_id': data.get('app_id'),
                'not_fill': data.get('not_fill'),
                'language_id': data.get('language_id')
            }

            # Try to get cached results
            cached_result = self.get_cached_query('app_search', query_args)
            if cached_result is not None:
                return jsonify(cached_result), cached_result['status']

            # If no cache, execute query
            filters = []
            if data['platform_id'] != '-1':
                filters.append(Platform.p_id==data['platform_id'])
            if data['app_id'] != '-1':
                filters.append(Application.app_id==data['app_id'])
            if data['not_fill'] and data['language_id']:
                unfilled_str_ids = db.session.query(String.str_id) \
                                            .outerjoin(StringLanguage, 
                                                        (String.str_id==StringLanguage.str_id) & 
                                                        (StringLanguage.lang_id==data['language_id'])) \
                                            .filter((StringLanguage.content=='') | 
                                                    (StringLanguage.content==None)) \
                                            .subquery()
                
                filters.append(String.str_id.in_(unfilled_str_ids))

            base_results = self.__base_query().filter(*filters) \
                                            .filter(AppString_Namespace.deleted == 0) \
                                            .yield_per(100) 

            result = self.__format_result(base_results.all(), False)
            
            # Cache the results
            # self.cache_service.cache_query_result('app_search', query_args, result, timeout=1800)
            
            return jsonify(result), result['status']
        except SQLAlchemyError as e:
            logger.error(f"Error in process_app_search: {str(e)}", exc_info=True)
            return jsonify({'msg': str(e)}), 500
        
    def search_stringid_diff_log(self, string_id: int) -> Response:
        """
        Search for the difference log of a specific string ID.

        Args:
            string_id (int): The ID of the string to search for.

        Returns:
            Response: JSON response with the difference log or error message.
        """
        try:
            sub_query = db.session.query(String_Update_Log.lang_id, db.func.max(String_Update_Log.updated_time).label('time')) \
                                  .filter(String_Update_Log.str_id==string_id,
                                          String_Update_Log.deleted==0,
                                          String_Update_Log.lang_id!=1) \
                                  .group_by(String_Update_Log.lang_id) \
                                  .subquery()
                                
            query = db.session.query(Language.lang_id, Language.chinese_name, String_Update_Log.old_value, String_Update_Log.new_value) \
                              .join(sub_query, (String_Update_Log.lang_id==sub_query.c.lang_id) &
                                    (String_Update_Log.updated_time==sub_query.c.time)) \
                              .join(Language, Language.lang_id==String_Update_Log.lang_id) \
                              .filter(String_Update_Log.deleted==0,
                                      String_Update_Log.str_id==string_id).all()
            if query:
                result = {
                    'status': 200,
                    'data': [{
                        'str_id': string_id,
                        'lang_id': entry.lang_id,
                        'lang_name': entry.chinese_name,
                        'old_value': entry.old_value,
                        'new_value': entry.new_value,
                    } for entry in query]
                }
                return jsonify(result), result['status']

            return jsonify({'msg': 'Not Found'}), 404
        except Exception as e:
            logger.error(f"Error in search_stringid_diff_log for string_id={string_id}: {str(e)}", exc_info=True)
            return jsonify({'error': str(e)}), 500

    def search_log(self, data: Dict) -> Response:
        """
        Search for log entries based on specified criteria.

        Args:
            data (Dict): Contains 'content' to search for and 'search_type' to determine the filter.

        Returns:
            Response: JSON response with logs or error messages
        """
        try:
            filters = []
            content = data.get('content').strip()
            search_type = data.get('search_type')
            
            if content != None:
                if search_type == 'record_event':
                    filters.append(Log.log.ilike(f'%{content}%'))
                elif search_type == 'username':
                    filters.append(User.name.ilike(f'%{content}%'))
                elif search_type == 'type':
                    filters.append(Action_Type.type_name.ilike(f'%{content}%'))
                else:
                    return jsonify({
                        'msg': "Invalid request"
                    }), 400

            query = self.__log_base_query().filter(*filters)
            logs = query.all()
            if not logs:
                return jsonify({
                    'msg': 'Log Not Found'
                }), 404
            result = self.__build_logs_result(logs)
            return jsonify(result), 200
        except SQLAlchemyError as e:
            logger.error(f"Database error occurred during search_log: {str(e)}", exc_info=True)
            return jsonify({'msg': 'Internal server error'}), 500
        except Exception as e:
            logger.error(f"Unexpected error occurred during search_log: {str(e)}", exc_info=True)
            return jsonify({'msg': 'Internal server error'}), 500

    def search_asn_namespace(self, app_id:int, str_id: int) -> Response:
        try:
            query = db.session.query(AppString_Namespace.asn_id, AppString_Namespace.namespace_id, Namespace.name) \
                            .join(Namespace, Namespace.namespace_id==AppString_Namespace.namespace_id) \
                            .filter(AppString_Namespace.app_id==app_id,
                                    AppString_Namespace.str_id==str_id,
                                    AppString_Namespace.deleted==0) \
                            .all()

            if query:
                result = {}
                for row in query:
                    if row.asn_id not in result:
                        result[row.asn_id] = row.name

                return jsonify(result), 200
            else:
                return jsonify({'msg': 'App string not Found.'}), 404
        except SQLAlchemyError as e:
            logger.error(f"Database error occurred during search_asn_namespace: {str(e)}", exc_info=True)
            return jsonify({'msg': 'Internal server error'}), 500
        except Exception as e:
            logger.error(f"Unexpected error occurred during search_asn_namespace: {str(e)}", exc_info=True)
            return jsonify({'msg': 'Internal server error'}), 500