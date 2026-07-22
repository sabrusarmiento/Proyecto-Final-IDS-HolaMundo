from flask import Blueprint, request
from services.mark_service import (
    marks_service,
    mark_service,
    create_mark_service,
    patch_mark_service,
    delete_mark_service
)
from middleware.auth_middleware import require_auth, require_min_admin_level
from helpers.constants import NIVEL_AYUDANTE

marks_bp = Blueprint('marks', __name__)

@marks_bp.route('/marks', methods=['GET'])
def get_marks():

    filters = {
        "id_alumno": request.args.get('id_alumno'),
        "id_evaluacion": request.args.get('id_evaluacion'),
        "id_equipo": request.args.get('id_equipo'),
        "corrector_nombre": request.args.get('corrector_nombre'),
        "nota": request.args.get('nota')
    }
    return marks_service(filters)


@marks_bp.route('/marks/<int:id_mark>', methods=['GET'])
def get_mark(id_mark):
    return mark_service(id_mark)


@marks_bp.route('/marks', methods=['POST'])
@require_auth
@require_min_admin_level(NIVEL_AYUDANTE)
def create_mark():
    data = request.get_json()
    return create_mark_service(data, request.user)


@marks_bp.route('/marks/<int:id_mark>', methods=['PATCH'])
@require_auth
@require_min_admin_level(NIVEL_AYUDANTE)
def patch_mark(id_mark):
    data = request.get_json()
    return patch_mark_service(id_mark, data, request.user)


@marks_bp.route('/marks/<int:id_mark>', methods=['DELETE'])
@require_auth
@require_min_admin_level(NIVEL_AYUDANTE)
def delete_mark(id_mark):
    return delete_mark_service(id_mark, request.user)
