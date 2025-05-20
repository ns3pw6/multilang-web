from . import check_bp
from services.check_service import CheckService
from .auth import check_permission

@check_bp.route('/check/<int:app_id>', methods=['POST'])
@check_permission()
def check(app_id: int):
    return check_service.check_app_strings(app_id)

check_service = CheckService()