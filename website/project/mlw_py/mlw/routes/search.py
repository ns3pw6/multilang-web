from flask import request, jsonify
from services.search_service import SearchService
from . import search_bp

@search_bp.route('/search', methods=['POST'])
def search():
    search_type = request.form.get('search_type')
    data = {}
    
    if search_type == 'stringid':
        data['stringids'] = request.form.get('stringID')
        
        results = search_service.process_stringid_search(data)
    elif search_type == 'string':
        data['search_string'] = request.form.get('searchString-string')
        data['platform_id'] = request.form.get('searchString-platform_id')
        data['app_id'] = request.form.get('searchString-app_id')
        data['language_id'] = request.form.get('searchString-language')
        data['case_sensitive'] = request.form.get('searchString-case-sensitive') == 'on'
        data['fuzzy_search'] = request.form.get('searchString-fuzzySearchCheck') == 'on'
        
        results = search_service.process_string_search(data)
    elif search_type == 'namespace':
        data['namespace'] = request.form.get('namespace')
        data['fuzzy_search'] = request.form.get('searchNamespace-fuzzySearchCheck') == 'on'
        
        results = search_service.process_namespace_search(data)
    elif search_type == 'app':
        data['platform_id'] = request.form.get('searchApp-platform_id')
        data['app_id'] = request.form.get('searchApp-app_id')
        data['language_id'] = request.form.get('searchApp-language')
        data['not_fill'] = request.form.get('searchapp-checkbox') == 'on'
        
        results = search_service.process_app_search(data)
    else:
        results = jsonify({'msg': 'Invalid search type'}), 400
        
    return results

@search_bp.route('/search/log/<int:string_id>', methods=['POST'])
def search_diff_log(string_id):
    return search_service.search_stringid_diff_log(string_id)

@search_bp.route('/log', methods=['POST'])
def search_log():
    search_type = request.form.get('type')
    content = request.form.get('content')
    data = {
        'search_type': search_type,
        'content': content,
    }
    return search_service.search_log(data)

@search_bp.route('/search/<int:app_id>/<int:str_id>', methods=['POST'])
def search_namespace(app_id, str_id):
    if request.method == 'POST':
        return search_service.search_asn_namespace(app_id, str_id)
    else:
        return jsonify({'msg': 'Invalid search type'}), 400

search_service = SearchService()
