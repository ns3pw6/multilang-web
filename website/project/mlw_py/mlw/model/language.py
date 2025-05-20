from server import db
from flask import jsonify
from model.dbModel import LanguageDB
from utility.verify_utils import validate_language_data

class Language(LanguageDB):
    
    @classmethod
    def get_lang_id_by_tag(cls, tag):
        try:
            lang = cls.query.filter_by(lang_tag=tag).first()

            if lang is None:
                return -1
            lang_id = lang.lang_id
            return lang_id
        except Exception as e:
            return str(e)
    
    @classmethod
    def get_lang_by_tag(cls, tag):
        try:
            lang = cls.query.filter_by(lang_tag=tag).first()

            if lang is None:
                return -1
            lang_name = lang.lang_name
            return lang_name
        except Exception as e:
            return str(e)
        
    @classmethod
    def new(cls, data):
        validation_error = validate_language_data(data)
        if validation_error:
            return validation_error
        try:
            language = cls(data['tag'], data['en'], data['zh'])
            db.session.add(language)
            db.session.commit()
            return jsonify({'msg': 'success'}), 201
        except Exception as e:
            return jsonify({'msg': 'Database error: ' + str(e)}), 500
    
    @classmethod
    def get(cls, lang_id):
        lang_info = cls.query.filter_by(lang_id=lang_id).first()

        if lang_info is None:
            return jsonify({'msg': 'Language not found'}), 404
        data = {}
        data['tag'] = lang_info.lang_tag
        data['en'] = lang_info.lang_name
        data['zh'] = lang_info.chinese_name
        return data
    
    @classmethod
    def get_all(cls):
        try:
            languages = cls.query.all()
            data = {}
            for lang in languages:
                lang_data = {
                    lang.lang_tag: lang.lang_name
                }
                data.update(lang_data)
            return data
        except Exception as e:
            return str(e)
    
    @classmethod
    def update(cls, data):
        validation_error = validate_language_data(data)
        if validation_error:
            return validation_error
        
        # Check if 'lang_id' exists in data
        if 'lang_id' not in data:
            return jsonify({'msg': 'Missing lang_id'}), 404
        try:
            lang = cls.query.filter_by(lang_id = data['lang_id']).first()
            if lang is None:
                return jsonify({'msg': 'Language not found'}), 404
            lang.lang_tag = data['tag']
            lang.lang_name = data['en']
            lang.chinese_name = data['zh']
            db.session.commit()
            return jsonify({'msg': 'success'}), 200
        except Exception as e:
            return jsonify({'msg': 'Database error: ' + str(e)}), 500