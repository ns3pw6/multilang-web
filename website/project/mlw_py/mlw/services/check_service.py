from flask import jsonify, Response
from server import db
from sqlalchemy import text
from model.language import Language
from utility.verify_utils import validate_language_data, process_special_char, compare_special_char, check_app_string_format

class CheckService():
    def __init__(self) -> None:
        pass
    
    def __build_query(self, app_id: int) -> str:
        """Build the SQL query for checking."""
        query = f"""SELECT * FROM string_mapping WHERE app_id = {app_id}"""
        return db.session.execute(text(query))

    def check_app_strings(self, app_id: int) -> Response:
        """Check if the language exists in the database."""
        languages = Language.get_all()
        result_set = self.__build_query(app_id).all()
        if not result_set:
            return jsonify({'msg': 'No strings found for the given app ID'}), 404
        result = check_app_string_format(result_set, languages)
        
        return jsonify({'msg': result}), 200