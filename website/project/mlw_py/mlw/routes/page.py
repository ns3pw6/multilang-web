from flask import render_template, url_for, redirect, request, abort, session, jsonify
from utility.session_utils import check_session
from model.dbModel import Platform
from model.language import Language
from services.proofread_service import ProofreadService
from . import userpage_bp

@userpage_bp.route('/search', methods=['GET'])
def search():
    if check_session():
        platforms = __get_platform()
        languages = __get_language()
        data = {
            'search': True,
            'page_title': '搜尋',
            'url': 'userpage_bp.search',
            'platforms': platforms,
            'languages': languages,
        }
        
        return  render_template('pages/search.html', **data)
    return redirect(url_for('login_bp.login'))

@userpage_bp.route('/download', methods=['GET'])
def download():
    if check_session():
        platforms = __get_platform()
        languages = __get_language()
        data = {
            'download': True,
            'page_title': '下載',
            'url': 'userpage_bp.download',
            'platforms': platforms,
            'languages': languages,
        }
        
        return render_template('pages/download.html', **data)
    return redirect(url_for('login_bp.login'))

@userpage_bp.route('/upload', methods=['GET'])
def upload():
    if check_session():
        platforms = __get_platform()
        data = {
            'upload': True,
            'page_title': '上傳',
            'url': 'userpage_bp.upload',
            'platforms': platforms,
        }
        
        return render_template('pages/upload.html', **data)
    return redirect(url_for('login_bp.login'))

@userpage_bp.route('/check', methods=['GET'])
def check():
    if check_session():
        platforms = __get_platform()
        languages = __get_language()
        data = {
            'check': True,
            'page_title': '檢查字串格式',
            'url': 'userpage_bp.check',
            'platforms': platforms,
            'languages': languages,
        }
        
        return render_template('pages/check.html', **data)
    return redirect(url_for('login_bp.login'))

@userpage_bp.route('/app_setting', methods=['GET'])
def app_setting():
    if check_session():
        platforms = __get_platform()
        data = {
            'app_setting': True,
            'page_title': 'App新增/修改',
            'url': 'userpage_bp.app_setting',
            'platforms': platforms,
        }
        
        return render_template('pages/app_setting.html', **data)
    return redirect(url_for('login_bp.login'))
    
@userpage_bp.route('/log', methods=['GET'])
def log():
    if check_session():
        data = {
            'log': True,
            'page_title': '字串更新紀錄',
            'url': 'userpage_bp.log',
        }
        
        return render_template('pages/log.html', **data)
    return redirect(url_for('login_bp.login'))

@userpage_bp.route('/proofread', methods=['GET'])
def proofread():
    if check_session():
        search_type = request.args.get('type', default=None)
        content = request.args.get('content', default=None)
        page = int(request.args.get('page', 1))
        per_page = 15 

        query = {
            'search_type': search_type,
            'content': content,
            'page': page,
            'per_page': per_page,
        }
        project_datas, total_projects , status = ProofreadService().get_projects(query)
        if status != 200:
            abort(status)
        
        data = {
            'proofread': True,
            'page_title': '中文校對',
            'url': 'userpage_bp.proofread',
        }
        
        if not project_datas:
            data.update({
                'project_data': {},
                'current_page': page,
                'total_pages': 1,
                'page_range': [1],
            })
        else:
            total_pages = (total_projects // per_page) + (1 if total_projects % per_page > 0 else 0)
            page_range = range(1, total_pages + 1)
            
            data.update({
                'project_data': project_datas,
                'current_page': page,
                'total_pages': total_pages,
                'page_range': page_range,
            })
        
        return render_template('pages/proofread.html', **data)
    return redirect(url_for('login_bp.login'))

@userpage_bp.route('/tutorial', methods=['GET'])
def tutorial():
    if check_session():
        data = {
            'tutorial': True,
            'page_title': '使用說明',
            'url': 'userpage_bp.tutorial',
        }
        
        return render_template('pages/tutorial.html', **data)
    return redirect(url_for('login_bp.login'))

@userpage_bp.route('/translate', methods=['GET'])
def translate():
    if check_session():
        data = {
            'translate': True,
            'page_title': '翻譯',
            'url': 'userpage_bp.translate',
        }
        
        return render_template('pages/translate.html', **data)

@userpage_bp.route('/language', methods=['GET'])
def language():
    if check_session():
        languages = __get_language()
        data = {
            'language': True,
            'page_title': '語言',
            'url': 'userpage_bp.language',
            'languages': languages,
        }
        
        return render_template('pages/language.html', **data)
    
@userpage_bp.route('/set_test_mode', methods=['POST'])
def set_test_mode():
    if check_session():
        test_mode = request.json.get('test_mode', False)
        session['test_mode'] = test_mode
        return jsonify({'status': 'success', 'test_mode': test_mode}), 200
    return redirect(url_for('login_bp.login'))

def __get_language():
    languages = Language.query.order_by(Language.lang_id).all()
    data = {}
    for language in languages:
        data[language.lang_id] = f'{language.lang_name}({language.chinese_name})'
    return data

def __get_platform():
    platforms = Platform.query.order_by(Platform.p_id).all()
    data = {}
    for platform in platforms:
        data[platform.p_id] = platform.p_name
    return data
