from flask import render_template, redirect, url_for, session, abort, request
from routes.login import login_bp
from routes.page import userpage_bp
from routes.app import app_bp
from routes.upload import upload_bp
from routes.language import lang_bp
from routes.search import search_bp
from routes.update import update_bp
from routes.download import download_bp
from routes.proofread import proofread_bp
from routes.check import check_bp
from server import app

# Read app basic config
BASE_URL = app.config['BASE_URL']

# regist routes
app.register_blueprint(login_bp, url_prefix = BASE_URL)
app.register_blueprint(userpage_bp, url_prefix = BASE_URL)
app.register_blueprint(app_bp, url_prefix = BASE_URL)
app.register_blueprint(upload_bp, url_prefix = BASE_URL)
app.register_blueprint(lang_bp, url_prefix = BASE_URL)
app.register_blueprint(search_bp, url_prefix = BASE_URL)
app.register_blueprint(update_bp, url_prefix = BASE_URL)
app.register_blueprint(download_bp, url_prefix = BASE_URL)
app.register_blueprint(proofread_bp, url_prefix = BASE_URL)
app.register_blueprint(check_bp, url_prefix = BASE_URL)

# Return to homepage
@app.route('/')
def index():
    return redirect(BASE_URL)

# Return page base on seesion username
@app.route(BASE_URL + '/')
def mlw():
    if 'username' in session:
        data = {
            'username': session['username'],
            'home': True,
            'url': 'mlw',
        }
        
        return render_template('pages/mainpage.html', **data)
    else:
        return redirect(url_for('login_bp.login'))
    
# Check website is under maintenance mode
@app.before_request
def check_under_maintenance():
    current_path = request.path
    
    if current_path.startswith('/mlw'):
        current_path = current_path[4:]

    if app.config['MAINTENANCE_MODE']:
        if any(current_path.startswith(path) for path in app.config['MAINTENANCE_MODE_WHITELIST']):
            return None
        
        if 'username' in session and session['username'] == app.config['MAINTAINER_NAME']:
            return None
        return render_template('pages/maintenance.html'), 503

@app.errorhandler(401)
def unauthorized(e):
    return render_template('pages/401.html', maintainer=app.config['MAINTAINER_NAME']), 401

@app.errorhandler(404)
def page_not_found(e):
    return render_template('pages/404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('pages/500.html', maintainer=app.config['MAINTAINER_NAME']), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
    # app.run(host='0.0.0.0', port=80, debug=False)