from flask import request
from services.app_service import AppService
from . import app_bp
from .auth import check_permission

@app_bp.route('/apps/<int:p_id>', methods=['GET'])
@check_permission()
def get_all_apps(p_id: int):
    return app_service.get_all_apps(p_id)

@app_bp.route('/app/<int:app_id>', methods=['GET'])
def get_app_info(app_id: int):
    return app_service.get_app_info(app_id)

@app_bp.route('/app/<int:app_id>', methods=['PATCH'])
@check_permission()
def update_app(app_id: int):
    data = request.get_json()
    data['app_id'] = app_id
    return app_service.update_app(data)

@app_bp.route('/app', methods=['POST'])
@check_permission()
def create_app():
    data = request.get_json()
    return  app_service.create_app(data)

app_service = AppService()