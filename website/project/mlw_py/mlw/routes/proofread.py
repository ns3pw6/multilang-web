from flask import request, jsonify, render_template, abort
from services.proofread_service import ProofreadService
from . import proofread_bp
from .auth import check_permission
    
@proofread_bp.route('/proofread', methods=['POST'])
@check_permission()
def new_project():
    if request.method == 'POST':
        data = request.get_json()
        return proofread_service.new_project(data)
    else:
        return jsonify({'msg': 'Invalid method'}), 400

@proofread_bp.route('/proofread/<int:project_id>', methods=['GET', 'POST', 'PATCH', 'DELETE'])
def handle_project_request(project_id):
    if request.method == 'GET':
        project_data, status = proofread_service.get_project_by_id(project_id)
        if status != 200:
            abort(status)
        
        data = {
            'proofread': True,
            'page_title': '中文校對',
            'url': 'userpage_bp.proofread',
        }
        
        return render_template('pages/proofread_project.html', **data, **project_data)
    elif request.method == 'POST':
        string = request.form.get('content')
        data = {
            'project_id': project_id,
            'string': string,
        }
        
        return proofread_service.insert_project_string(data)
    elif request.method == 'PATCH':
        project_name = request.form.get('project-name') or None
        spec_link = request.form.get('spec-link') or None
        data = {
            'project_id': project_id,
            'project_name': project_name,
            'spec_link': spec_link,
        }
        
        return proofread_service.update_project_info(data)
    elif request.method == 'DELETE':
        return proofread_service.delete_project(project_id)
    else:
        return jsonify({'msg': 'Invalid method'}), 400
    
@proofread_bp.route('/proofread/<int:project_id>/<int:ps_id>', methods=['PATCH', 'DELETE'])
@check_permission()
def handle_project_string_request(project_id, ps_id):
    if request.method == 'PATCH':
        data = request.get_json()
        return proofread_service.update_project_string(data)
    elif request.method == 'DELETE':
        return proofread_service.remove_project_string(ps_id)
    else:
        return jsonify({'msg': 'Invalid method'}), 400

@proofread_bp.route('/proofread/log/<int:project_id>', methods=['GET'])
@check_permission()
def get_project_log(project_id):
    return proofread_service.project_update_log(project_id)

@proofread_bp.route('/proofread/updatePersonInCharge/<int:project_id>', methods=['PATCH'])
@check_permission()
def update_person_in_charge(project_id):
    return proofread_service.update_person_in_charge(project_id)

@proofread_bp.route('/proofread/updateReviewer/<int:project_id>', methods=['PATCH'])
@check_permission()
def update_reviewer(project_id):
    return proofread_service.proofread_finished(project_id)

@proofread_bp.route('proofread/download/<int:proofread_id>', methods=['POST'])
@check_permission()
def download_proofread(proofread_id):
    data, status = proofread_service.get_project_by_id(proofread_id)
    if status != 200:
        return data, status
    
    return proofread_service.download(proofread_id, data.get('strings'))

proofread_service = ProofreadService()