"""
=============================================================================
PROYECTO: ESTADÍSTICA BIVARIADA - CONSULTORA MÉDICA
SCRIPT: 3_regresion.py
PROPÓSITO:
  Análisis Estadístico Bivariado, Correlación Lineal de Pearson y Mínimos Cuadrados.
  Modo Demostración en Tiempo Real basado en la tabla 'turnos' (Global e Individual).
=============================================================================
"""

import math
import os
import sys
import pymysql
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Asegurar codificación utf-8 en salidas de consola en Windows
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Configuración de base de datos
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "consultora_medica",
    "charset": "utf8mb4",
    "autocommit": True
}


def obtener_conexion():
    try:
        return pymysql.connect(
            host=DB_CONFIG["host"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["database"],
            charset=DB_CONFIG["charset"],
            autocommit=DB_CONFIG["autocommit"],
            auth_plugin_map={"auth_gssapi_client": "pymysql.credentials"}
        )
    except pymysql.err.OperationalError:
        print("[!] Base de datos 'consultora_medica' no detectada...")
        conexion_raiz = pymysql.connect(
            host=DB_CONFIG["host"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            charset=DB_CONFIG["charset"],
            autocommit=True,
            auth_plugin_map={"auth_gssapi_client": "pymysql.credentials"}
        )
        cursor_raiz = conexion_raiz.cursor()
        ruta_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "1_schema.sql")
        with open(ruta_script, "r", encoding="utf-8") as f:
            contenido_sql = f.read()
        for sentencia in contenido_sql.split(";"):
            sentencia_limpia = sentencia.strip()
            if sentencia_limpia:
                cursor_raiz.execute(sentencia_limpia)
        cursor_raiz.close()
        conexion_raiz.close()

        return pymysql.connect(
            host=DB_CONFIG["host"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["database"],
            charset=DB_CONFIG["charset"],
            autocommit=DB_CONFIG["autocommit"],
            auth_plugin_map={"auth_gssapi_client": "pymysql.credentials"}
        )


def calcular_modelo_bivariado(x_valores, y_valores, nombres_adicionales=None):
    n = len(x_valores)
    if n < 3:
        return {
            "n": n, "mean_x": sum(x_valores)/n if n > 0 else 0, "mean_y": sum(y_valores)/n if n > 0 else 0,
            "ss_xx": 0, "ss_yy": 0, "ss_xy": 0, "cov_xy": 0, "a": 0, "b": 0, "r": 0, "r2": 0, "se": 0,
            "y_pred": y_valores, "residuos": [0]*n, "outliers": []
        }

    mean_x = sum(x_valores) / n
    mean_y = sum(y_valores) / n

    ss_xx = sum((xi - mean_x) ** 2 for xi in x_valores)
    ss_yy = sum((yi - mean_y) ** 2 for yi in y_valores)
    ss_xy = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x_valores, y_valores))

    cov_xy = ss_xy / (n - 1)
    b = ss_xy / ss_xx if ss_xx != 0 else 0.0
    a = mean_y - (b * mean_x)

    denominador_r = math.sqrt(ss_xx * ss_yy)
    r = (ss_xy / denominador_r) if denominador_r != 0 else 0.0
    r2 = r ** 2

    y_pred = [a + b * xi for xi in x_valores]
    residuos = [yi - yhat for yi, yhat in zip(y_valores, y_pred)]
    suma_residuos_cuad = sum(e ** 2 for e in residuos)
    se = math.sqrt(suma_residuos_cuad / (n - 2)) if n > 2 else 0.0

    outliers = []
    for idx, (xi, yi, yhat, ei) in enumerate(zip(x_valores, y_valores, y_pred, residuos)):
        if se > 0 and abs(ei) > (2.0 * se):
            info_extra = nombres_adicionales[idx] if nombres_adicionales else {}
            outliers.append({"indice": idx, "x": xi, "y_real": yi, "y_pred": yhat, "residuo": ei, "info": info_extra})

    return {
        "n": n, "mean_x": mean_x, "mean_y": mean_y, "ss_xx": ss_xx, "ss_yy": ss_yy, "ss_xy": ss_xy,
        "cov_xy": cov_xy, "a": a, "b": b, "r": r, "r2": r2, "se": se, "y_pred": y_pred,
        "residuos": residuos, "outliers": outliers
    }


def interpretar_correlacion(r):
    abs_r = abs(r)
    sentido = "DIRECTA / POSITIVA" if r > 0 else "INVERSA / NEGATIVA"
    if abs_r >= 0.85:
        fuerza = "MUY FUERTE"
    elif abs_r >= 0.65:
        fuerza = "MODERADA A FUERTE"
    elif abs_r >= 0.35:
        fuerza = "DÉBIL"
    else:
        fuerza = "PRÁCTICAMENTE NULA / DESPRECIABLE"
    return fuerza, sentido


def predecir_tiempo_turno(a, b, valor_x, margen_seguridad=5.0):
    y_estimado = a + (b * valor_x)
    bloque_recomendado = math.ceil((y_estimado + margen_seguridad) / 5.0) * 5
    return y_estimado, bloque_recomendado


def graficar_reporte_ejecutivo(datos_completos, modelo_x1, modelo_x2, ruta_guardado=None, mostrar_interactivo=False):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
    fig.patch.set_facecolor('#F8F9FA')

    x1 = [row["edad"] for row in datos_completos if row["edad"] is not None and row["tiempo"] is not None]
    y = [row["tiempo"] for row in datos_completos if row["edad"] is not None and row["tiempo"] is not None]

    ax1.set_facecolor('#FFFFFF')
    if x1 and y:
        ax1.scatter(x1, y, color='#1F77B4', alpha=0.7, edgecolors='black', s=45, label=f'Turnos observados (n={len(x1)})')
        x1_line = [min(x1), max(x1)]
        y1_line = [modelo_x1["a"] + modelo_x1["b"] * val for val in x1_line]
        ax1.plot(x1_line, y1_line, color='#D62728', linewidth=2.5, label=f'Recta: ŷ = {modelo_x1["a"]:.2f} + {modelo_x1["b"]:.2f}x')

        mx1, my = modelo_x1["mean_x"], modelo_x1["mean_y"]
        ax1.scatter([mx1], [my], color='#2CA02C', s=160, zorder=5, marker='o', edgecolors='black', label=f'Centro Medias')

    ax1.set_title('Edad del Paciente vs Tiempo de Atención', fontsize=12, fontweight='bold')
    ax1.set_xlabel('Edad del Paciente (años)')
    ax1.set_ylabel('Tiempo de Consulta (minutos)')
    ax1.grid(True, linestyle='--', alpha=0.5)
    ax1.legend(loc='upper left', fontsize=9)

    x2 = [row["experiencia"] for row in datos_completos if row["experiencia"] is not None and row["tiempo"] is not None]
    ax2.set_facecolor('#FFFFFF')
    if x2 and y:
        ax2.scatter(x2, y, color='#9467BD', alpha=0.7, edgecolors='black', s=45, label=f'Turnos observados (n={len(x2)})')
        x2_line = [min(x2), max(x2)]
        y2_line = [modelo_x2["a"] + modelo_x2["b"] * val for val in x2_line]
        ax2.plot(x2_line, y2_line, color='#D62728', linewidth=2.5, label=f'Recta: ŷ = {modelo_x2["a"]:.2f} + {modelo_x2["b"]:.2f}x')

        mx2 = modelo_x2["mean_x"]
        ax2.scatter([mx2], [my], color='#2CA02C', s=160, zorder=5, marker='o', edgecolors='black', label=f'Centro Medias')

    ax2.set_title('Experiencia Médica vs Tiempo de Atención', fontsize=12, fontweight='bold')
    ax2.set_xlabel('Años de Experiencia')
    ax2.set_ylabel('Tiempo de Consulta (minutos)')
    ax2.grid(True, linestyle='--', alpha=0.5)
    ax2.legend(loc='upper left', fontsize=9)

    plt.suptitle('CENTRO MÉDICO - TABLERO GERENCIAL (En Tiempo Real)', fontsize=14, fontweight='bold', y=0.98)
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])

    if ruta_guardado is None:
        ruta_guardado = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reporte_bivariado_gerencia.png")
    
    os.makedirs(os.path.dirname(ruta_guardado), exist_ok=True)
    fig.savefig(ruta_guardado, dpi=300)
    if mostrar_interactivo:
        plt.show()
    else:
        plt.close(fig)

    return ruta_guardado


def graficar_reporte_doctor(nombre_doctor, registros, modelo_edad, ruta_guardado):
    """
    Genera y guarda un gráfico individualizado para el especialista en tiempo real.
    """
    fig, ax = plt.subplots(figsize=(8, 6))
    fig.patch.set_facecolor('#F8F9FA')
    ax.set_facecolor('#FFFFFF')

    x1 = [row["edad"] for row in registros if row["edad"] is not None and row["tiempo"] is not None]
    y = [row["tiempo"] for row in registros if row["edad"] is not None and row["tiempo"] is not None]

    if x1 and y:
        ax.scatter(x1, y, color='#1F77B4', alpha=0.8, edgecolors='black', s=60, label=f'Turnos (n={len(x1)})')
        if modelo_edad and modelo_edad["n"] >= 3:
            x1_line = [min(x1), max(x1)]
            y1_line = [modelo_edad["a"] + modelo_edad["b"] * val for val in x1_line]
            ax.plot(x1_line, y1_line, color='#D62728', linewidth=2.5, label=f'ŷ = {modelo_edad["a"]:.2f} + {modelo_edad["b"]:.2f}x')
            
            mx, my = modelo_edad["mean_x"], modelo_edad["mean_y"]
            ax.scatter([mx], [my], color='#2CA02C', s=180, zorder=5, marker='o', edgecolors='black', label='Centro de Medias')

    ax.set_title(f'Análisis Bivariado - {nombre_doctor}', fontsize=12, fontweight='bold', pad=12)
    ax.set_xlabel('Edad del Paciente [X1] (años)', fontsize=10)
    ax.set_ylabel('Tiempo de Consulta [Y] (minutos)', fontsize=10)
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.legend(loc='upper left', fontsize=9)

    plt.tight_layout()
    os.makedirs(os.path.dirname(ruta_guardado), exist_ok=True)
    fig.savefig(ruta_guardado, dpi=300)
    plt.close(fig)
    return ruta_guardado


def generar_grafico_doctor(id_doctor, ruta_grafico):
    conexion = obtener_conexion()
    try:
        cursor = conexion.cursor()
        cursor.execute("SELECT anios_experiencia, nombre, especialidad FROM doctores WHERE id_doctor = %s;", (id_doctor,))
        doc_info = cursor.fetchone()
        if not doc_info:
            return None
        exp_doc, nombre_doc, esp_doc = doc_info[0], doc_info[1], doc_info[2]

        cursor.execute("""
            SELECT t.id_turno, t.edad_paciente, t.tiempo_estimado_min 
            FROM turnos t 
            WHERE t.id_doctor = %s;
        """, (id_doctor,))
        filas_t = cursor.fetchall()
        
        registros = []
        for fila in filas_t:
            registros.append({
                "id": fila[0], "edad": fila[1], "experiencia": exp_doc,
                "tiempo": fila[2], "medico": nombre_doc, "especialidad": esp_doc
            })

        edades = [r["edad"] for r in registros if r["edad"] is not None and r["tiempo"] is not None]
        tiempos = [r["tiempo"] for r in registros if r["edad"] is not None and r["tiempo"] is not None]

        modelo_edad = calcular_modelo_bivariado(edades, tiempos, registros) if len(edades) >= 3 else None
        
        graficar_reporte_doctor(nombre_doc, registros, modelo_edad, ruta_grafico)
    finally:
        conexion.close()


def obtener_datos_regresion(conexion=None, generar_grafico=True, ruta_grafico=None, mostrar_interactivo=False):
    cerrar_conexion = False
    if conexion is None:
        conexion = obtener_conexion()
        cerrar_conexion = True

    try:
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT t.id_turno, t.edad_paciente, d.anios_experiencia, t.tiempo_estimado_min, d.nombre, d.especialidad
            FROM turnos t JOIN doctores d ON t.id_doctor = d.id_doctor
            ORDER BY t.id_turno ASC;
        """)
        filas_t = cursor.fetchall()
        cursor.close()

        registros = []
        for fila in filas_t:
            registros.append({
                "id": fila[0], "edad": fila[1], "experiencia": fila[2],
                "tiempo": fila[3], "medico": fila[4], "especialidad": fila[5]
            })

        edades = [r["edad"] for r in registros if r["edad"] is not None and r["tiempo"] is not None]
        experiencias = [r["experiencia"] for r in registros if r["experiencia"] is not None and r["tiempo"] is not None]
        tiempos = [r["tiempo"] for r in registros if r["edad"] is not None and r["tiempo"] is not None]

        modelo_edad = calcular_modelo_bivariado(edades, tiempos, registros)
        modelo_exp = calcular_modelo_bivariado(experiencias, tiempos, registros)

        fuerza_edad, sentido_edad = interpretar_correlacion(modelo_edad["r"])
        fuerza_exp, sentido_exp = interpretar_correlacion(modelo_exp["r"])

        ruta_png = None
        if generar_grafico and len(edades) >= 3:
            ruta_png = graficar_reporte_ejecutivo(
                registros, modelo_edad, modelo_exp,
                ruta_guardado=ruta_grafico, mostrar_interactivo=mostrar_interactivo
            )

        return {
            "registros": registros,
            "modelo_edad": modelo_edad,
            "modelo_exp": modelo_exp,
            "fuerza_edad": fuerza_edad,
            "sentido_edad": sentido_edad,
            "fuerza_exp": fuerza_exp,
            "sentido_exp": sentido_exp,
            "outliers": modelo_edad["outliers"],
            "ruta_grafico": ruta_png
        }
    finally:
        if cerrar_conexion and conexion:
            conexion.close()


def obtener_regresion_doctor(id_doctor, conexion=None):
    cerrar_conexion = False
    if conexion is None:
        conexion = obtener_conexion()
        cerrar_conexion = True

    try:
        cursor = conexion.cursor()
        cursor.execute("SELECT anios_experiencia, nombre, especialidad FROM doctores WHERE id_doctor = %s;", (id_doctor,))
        doc_info = cursor.fetchone()
        if not doc_info:
            return None
        exp_doc, nombre_doc, esp_doc = doc_info[0], doc_info[1], doc_info[2]

        cursor.execute("""
            SELECT t.id_turno, t.edad_paciente, t.tiempo_estimado_min 
            FROM turnos t 
            WHERE t.id_doctor = %s;
        """, (id_doctor,))
        filas_t = cursor.fetchall()
        cursor.close()

        registros = []
        for fila in filas_t:
            registros.append({
                "id": fila[0], "edad": fila[1], "experiencia": exp_doc,
                "tiempo": fila[2], "medico": nombre_doc, "especialidad": esp_doc
            })

        edades = [r["edad"] for r in registros if r["edad"] is not None and r["tiempo"] is not None]
        tiempos = [r["tiempo"] for r in registros if r["edad"] is not None and r["tiempo"] is not None]

        modelo_edad = calcular_modelo_bivariado(edades, tiempos, registros) if len(edades) >= 3 else None
        fuerza_edad, sentido_edad = interpretar_correlacion(modelo_edad["r"]) if modelo_edad else ("Insuficientes datos", "N/D")

        # Generar gráfico individual exclusivo para este doctor en static/img/
        base_dir = os.path.dirname(os.path.abspath(__file__))
        ruta_img_doc = os.path.join(base_dir, "static", "img", f"reporte_doctor_{id_doctor}.png")
        graficar_reporte_doctor(nombre_doc, registros, modelo_edad, ruta_img_doc)

        return {
            "registros": registros,
            "modelo_edad": modelo_edad,
            "fuerza_edad": fuerza_edad,
            "sentido_edad": sentido_edad,
            "outliers": modelo_edad["outliers"] if modelo_edad else [],
            "ruta_grafico_doctor": f"img/reporte_doctor_{id_doctor}.png"
        }
    finally:
        if cerrar_conexion and conexion:
            conexion.close()


def main():
    print("=" * 85)
    print("  CONSULTORA MÉDICA - AUDITORÍA BIVARIADA (Tiempo Real)")
    print("=" * 85)


if __name__ == "__main__":
    main()