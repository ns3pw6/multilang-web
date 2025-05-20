from . import upload_bp
from flask import request, jsonify
from services.upload_service import UploadService
from server import app
from .auth import check_permission

@upload_bp.route('/upload/<filename>', methods=['POST'])
@check_permission()
def upload_excel(filename):
    file = request.files['file']
    return upload_service.upload_excel(file, filename)
    
@upload_bp.route('/upload/<int:p_id>/<int:app_id>', methods=['POST'])
def upload_from_svn(p_id, app_id):
    data = request.get_json()
    return upload_service.upload_from_svn(p_id, app_id, data)

@upload_bp.route('/upload/excel', methods=['POST'])
def upload_excel_content():
    data = request.get_json()
    return upload_service.upload_excel_content(data)

@upload_bp.route('/upload', methods=['POST', 'PATCH', 'DELETE'])
def upload():
    data = request.get_json()
    if request.method == 'POST':
        return upload_service.insert_string(data)
    elif request.method == 'PATCH':
        return upload_service.update_string(data)
    elif request.method == 'DELETE':
        return upload_service.remove_string(data)
    return jsonify({'msg': f'未知錯誤!!請告知目前管理員: {app.config["MAINTAINER_NAME"]} !!'})

upload_service = UploadService()