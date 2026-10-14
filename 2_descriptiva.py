"""
=============================================================================
PROYECTO: ESTADÍSTICA BIVARIADA - CONSULTORA MÉDICA
SCRIPT: 2_descriptiva.py
PROPÓSITO:
  Análisis Estadístico Descriptivo (Univariado) de Tiempos de Atención Médica.
=============================================================================
"""

import math
import time
import os
import sys
import db

# Asegurar codificación utf-8 en salidas de consola en Windows
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

def obtener_conexion():
    """
    Obtiene una conexión desde el pool definido en db.py.
    """
    return db.get_connection()


def calcular_estadisticas_univariadas(valores):
    """
    Calcula Media muestral, Varianza muestral, Desvío Estándar y Coeficiente de Variación.
    """
    n = len(valores)
    if n < 2:
        return None
    
    media = sum(valores) / n
    suma_cuadrados = sum((x - media) ** 2 for x in valores)
    varianza = suma_cuadrados / (n - 1)
    desviacion = math.sqrt(varianza)
    cv = (desviacion / media) * 100.0 if media != 0 else 0.0
    
    return {
        "n": n,
        "media": media,
        "varianza": varianza,
        "desviacion": desviacion,
        "cv": cv
    }


def clasificar_homogeneidad(cv):
    """
    Interpreta el Coeficiente de Variación (CV).
    """
    if cv < 15.0:
        return "ALTA HOMOGENEIDAD (Excelente estabilidad operativa)", "BAJA"
    elif cv <= 30.0:
        return "VARIABILIDAD MODERADA (Aceptable, requiere monitoreo)", "MEDIA"
    else:
        return "ALTA DISPERSIÓN (Inconsistente, potencial cuello de botella)", "ALTA"


def obtener_datos_descriptivos(conexion=None):
    """
    Ejecuta el análisis descriptivo univariado leyendo exclusivamente de la tabla 'turnos' en tiempo real.
    """
    t_inicio = time.perf_counter()
    cerrar_conexion = False
    
    if conexion is None:
        conexion = obtener_conexion()
        cerrar_conexion = True

    try:
        cursor = conexion.cursor()

        # 1. Obtener lista de doctores
        cursor.execute("SELECT id_doctor, nombre, especialidad, anios_experiencia FROM doctores ORDER BY id_doctor ASC;")
        doctores_raw = cursor.fetchall()

        doctores_resumen = []
        todos_los_tiempos = []

        for doc in doctores_raw:
            id_doc = doc[0]
            nombre = doc[1]
            esp = doc[2]
            exp = doc[3]

            # Leer exclusivamente de turnos en tiempo real
            cursor.execute("SELECT tiempo_estimado_min FROM turnos WHERE id_doctor = %s;", (id_doc,))
            filas_t = cursor.fetchall()
            tiempos_doc = [f[0] for f in filas_t if f[0] is not None]

            todos_los_tiempos.extend(tiempos_doc)

            st = calcular_estadisticas_univariadas(tiempos_doc)
            if st:
                diagnostico, riesgo = clasificar_homogeneidad(st["cv"])
                doctores_resumen.append({
                    "id_doctor": id_doc,
                    "nombre": nombre,
                    "especialidad": esp,
                    "anios_experiencia": exp,
                    "n": st["n"],
                    "media": st["media"],
                    "varianza": st["varianza"],
                    "desviacion": st["desviacion"],
                    "cv": st["cv"],
                    "diagnostico": diagnostico,
                    "nivel_riesgo": riesgo
                })
            else:
                doctores_resumen.append({
                    "id_doctor": id_doc,
                    "nombre": nombre,
                    "especialidad": esp,
                    "anios_experiencia": exp,
                    "n": len(tiempos_doc),
                    "media": 0,
                    "varianza": 0,
                    "desviacion": 0,
                    "cv": 0,
                    "diagnostico": "Sin turnos suficientes (n < 2)",
                    "nivel_riesgo": "N/D"
                })

        t_fin = time.perf_counter()
        tiempo_computo_ms = (t_fin - t_inicio) * 1000

        stats_general = calcular_estadisticas_univariadas(todos_los_tiempos)
        if stats_general:
            interp_gral, nivel_riesgo_gral = clasificar_homogeneidad(stats_general["cv"])
        else:
            stats_general = {"n": len(todos_los_tiempos), "media": 0, "varianza": 0, "desviacion": 0, "cv": 0}
            interp_gral, nivel_riesgo_gral = "N/D", "N/D"

        doctores_ordenados = sorted([d for d in doctores_resumen if d["n"] >= 2], key=lambda x: x["cv"])
        doc_mas_homogeneo = doctores_ordenados[0] if doctores_ordenados else None
        doc_mas_disperso = doctores_ordenados[-1] if doctores_ordenados else None

        cursor.close()

        return {
            "n_total": len(todos_los_tiempos),
            "tiempo_computo_ms": tiempo_computo_ms,
            "general": stats_general,
            "diagnostico_general": interp_gral,
            "nivel_riesgo_general": nivel_riesgo_gral,
            "doctores": doctores_resumen,
            "doc_mas_homogeneo": doc_mas_homogeneo,
            "doc_mas_disperso": doc_mas_disperso
        }
    finally:
        if cerrar_conexion and conexion:
            conexion.close()


def calcular_estadisticas_doctor(id_doctor, conexion=None):
    """
    Calcula y retorna un diccionario con las estadísticas del doctor.
    Wrapper para compatibilidad con llamadas externas.
    """
    return obtener_datos_doctor(id_doctor, conexion=conexion)


def obtener_datos_doctor(id_doctor, conexion=None):
    """
    Obtiene la información descriptiva individual de un especialista leyendo de 'turnos'.
    """
    cerrar_conexion = False
    if conexion is None:
        conexion = obtener_conexion()
        cerrar_conexion = True

    try:
        cursor = conexion.cursor()
        cursor.execute("SELECT id_doctor, nombre, especialidad, anios_experiencia FROM doctores WHERE id_doctor = %s;", (id_doctor,))
        doc_row = cursor.fetchone()
        if not doc_row:
            return None

        # Obtener turnos exclusivos de este doctor
        sql_t = "SELECT id_turno, edad_paciente, tiempo_estimado_min, fecha_turno FROM turnos WHERE id_doctor = %s;"
        cursor.execute(sql_t, (id_doctor,))
        turnos_rows = cursor.fetchall()
        cursor.close()

        registros = []
        tiempos = []

        for f in turnos_rows:
            registros.append({
                "id": f[0],
                "edad": f[1],
                "tiempo": f[2],
                "fecha": str(f[3])
            })
            if f[2] is not None:
                tiempos.append(f[2])

        st = calcular_estadisticas_univariadas(tiempos) if len(tiempos) >= 2 else None
        diagnostico, riesgo = clasificar_homogeneidad(st["cv"]) if st else ("Sin turnos suficientes", "N/D")

        return {
            "id_doctor": doc_row[0],
            "nombre": doc_row[1],
            "especialidad": doc_row[2],
            "anios_experiencia": doc_row[3],
            "n": st["n"] if st else len(tiempos),
            "media": st["media"] if st else (sum(tiempos)/len(tiempos) if tiempos else 0),
            "varianza": st["varianza"] if st else 0,
            "desviacion": st["desviacion"] if st else 0,
            "cv": st["cv"] if st else 0,
            "diagnostico": diagnostico,
            "nivel_riesgo": riesgo,
            "consultas": registros
        }
    finally:
        if cerrar_conexion and conexion:
            conexion.close()


def main():
    print("=" * 80)
    print("  CONSULTORA MÉDICA - AUDITORÍA ESTADÍSTICA DESCRIPTIVA (Tiempo Real)")
    print("=" * 80)
    datos = obtener_datos_descriptivos()
    print(f"Total registros en turnos: {datos['n_total']}")


if __name__ == "__main__":
    main()
