import sys
import os
import random
from datetime import datetime, timedelta

# Add parent directory to sys.path to import db
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import db

def seed_db():
    conexion = db.get_connection()
    cursor = conexion.cursor()
    
    # Limpiar tablas
    try:
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        cursor.execute("TRUNCATE TABLE turnos;")
        cursor.execute("TRUNCATE TABLE consultas;")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        
        # Obtener doctores
        cursor.execute("SELECT id_doctor FROM doctores;")
        doctores = [row[0] for row in cursor.fetchall()]
        
        # Insertar 10 pacientes por cada doctor
        for id_doctor in doctores:
            for i in range(1, 11):
                cursor.execute("""
                    INSERT INTO turnos (nombre_paciente, edad_paciente, id_doctor, fecha_turno, hora_turno, estado, tiempo_estimado_min) 
                    VALUES (%s, %s, %s, %s, %s, "Activo", %s);
                """, (f"Paciente {id_doctor}_{i}", random.randint(20, 70), id_doctor, datetime.now().strftime("%Y-%m-%d"), f"{9+i}:00", round(random.uniform(15, 45), 1)))
        
        conexion.commit()
        print("Base de datos precargada correctamente.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        conexion.close()

if __name__ == "__main__":
    seed_db()
