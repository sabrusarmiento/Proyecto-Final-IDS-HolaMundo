from database.db import query_db, modify_db


def get_all_exams(filters):
    try:
        id_curso = filters.get('id_curso')

        sql = """
            SELECT 
                e.id_evaluacion,
                e.id_tipo,
                e.id_curso,
                e.id_usuario,
                e.fecha,
                e.asociacion,
                t.nombre AS nombre
            FROM evaluaciones e
            JOIN tipos_evaluacion t ON e.id_tipo = t.id_tipo
        """
        params = []

        if id_curso:
            sql += " WHERE e.id_curso = %s"
            params.append(id_curso)
        
        sql += " ORDER BY e.id_evaluacion ASC"

        result = query_db(sql, params)

        return {
            "ok": True, 
            "data": result if result else []
            }
    except Exception as e:
        return {
            "ok": False, 
            "code": 500, 
            "message": "Internal Server Error", 
            "description": str(e)
            }


def get_exam_by_id(id_exam):
    try:
        sql = "SELECT id_tipo, id_usuario, fecha FROM evaluaciones WHERE id_evaluacion = %s"
        result = query_db(sql, (id_exam,))

        if not result:
            return {
                "ok": False, 
                "code": 404, 
                "message": "Not Found",
                "description": f"No existe una evaluación con ID {id_exam}"
                }

        return {"ok": True, "data": result}
    except Exception as e:
        return {
            "ok": False, 
            "code": 500, 
            "message": "Internal Server Error", 
            "description": str(e)
            }


def create_exam(data):
    try:
        id_usuario = data.get('id_usuario')
        fecha      = data.get('fecha')
        id_curso   = data.get('id_curso')
        nombre     = data.get('nombre')
        asociacion = data.get('asociacion', 'Individual')

        if not nombre:
            return {
                "ok": False, 
                "code": 400, 
                "message": "Bad Request",
                "description": "El nombre de la evaluacion es requerido"
                }
        if not id_curso:
            return {
                "ok": False, 
                "code": 400, 
                "message": "Bad Request",
                "description": "El id_curso es requerido"
                }

        sql_tipo = """
            INSERT INTO tipos_evaluacion (nombre)
            VALUES (%s)
            ON DUPLICATE KEY UPDATE nombre = nombre
        """
        modify_db(sql_tipo, (nombre,))

        result_tipo = query_db(
            "SELECT id_tipo FROM tipos_evaluacion WHERE nombre = %s LIMIT 1",
            (nombre,)
        )
        if not result_tipo:
            return {
                "ok": False, 
                "code": 500, 
                "message": "Internal Server Error",
                "description": "No se pudo obtener el tipo de evaluacion"
                }

        id_tipo_real = result_tipo[0]['id_tipo']

        if not id_usuario:
            fallback = query_db("SELECT id_usuario FROM usuarios LIMIT 1", [])
            id_usuario = fallback[0]['id_usuario'] if fallback else None

        if not id_usuario:
            return {
                "ok": False, 
                "code": 400, 
                "message": "Bad Request",
                "description": "No se pudo determinar el usuario que crea la evaluacion"
                }

        ya_existe = query_db(
            """
            SELECT e.id_evaluacion
            FROM evaluaciones e
            JOIN tipos_evaluacion t ON e.id_tipo = t.id_tipo
            WHERE e.id_curso = %s AND t.nombre = %s
            """,
            (id_curso, nombre)
        )
        if ya_existe:
            return {
                "ok": False,
                "code": 409,
                "message": "Conflict",
                "description": f"Ya existe una evaluación llamada '{nombre}' en este curso"
            }

        sql = """
            INSERT INTO evaluaciones (id_tipo, id_usuario, fecha, id_curso, asociacion)
            VALUES (%s, %s, %s, %s, %s)
        """
        modify_db(sql, (id_tipo_real, id_usuario, fecha, id_curso, asociacion))

        return {
            "ok": True, 
            "message": "Evaluacion creada con exito"
            }
    except Exception as e:
        return {
            "ok": False, 
            "code": 400, 
            "message": "Bad Request", 
            "description": str(e)
            }


def patch_exam_by_id(id_exam, data):
    try:
        id_type = data.get('id_tipo')
        id_user = data.get('id_usuario')
        date    = data.get('fecha')

        updates = []
        params  = []

        if id_type is not None:
            updates.append("id_tipo = %s")
            params.append(id_type)
        if id_user is not None:
            updates.append("id_usuario = %s")
            params.append(id_user)
        if date is not None:
            updates.append("fecha = %s")
            params.append(date)

        if not updates:
            return {
                "ok": False, 
                "code": 400, 
                "message": "Bad Request",
                "description": "No se enviaron campos para actualizar"
                }

        sql = f"UPDATE evaluaciones SET {', '.join(updates)} WHERE id_evaluacion = %s"
        params.append(id_exam)

        modify_row = modify_db(sql, params)
        if modify_row == 0:
            return {
                "ok": False, 
                "code": 404, 
                "message": "Not Found",
                "description": f"No hay una evaluacion con el id {id_exam} para actualizar"
                }

        return {
            "ok": True, 
            "message": "Evaluacion actualizada con exito", 
            "id_evaluacion": id_exam
            }
    except Exception as e:
        return {
            "ok": False, 
            "code": 400, 
            "message": 
            "Bad Request", "description": str(e)
            }


def delete_exam_by_id(id_exam):
    try:
        modify_db("DELETE FROM notas WHERE id_evaluacion = %s", (id_exam,))

        modify_row = modify_db(
            "DELETE FROM evaluaciones WHERE id_evaluacion = %s",
            (id_exam,)
        )

        if modify_row == 0:
            return {
                "ok": False, 
                "code": 404, 
                "message": "Not Found",
                "description": f"No se encontro la evaluacion con el ID {id_exam}."
                }

        return {
            "ok": True, 
            "message": f"Evaluacion con ID {id_exam} eliminada correctamente"
            }
    except Exception as e:
        return {
            "ok": False, 
            "code": 500, 
            "message": "Internal Server Error", 
            "description": str(e)
            }


def save_notes_to_db(id_exam, notes_dict, id_corrector, correctores_dict=None):
    try:
        corrector_nombre = None
        if id_corrector:
            user_result = query_db(
                "SELECT nombre, apellido FROM usuarios WHERE id_usuario = %s",
                (id_corrector,)
            )
            if user_result:
                corrector_nombre = f"{user_result[0]['nombre']} {user_result[0]['apellido']}"

        for id_alumno, nota in notes_dict.items():
            existing = query_db(
                "SELECT nota, corrector_nombre FROM notas WHERE id_alumno = %s AND id_evaluacion = %s",
                (id_alumno, id_exam)
            )

            if existing:
                nota_actual = existing[0]['nota']
                corrector_actual = existing[0]['corrector_nombre']
                if float(nota_actual) == float(nota):
                    final_corrector = corrector_actual
                else:
                    final_corrector = corrector_nombre
            else:
                final_corrector = corrector_nombre

            sql = """
                INSERT INTO notas (id_alumno, id_evaluacion, nota, corrector_nombre)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE 
                    nota = VALUES(nota),
                    corrector_nombre = VALUES(corrector_nombre)
            """
            modify_db(sql, (id_alumno, id_exam, nota, final_corrector))

        return {
            "ok": True
            }
    except Exception as e:
        return {
            "ok": False, 
            "code": 500, 
            "message": "Internal Server Error",
            "description": f"Error al insertar notas en la DB: {str(e)}"
            }


def get_students_with_notes_db(id_curso, limit=None, offset=0, order_by=None, order='ASC'):
    try:
        allowed_order_fields = {'nombre', 'apellido', 'padron'}
        order_clause = ""
        if order_by and order_by in allowed_order_fields:
            direction = 'DESC' if str(order).upper() == 'DESC' else 'ASC'
            order_clause = f"ORDER BY a.{order_by} {direction}"
        else:
            order_clause = "ORDER BY a.apellido ASC, a.nombre ASC"

        sql = f"""
            SELECT 
                a.id_alumno, a.nombre, a.apellido, a.padron, a.correo,
                a.estado_alumno,
                e.nombre_equipo AS equipo,
                IFNULL(GROUP_CONCAT(
                    CONCAT(n.id_evaluacion, ':', n.nota)
                    ORDER BY n.id_evaluacion SEPARATOR ','
                ), '') AS notas_raw,
                IFNULL(GROUP_CONCAT(
                    CONCAT(n.id_evaluacion, ':', IFNULL(n.corrector_nombre, ''))
                    ORDER BY n.id_evaluacion SEPARATOR ','
                ), '') AS correctores_raw
            FROM alumnos a
            LEFT JOIN equipo_alumno ea ON a.id_alumno = ea.id_alumno
            LEFT JOIN equipos e ON ea.id_equipo = e.id_equipo
            LEFT JOIN notas n ON a.id_alumno = n.id_alumno
            WHERE a.id_curso = %s
            GROUP BY a.id_alumno, a.nombre, a.apellido, a.padron, a.estado_alumno, e.nombre_equipo
            {order_clause}
        """

        count_sql = "SELECT COUNT(*) as total FROM alumnos WHERE id_curso = %s"
        total = query_db(count_sql, (id_curso,))[0]['total']

        params = [id_curso]
        if limit is not None:
            sql += " LIMIT %s OFFSET %s"
            params += [int(limit), int(offset)]

        result = query_db(sql, params)
        return {
            "ok": True,
            "data": result if result else [],
            "total": total
        }
    except Exception as e:
        return {
            "ok": False,
            "code": 500,
            "message": "Internal Server Error",
            "description": f"Error al obtener reporte: {str(e)}"
        }


def get_promocion_config_db(id_curso):
    try:
        flag = query_db(
            "SELECT es_promocionable, cuenta_asistencia, porcentaje_asistencia FROM curso_promocion_config WHERE id_curso = %s",
            (id_curso,)
        )
        es_promocionable   = flag[0]['es_promocionable']      if flag else False
        cuenta_asistencia  = bool(flag[0]['cuenta_asistencia']) if flag else False
        pct_asistencia     = float(flag[0]['porcentaje_asistencia']) if flag else 75.0

        detalle = query_db(
            """
            SELECT id_evaluacion, cuenta_para_promocion, nota_minima
            FROM configuracion_promocion
            WHERE id_curso = %s
            """,
            (id_curso,)
        )

        return {
            "ok": True,
            "data": {
                "es_promocionable":      bool(es_promocionable),
                "cuenta_asistencia":     cuenta_asistencia,
                "porcentaje_asistencia": pct_asistencia,
                "evaluaciones":          detalle or []
            }
        }
    except Exception as e:
        return {
            "ok": False,
            "code": 500,
            "message": "Internal Server Error",
            "description": str(e)
        }


def save_promocion_config_db(id_curso, es_promocionable, evaluaciones, cuenta_asistencia=False, porcentaje_asistencia=75.0):
    try:
        modify_db(
            """
            INSERT INTO curso_promocion_config (id_curso, es_promocionable, cuenta_asistencia, porcentaje_asistencia)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
                es_promocionable      = VALUES(es_promocionable),
                cuenta_asistencia     = VALUES(cuenta_asistencia),
                porcentaje_asistencia = VALUES(porcentaje_asistencia)
            """,
            (id_curso, bool(es_promocionable), bool(cuenta_asistencia), float(porcentaje_asistencia))
        )

        for ev in evaluaciones:
            id_eval  = ev.get('id_evaluacion')
            cuenta   = bool(ev.get('cuenta', ev.get('cuenta_para_promocion', False)))
            nota_raw = ev.get('nota_minima', None)
            nota_min = float(nota_raw) if nota_raw is not None else None
            try:
                nota_min = float(nota_min)
            except (ValueError, TypeError):
                nota_min = None

            modify_db(
                """
                INSERT INTO configuracion_promocion
                    (id_curso, id_evaluacion, es_promocionable, cuenta_para_promocion, nota_minima)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    cuenta_para_promocion = VALUES(cuenta_para_promocion),
                    nota_minima           = VALUES(nota_minima),
                    es_promocionable      = VALUES(es_promocionable)
                """,
                (id_curso, id_eval, bool(es_promocionable), cuenta, nota_min)
            )

        return {"ok": True, "message": "Configuración de promoción guardada correctamente"}
    except Exception as e:
        return {
            "ok": False,
            "code": 500,
            "message": "Internal Server Error",
            "description": str(e)
        }