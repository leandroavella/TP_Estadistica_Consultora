"""
=============================================================================
PROYECTO: ESTADÍSTICA BIVARIADA - CONSULTORA MÉDICA
SERVIDOR WEB: app.py (Flask Dashboard Gerencial)
PROPÓSITO:
  Panel de administración y auditoría estadística para el centro médico.
  Integra la lógica de:
    - 1_schema.sql (Persistencia relacional en MariaDB / MySQL)
    - 2_descriptiva.py (Análisis Descriptivo Univariado y Coeficiente de Variación)
    - 3_regresion.py (Regresión Lineal, Pearson r, R², Outliers y Predicción)
=============================================================================
"""

import os
import sys
import math
import importlib
import logging
import db
from datetime import datetime, timedelta
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, flash

load_dotenv()

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configurar encoding en Windows si aplica
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Importación dinámica de los módulos existentes
modulo_descriptiva = importlib.import_module("2_descriptiva")
modulo_regresion = importlib.import_module("3_regresion")

# Inicialización de la aplicación Flask
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
IMG_DIR = os.path.join(STATIC_DIR, "img")

os.makedirs(IMG_DIR, exist_ok=True)
os.makedirs(TEMPLATES_DIR, exist_ok=True)

app = Flask(
    __name__,
    static_folder=STATIC_DIR,
    template_folder=TEMPLATES_DIR
)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "consultora_medica_secret_key_2026_estadistica")

# Ruta para almacenar la imagen del reporte gerencial
RUTA_GRAFICO_STATIC = os.path.join(IMG_DIR, "reporte_bivariado_gerencia.png")
RUTA_GRAFICO_ROOT = os.path.join(BASE_DIR, "reporte_bivariado_gerencia.png")


def obtener_consultas_recientes(limite=15):
    """
    Obtiene los registros más recientes de consultas desde MariaDB
    para el resumen operativo del dashboard principal.
    """
    conexion = db.get_connection()
    try:
        cursor = conexion.cursor()
        sql = "SELECT c.id_consulta, c.edad_paciente, d.nombre AS medico, d.especialidad, c.anios_experiencia_doc, c.tiempo_atencion_min, c.fecha_consulta FROM consultas c JOIN doctores d ON c.id_doctor = d.id_doctor ORDER BY c.id_consulta DESC LIMIT %s;"
        cursor.execute(sql, (limite,))
        filas = cursor.fetchall()
        cursor.close()

        consultas = []
        for f in filas:
            consultas.append({
                "id": f[0],
                "edad": f[1],
                "medico": f[2],
                "especialidad": f[3],
                "experiencia": f[4],
                "tiempo": f[5],
                "fecha": f[6]
            })
        return consultas
    except Exception as e:
        logger.error(f"Error al obtener consultas recientes: {e}")
        return []
    finally:
        conexion.close()


def obtener_turnos(id_doctor=None):
    """
    Obtiene los turnos registrados desde la tabla MariaDB 'turnos'.
    """
    conexion = db.get_connection()
    try:
        cursor = conexion.cursor()
        if id_doctor:
            sql = "SELECT t.id_turno, t.nombre_paciente, t.edad_paciente, d.nombre AS medico, d.especialidad, t.fecha_turno, t.hora_turno, t.estado, t.tiempo_estimado_min, t.id_doctor FROM turnos t JOIN doctores d ON t.id_doctor = d.id_doctor WHERE t.id_doctor = %s ORDER BY t.fecha_turno ASC, t.hora_turno ASC;"
            cursor.execute(sql, (id_doctor,))
        else:
            sql = "SELECT t.id_turno, t.nombre_paciente, t.edad_paciente, d.nombre AS medico, d.especialidad, t.fecha_turno, t.hora_turno, t.estado, t.tiempo_estimado_min, t.id_doctor FROM turnos t JOIN doctores d ON t.id_doctor = d.id_doctor ORDER BY t.fecha_turno ASC, t.hora_turno ASC;"
            cursor.execute(sql)
        filas = cursor.fetchall()
        cursor.close()

        turnos = []
        for f in filas:
            turnos.append({
                "id_turno": f[0],
                "paciente": f[1],
                "edad": f[2],
                "medico": f[3],
                "especialidad": f[4],
                "fecha": f[5],
                "hora": str(f[6]),
                "estado": f[7],
                "tiempo_estimado": f[8],
                "id_doctor": f[9]
            })
        return turnos
    except Exception as e:
        logger.error(f"Error al obtener turnos: {e}")
        return []
    finally:
        conexion.close()


def asegurar_grafico_gerencial(force=False):
    """
    Verifica que el gráfico gerencial exista en static/img/.
    Si no existe o force=True, lo regenera automáticamente.
    """
    if force and os.path.exists(RUTA_GRAFICO_STATIC):
        os.remove(RUTA_GRAFICO_STATIC)
        if os.path.exists(RUTA_GRAFICO_ROOT):
            os.remove(RUTA_GRAFICO_ROOT)

    if not os.path.exists(RUTA_GRAFICO_STATIC):
        modulo_regresion.obtener_datos_regresion(
            generar_grafico=True,
            ruta_grafico=RUTA_GRAFICO_STATIC,
            mostrar_interactivo=False
        )
        try:
            import shutil
            shutil.copyfile(RUTA_GRAFICO_STATIC, RUTA_GRAFICO_ROOT)
        except Exception:
            pass


# =============================================================================
# RUTAS DE LA APLICACIÓN WEB
# =============================================================================

@app.route("/")
def index():
    datos_desc = modulo_descriptiva.obtener_datos_descriptivos()
    datos_reg = modulo_regresion.obtener_datos_regresion(generar_grafico=False)
    consultas_recientes = obtener_consultas_recientes(limite=15)
    turnos_recientes = obtener_turnos()
    asegurar_grafico_gerencial()

    total_doctores = len(datos_desc["doctores"])
    kpis = {
        "n_total": datos_desc["n_total"],
        "media_global": datos_desc["general"]["media"],
        "desviacion_global": datos_desc["general"]["desviacion"],
        "cv_global": datos_desc["general"]["cv"],
        "diagnostico_global": datos_desc["diagnostico_general"],
        "nivel_riesgo_global": datos_desc["nivel_riesgo_general"],
        "total_doctores": total_doctores,
        "r_edad": datos_reg["modelo_edad"]["r"],
        "r2_edad": datos_reg["modelo_edad"]["r2"] * 100,
        "total_outliers": len(datos_reg["outliers"]),
        "tiempo_computo_ms": datos_desc["tiempo_computo_ms"],
        "turnos_activos": len([t for t in turnos_recientes if t["estado"] == "Activo"])
    }

    return render_template(
        "index.html",
        kpis=kpis,
        doctores=datos_desc["doctores"],
        consultas=consultas_recientes,
        turnos=turnos_recientes[:5]
    )


@app.route("/descriptiva")
def descriptiva():
    datos = modulo_descriptiva.obtener_datos_descriptivos()
    return render_template("descriptiva.html", datos=datos)


@app.route("/regresion")
def regresion():
    datos = modulo_regresion.obtener_datos_regresion(generar_grafico=True)
    asegurar_grafico_gerencial()
    return render_template("regresion.html", datos=datos, timestamp=datetime.now().timestamp())


@app.route("/prediccion", methods=["GET", "POST"])
def prediccion():
    # Obtener datos de regresión para el modelo
    datos_reg = modulo_regresion.obtener_datos_regresion(generar_grafico=False)
    
    # Valores por defecto para el formulario
    edad_inicial = 45 
    
    return render_template(
        "prediccion.html",
        edad_inicial=edad_inicial,
        modelo={
            "a": datos_reg["modelo_edad"]["a"],
            "b": datos_reg["modelo_edad"]["b"],
            "r": datos_reg["modelo_edad"]["r"],
            "r2": datos_reg["modelo_edad"]["r2"]
        }
    )


@app.route("/especialistas")
def especialistas():
    conexion = db.get_connection()
    try:
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT d.id_doctor, d.nombre, d.especialidad, d.anios_experiencia, 
                   (SELECT COUNT(*) FROM turnos t WHERE t.id_doctor = d.id_doctor AND t.estado = 'Activo') as turnos_activos
            FROM doctores d
        """)
        filas = cursor.fetchall()
        cursor.close()
        
        doctores_list = []
        for f in filas:
            doctores_list.append({
                "id_doctor": f[0],
                "nombre": f[1],
                "especialidad": f[2],
                "anios_experiencia": f[3],
                "media_tiempo": 0,
                "turnos_activos": f[4],
                "n_consultas": 0,
                "cv": 0,
                "diagnostico": "N/D"
            })
        return render_template("especialistas.html", especialistas=doctores_list)
    except Exception as e:
        import traceback
        traceback.print_exc()
        logger.error(f"Error al listar especialistas: {e}")
        flash(f"Error al cargar la lista de especialistas: {e}", "danger")
        return redirect(url_for("index"))
    finally:
        try:
            conexion.close()
        except:
            pass 


@app.route("/turnos", methods=["GET", "POST"])
def turnos():
    conexion = db.get_connection()
    if request.method == "POST":
        try:
            nombre_paciente = request.form.get("nombre_paciente", "").strip()
            edad_paciente = int(request.form.get("edad_paciente", 30))
            id_doctor = int(request.form.get("id_doctor", 1))
            fecha_turno = request.form.get("fecha_turno", "")

            if not nombre_paciente or not fecha_turno:
                flash("Por favor complete los campos obligatorios del paciente y la fecha.", "danger")
            else:
                reg_doc = modulo_regresion.obtener_regresion_doctor(id_doctor, conexion=conexion)
                if reg_doc and reg_doc["modelo_edad"]:
                    a = reg_doc["modelo_edad"]["a"]
                    b = reg_doc["modelo_edad"]["b"]
                else:
                    datos_reg = modulo_regresion.obtener_datos_regresion(conexion=conexion, generar_grafico=False)
                    a = datos_reg["modelo_edad"]["a"]
                    b = datos_reg["modelo_edad"]["b"]

                y_est, _ = modulo_regresion.predecir_tiempo_turno(a, b, edad_paciente)

                cursor = conexion.cursor()
                sql_ultimo = "SELECT hora_turno, tiempo_estimado_min FROM turnos WHERE id_doctor = %s AND fecha_turno = %s AND estado = 'Activo' ORDER BY hora_turno DESC LIMIT 1;"
                cursor.execute(sql_ultimo, (id_doctor, fecha_turno))
                ultimo_turno = cursor.fetchone()

                if ultimo_turno:
                    h_str = str(ultimo_turno[0])
                    duracion_anterior = float(ultimo_turno[1])
                    formato_hora = "%H:%M:%S" if len(h_str) > 5 else "%H:%M"
                    t_obj = datetime.strptime(h_str[:8], formato_hora)
                    minutos_totales = int(duracion_anterior)
                    nueva_hora_dt = t_obj + timedelta(minutes=minutos_totales)
                    hora_turno = nueva_hora_dt.strftime("%H:%M")
                else:
                    hora_turno = "09:00"

                sql = "INSERT INTO turnos (nombre_paciente, edad_paciente, id_doctor, fecha_turno, hora_turno, estado, tiempo_estimado_min) VALUES (%s, %s, %s, %s, %s, 'Activo', %s);"
                cursor.execute(sql, (nombre_paciente, edad_paciente, id_doctor, fecha_turno, hora_turno, round(y_est, 1)))
                conexion.commit()
                cursor.close()

                # Regenerar gráfico gerencial en tiempo real tras POST exitoso
                asegurar_grafico_gerencial(force=True)

                flash(f"¡Turno reservado para {nombre_paciente} a las {hora_turno}! Duración estimada: {y_est:.1f} min.", "success")
                return redirect(url_for("turnos"))
        except Exception as e:
            logger.error(f"Error al registrar el turno: {e}")
            flash(f"Error al registrar el turno: {str(e)}", "danger")
        finally:
            conexion.close()

    datos_desc = modulo_descriptiva.obtener_datos_descriptivos()
    lista_turnos = obtener_turnos()
    return render_template(
        "turnos.html",
        doctores=datos_desc["doctores"],
        turnos=lista_turnos
    )


@app.route("/turnos/cancelar/<int:id_turno>", methods=["POST"])
def cancelar_turno(id_turno):
    conexion = db.get_connection()
    try:
        cursor = conexion.cursor()
        sql = "UPDATE turnos SET estado = 'Cancelado' WHERE id_turno = %s;"
        cursor.execute(sql, (id_turno,))
        conexion.commit()
        cursor.close()
        
        # Regenerar gráfico gerencial en tiempo real tras POST exitoso
        asegurar_grafico_gerencial(force=True)
        
        flash("Turno cancelado correctamente.", "info")
    except Exception as e:
        logger.error(f"Error al cancelar el turno {id_turno}: {e}")
        flash(f"Error al cancelar el turno: {str(e)}", "danger")
    finally:
        conexion.close()
    return redirect(url_for("turnos"))


@app.route("/especialista/<int:id_doctor>")
def especialista_detalle(id_doctor):
    conexion = db.get_connection()
    try:
        cursor = conexion.cursor()
        cursor.execute("SELECT id_doctor, nombre, especialidad, anios_experiencia FROM doctores WHERE id_doctor = %s", (id_doctor,))
        doc = cursor.fetchone()
        cursor.close()

        if not doc:
            flash("Especialista no encontrado.", "danger")
            return redirect(url_for("index"))

        ruta_grafico_doc = os.path.join(IMG_DIR, f"reporte_doctor_{id_doctor}.png")
        # Asegurar que la función existe antes de llamarla
        if hasattr(modulo_regresion, "generar_grafico_doctor"):
            modulo_regresion.generar_grafico_doctor(id_doctor, ruta_grafico=ruta_grafico_doc)
        else:
            logger.error("La función 'generar_grafico_doctor' no existe en '3_regresion'.")

        turnos_doc = obtener_turnos(id_doctor=id_doctor)
        metricas_doc = modulo_descriptiva.calcular_estadisticas_doctor(id_doctor, conexion=conexion)

        return render_template(
            "especialista_detalle.html",
            doctor={"id_doctor": doc[0], "nombre": doc[1], "especialidad": doc[2], "anios_experiencia": doc[3]},
            turnos=turnos_doc,
            metricas=metricas_doc,
            ruta_grafico_doctor=f"img/reporte_doctor_{id_doctor}.png"
        )
    except Exception as e:
        logger.error(f"Error al obtener detalle del especialista {id_doctor}: {e}")
        flash("Error al cargar detalle del especialista.", "danger")
        return redirect(url_for("especialistas"))
    finally:
        conexion.close()


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
