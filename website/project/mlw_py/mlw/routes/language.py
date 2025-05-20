from flask import request, jsonify
from model.language import Language
from . import lang_bp
from .auth import check_permission

@lang_bp.route('/language', methods=['POST'])
@check_permission()
def new_language():
    data = request.get_json()
    return Language.new(data)

@lang_bp.route('/language/<int:lang_id>', methods=['GET'])
@check_permission()
def get_language_info(lang_id):
    return jsonify(Language.get(lang_id))

@lang_bp.route('/language/<int:lang_id>', methods=['PATCH'])
@check_permission()
def modify_language(lang_id):
    data = request.get_json()
    return Language.update(data)
