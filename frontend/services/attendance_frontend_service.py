import os
import requests
from config import BASE_URL, get_headers
BASE = os.getenv("BACKEND_URL", "http://127.0.0.1:5000")
from helpers.logger import log_action
from config import get_user

def attendance_get_all(id_clase=None):
    try:
        params = {"id_clase": id_clase} if id_clase else {}
        r = requests.get(f"{BASE}/asistencia", params=params, headers=get_headers())
        return r.json().get("attendance", []) if r.status_code == 200 else []
    except Exception as e:
        print(f"Error: {e}")
        return []

def send_attendance_link(id_clase, horas=None, minutos=None):
    user=get_user()
    try:
        r = requests.post(f"{BASE}/asistencia/enviar-link", json={"id_clase": id_clase, "horas": horas, "minutos": minutos}, headers=get_headers())
        log_action(
            method='POST',
            description=f'Se envio link asistencia de la clase con id {id_clase}',
            user_id=user.get('id_usuario', 'desconocido'),
            user_email=user.get('correo', 'desconocido'),
            status_code=r.status_code
        )
        return r.json()
    except Exception as e:
        print(f"Error: {e}")
        return {"message": "No se pudo enviar el link de asistencia."}

def mark_attendance(payload):
    try:
        r = requests.post(f"{BASE}/asistencia", json=payload)
        return r.json(), r.status_code
    except Exception as e:
        return {"errors": [{"description": str(e)}]}, 502
    
def get_class(id_clase):
    try:
        r = requests.get(f"{BASE_URL}/clases/{id_clase}")
        return r.json().get("class") if r.status_code == 200 else None
    except Exception:
        return None
