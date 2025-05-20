from server import db
from model.language import Language
from utility.verify_utils import validate_language_data
from flask import jsonify, Response
from typing import Dict

class LanguageService(object):
    
    def __init__(self) -> None:
        pass

    def new_language(self, data: Dict) -> Response:
        """Create a new language entry in the database."""
        validation_error = validate_language_data(data)
        if validation_error:
            return validation_error
        try:
            language = Language(data['tag'], data['en'], data['zh'])
            db.session.add(language)
            db.session.commit()
            return jsonify({'msg': 'success'}), 201
        except Exception as e:
            return jsonify({'msg': 'Database error: ' + str(e)}), 500
        
    def get_language_info(self, lang_id: int) -> Response:
        """Retrieve language information by ID."""
        lang_info = Language.query.filter_by(lang_id = lang_id).first()
        
        if lang_info is None:
            return jsonify({'msg': 'Language not found'}), 404
        data = {}
        data['tag'] = lang_info.lang_tag
        data['en'] = lang_info.lang_name
        data['zh'] = lang_info.chinese_name
        return jsonify(data), 200

    def modify_language(self, data: Dict) -> Response:
        """Update language information in the database."""
        validation_error = validate_language_data(data)
        if validation_error:
            return validation_error
        
        if 'lang_id' not in data:
            return jsonify({'msg': 'Missing lang_id'}), 400
        try:
            lang = Language.query.filter_by(lang_id = data['lang_id']).first()
            if lang is None:
                return jsonify({'msg': 'Language not found'}), 404
            lang.lang_tag = data['tag']
            lang.lang_name = data['en']
            lang.chinese_name = data['zh']
            db.session.commit()
            return jsonify({'msg': 'success'}), 200
        except Exception as e:
            return jsonify({'msg': 'Database error: ' + str(e)}), 500
