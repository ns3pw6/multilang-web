from . import update_bp
from flask import request, jsonify
from services.update_service import UpdateService
from .auth import check_permission

@update_bp.route('/update', methods=['POST', 'PATCH'])
@check_permission()
def update_string_content():
    data = request.get_json()
    if request.method == 'POST':
        if data['lang_tag'] == 'note':
            return update_service.update_note(data)
        else:
            return update_service.update_string(data)
    elif request.method == 'PATCH':
        return update_service.recover_string(data)
    else:
        return jsonify({'msg': 'Invalid search type'}), 400

@update_bp.route('/update/<int:asn_id>', methods=['PATCH'])
@check_permission()
def remove_string(asn_id):
    if request.method == 'PATCH':
        return update_service.remove_string(asn_id)
    else:
        return jsonify({'msg': 'Invalid search type'}), 400

update_service = UpdateService()