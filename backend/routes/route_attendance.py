from flask import Blueprint, request
from services.attendance_service import (
    attendance_get_handler,
    attendance_post_handler,
    attendance_patch_handler,
    attendance_delete_handler,
    send_attendance_link_service, 
)
from middleware.auth_middleware import require_auth, require_min_admin_level
from helpers.constants import NIVEL_AYUDANTE

attendance_bp = Blueprint('attendance', __name__)

@attendance_bp.route("/asistencia", methods=["GET"])
@require_auth
def get_attendance():
    id_clase = request.args.get("id_clase")
    id_alumno = request.args.get("id_alumno")
    return attendance_get_handler(id_clase, id_alumno)

@attendance_bp.route("/asistencia", methods=["POST"])
def post_attendance():
    data = request.get_json()
    return attendance_post_handler(data)

@attendance_bp.route("/asistencia/enviar-link", methods=["POST"])
@require_auth
@require_min_admin_level(NIVEL_AYUDANTE)
def post_send_attendance_link():
    data = request.get_json()
    return send_attendance_link_service(data.get("id_clase"), data.get("horas"), data.get("minutos"), request.user)

@attendance_bp.route("/asistencia/<int:id>", methods=["PATCH"])
@require_auth
def patch_attendance(id):
    data = request.get_json()
    return attendance_patch_handler(id, data)


@attendance_bp.route("/asistencia/<int:id>", methods=["DELETE"])
@require_auth
def delete_attendance(id):
    return attendance_delete_handler(id)