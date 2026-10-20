# utils/glosario.py

GLOSARIO_ESTADISTICO = {
    "media": {
        "titulo": "Media",
        "explicacion": "Es el tiempo promedio que el especialista dedica a cada paciente. Representa el ritmo estándar de atención en la jornada."
    },
    "desviacion_estandar": {
        "titulo": "Desviación Estándar",
        "explicacion": "Indica qué tanto varía el tiempo de atención. Un valor alto sugiere que el especialista tiene tiempos de atención muy irregulares entre pacientes."
    },
    "coeficiente_variacion": {
        "titulo": "Coeficiente de Variación (CV)",
        "explicacion": "Es una medida relativa de dispersión. Un CV bajo indica que el especialista es muy consistente y predecible en su ritmo de trabajo."
    },
    "r_cuadrado": {
        "titulo": "R² (Coeficiente de Determinación)",
        "explicacion": "Representa qué porcentaje del tiempo de atención depende específicamente de la edad del paciente. Si es bajo, otros factores influyen más que la edad."
    }
}

def obtener_explicacion(metrica):
    return GLOSARIO_ESTADISTICO.get(metrica, {"titulo": metrica.replace("_", " ").title(), "explicacion": "Información no disponible."})
