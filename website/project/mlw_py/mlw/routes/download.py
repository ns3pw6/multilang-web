from . import download_bp
from flask import jsonify, request
from services.download_service import DownloadService
from .auth import check_permission
from datetime import datetime

@download_bp.route('/download', methods = ['POST'])
@check_permission()
def download():
    download_type = request.form.get('download_type')
    data = {}
    
    if download_type == 'due':
        data['p_id'] = request.form.get('select_platform_id')
        data['app_id'] = request.form.get('select_app_id')
        return download_service.download_untranslate_excel(data)
    elif download_type == 'dfe':
        data['p_id'] = request.form.get('select_platform_id')
        data['app_id'] = request.form.get('select_app_id')
        data['lang_id'] = request.form.get('download_language')
        return download_service.download_full_excel(data)
    elif download_type == 'svn':
        data['p_id'] = request.form.get('select_platform_id')
        data['app_id'] = request.form.get('select_app_id')
        return download_service.download_svn(data)
    elif download_type == 'time':
        if not request.form.get('start_time'):
            return jsonify({'msg': '請選擇起始日期'}), 400
        now = datetime.now()
        formatted_time = now.strftime("%Y-%m-%d")
        data['start_time'] = request.form.get('start_time')
        data['end_time'] = request.form.get('end_time') or formatted_time
        return download_service.download_untranslate_by_time(data)
    else:
        return jsonify({'msg': 'Invalid download type'}), 400
    
@download_bp.route('/download/search', methods = ['POST'])
@check_permission()
def download_search():
    data = request.json
    return download_service.download_search(data)

download_service = DownloadService()