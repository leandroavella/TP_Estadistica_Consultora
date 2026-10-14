# Consultora Médica: Optimización Operativa mediante Estadística Bivariada

**Trabajo Práctico Integrador de Estadística Aplicada**  
**Dominio:** Gestión Hospitalaria y Optimización de Procesos en Centros de Salud  
**Tecnologías:** MariaDB / MySQL, Python 3, PyMySQL, Matplotlib  
**Muestra Muestral:** $n = 100$ consultas médicas completas  

---

## 1. Introducción y Justificación del Proyecto

En la gestión sanitaria moderna, la asignación ineficiente de tiempos de consulta médica genera dos problemas críticos: **saturación de las salas de espera** por demoras acumuladas y **pérdida de capacidad instalada** por sobrestimación de tiempos.

Este proyecto implementa una solución de software que traslada la teoría estadística bivariada a la resolución directa de dilemas de gestión en un centro de salud. A través de la automatización sobre una base de datos relacional de **100 registros reales y representativos**, el sistema reemplaza el cálculo manual propenso a errores por modelos analíticos y predictivos exactos basados en el método de **Mínimos Cuadrados** y la **Correlación de Pearson**.

---

## 2. Variables Analizadas

El modelo captura y procesa las siguientes variables clínicas y operativas:

| Variable | Notación | Tipo | Descripción | Unidad |
| :--- | :---: | :--- | :--- | :---: |
| **Edad del Paciente** | $X_1$ | Cuantitativa Discreta | Variable explicativa / independiente | Años |
| **Experiencia del Médico** | $X_2$ | Cuantitativa Discreta | Variable explicativa / independiente | Años |
| **Tiempo de Atención** | $Y$ | Cuantitativa Continua | Variable respuesta / dependiente | Minutos |
| **Doctor / Especialidad** | Cualitativa | Categórica Nominal | Factor de agrupamiento y auditoría | - |

---

## 3. Resolución Explícita de los 6 Problemas Operativos

El software fue diseñado para dar respuesta rigurosa y comprobable a los siguientes seis desafíos del mundo real:

### Problema 1: Volumen y Eficiencia Operativa
* **Desafío:** En un centro médico con gran volumen de pacientes, calcular a mano la media, varianzas y sumatorias cruzadas para una muestra representativa ($n = 100$) involucra más de 400 operaciones aritméticas encadenadas, demandando entre 2 y 3 horas hombre y con una tasa inaceptable de error humano en redondeos.
* **Solución del Software:** El script `2_descriptiva.py` procesa los 100 registros en **milisegundos** directamente desde el motor MariaDB, eliminando la totalidad del error de cálculo humano y permitiendo auditorías continuas e instantáneas.

### Problema 2: Predicción de Demanda para Organización de Agendas
* **Desafío:** Tradicionalmente, los centros de salud asignan bloques fijos (por ejemplo, 15 o 20 minutos por turno para todos los pacientes), lo cual produce cuellos de botella severos cuando concurren pacientes gerontológicos que requieren más tiempo.
* **Solución del Software:** El script `3_regresion.py` aplica el modelo de regresión lineal por Mínimos Cuadrados:
  $$\hat{y} = a + b \cdot X_1$$
  A partir de la edad del paciente que solicita el turno, el sistema predice con exactitud matemática el tiempo esperado de atención ($\hat{y}$) y calcula un bloque dinámico de agenda sugerido con margen de seguridad, optimizando la programación sin generar tiempos muertos ni retrasos en sala de espera.

### Problema 3: Evaluación de Desempeño y Homogeneidad
* **Desafío:** Comparar doctores únicamente por su tiempo medio de consulta es engañoso: un médico puede tener un promedio bajo pero una altísima dispersión (inconsistencia en su atención), mientras que otro puede ser predecible y constante.
* **Solución del Software:** `2_descriptiva.py` calcula y contrasta el **Coeficiente de Variación ($CV$)** individual para cada doctor y especialidad:
  $$CV = \left( \frac{s}{\bar{x}} \right) \times 100\%$$
  - $CV < 15\%$: Desempeño altamente homogéneo y predecible (ideal para turnos seriados).
  - $15\% \le CV \le 30\%$: Variabilidad moderada sujeta a supervisión.
  - $CV > 30\%$: Alta dispersión que alerta a la dirección médica sobre posibles cuellos de botella o desvíos de protocolos clínicos.

### Problema 4: Detección de Anomalías y Casos Atípicos (Outliers)
* **Desafío:** Identificar consultas que se desviaron abruptamente del estándar para auditar posibles negligencias, urgencias no reportadas o pérdidas de tiempo innecesarias.
* **Solución del Software:** Mediante el Error Estándar de la Estimación ($s_e$), el sistema detecta de forma automática aquellos residuos cuyo desvío supera el intervalo crítico de dos errores estándar:
  $$|e_i| = |y_i - \hat{y}_i| > 2 \cdot s_e$$
  Los casos anómalos son reportados con nombre del profesional, edad del paciente y desvío neto, y son resaltados visualmente con un marcador distintivo en el gráfico de dispersión de Matplotlib.

### Problema 5: Validación de Hipótesis Operativas
* **Desafío:** Determinar si el tiempo de consulta responde a la edad del paciente o a la experiencia del médico, o si alguna de estas variables es estadísticamente irrelevante.
* **Solución del Software:** El sistema calcula y compara los coeficientes de correlación lineal de Pearson ($r$) y coeficientes de determinación ($R^2$):
  - **Hipótesis A ($X_1$ vs $Y$):** Evalúa la asociación entre la edad del paciente y la duración de la consulta.
  - **Hipótesis B ($X_2$ vs $Y$):** Evalúa la asociación entre los años de experiencia del médico y la duración de la consulta.
  El análisis comparativo valida matemáticamente cuál de las dos variables posee mayor capacidad predictiva y explica un porcentaje superior de la varianza total ($R^2$).

### Problema 6: Toma de Decisiones Administrativas y Reporte Gerencial
* **Desafío:** Los directivos médicos y administradores de clínicas necesitan información gráfica, visual y ejecutiva para tomar decisiones de asignación de recursos.
* **Solución del Software:** `3_regresion.py` consolida un informe ejecutivo por consola y exporta un tablero gráfico en alta resolución (`reporte_bivariado_gerencia.png`) que incluye:
  - Diagramas de dispersión con sus respectivas rectas de regresión ajustadas.
  - El **Centro de Medias o Centroide $(\bar{x}, \bar{y})$** explícitamente destacado con líneas de referencia ortogonales.
  - Marcación diferenciada de los puntos atípicos detectados.
  - Ecuaciones completas y métricas $r$ y $R^2$ integradas en el panel.

---

## 4. Marco Matemático y Fórmulas Implementadas

Todas las funciones estadísticas fueron programadas paso a paso sin cajas negras para evidenciar el rigor de cálculo:

### 1. Medidas Univariadas
* **Media Muestral:**
  $$\bar{x} = \frac{1}{n} \sum_{i=1}^n x_i$$
* **Varianza Muestral:**
  $$s^2 = \frac{1}{n - 1} \sum_{i=1}^n (x_i - \bar{x})^2$$
* **Desvío Estándar Muestral:**
  $$s = \sqrt{s^2}$$
* **Coeficiente de Variación:**
  $$CV = \left( \frac{s}{\bar{x}} \right) \cdot 100$$

### 2. Medidas Bivariadas y Recta de Regresión
* **Sumatorias de Desvíos Cuadráticos y Cruzados:**
  $$SS_{xx} = \sum_{i=1}^n (x_i - \bar{x})^2, \quad SS_{yy} = \sum_{i=1}^n (y_i - \bar{y})^2, \quad SS_{xy} = \sum_{i=1}^n (x_i - \bar{x})(y_i - \bar{y})$$
* **Covarianza Muestral:**
  $$S_{xy} = \frac{SS_{xy}}{n - 1}$$
* **Pendiente de la Recta ($b$):**
  $$b = \frac{SS_{xy}}{SS_{xx}}$$
* **Ordenada al Origen ($a$):**
  $$a = \bar{y} - b \cdot \bar{x}$$
* **Coeficiente de Correlación de Pearson ($r$):**
  $$r = \frac{SS_{xy}}{\sqrt{SS_{xx} \cdot SS_{yy}}}$$
* **Coeficiente de Determinación ($R^2$):**
  $$R^2 = (r)^2$$
* **Error Estándar de la Estimación ($s_e$):**
  $$s_e = \sqrt{\frac{\sum_{i=1}^n (y_i - \hat{y}_i)^2}{n - 2}}$$

---

## 5. Estructura de la Base de Datos (`1_schema.sql`)

El diseño relacional normalizado consta de dos entidades:

```sql
-- 1. Doctores / Profesionales
CREATE TABLE doctores (
    id_doctor INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(80) NOT NULL,
    especialidad VARCHAR(60) NOT NULL,
    anios_experiencia INT NOT NULL
);

-- 2. Consultas Médicas (n = 100)
CREATE TABLE consultas (
    id_consulta INT AUTO_INCREMENT PRIMARY KEY,
    edad_paciente INT NOT NULL,           -- Variable X1
    id_doctor INT NOT NULL,               -- FK
    anios_experiencia_doc INT NOT NULL,   -- Variable X2
    tiempo_atencion_min FLOAT NOT NULL,   -- Variable Y
    fecha_consulta DATETIME NOT NULL,
    FOREIGN KEY (id_doctor) REFERENCES doctores(id_doctor)
);
```

### Características de los 100 Registros
- Distribución de edades entre 3 y 84 años (pacientes pediátricos, adultos jóvenes y adultos mayores).
- 5 profesionales de especialidades diferenciadas (Clínica Médica, Pediatría, Cardiología, Medicina General y Traumatología) con experiencias de 4 a 24 años.
- Inclusión deliberada de casos típicos y 2 casos atípicos representativos para comprobar el funcionamiento del detector de anomalías (urgencia médica extendida y firma rápida de recetas).

---

## 6. Guía de Instalación y Ejecución

### Requisitos Previos
- Python 3.9 o superior.
- Servidor MariaDB o MySQL activo (por ejemplo mediante XAMPP, WampServer o servicio nativo).
- Librerías necesarias:
  ```bash
  pip install pymysql matplotlib flask
  ```

### Paso 1: Configurar la Base de Datos
El script SQL puede ser cargado mediante el cliente de MariaDB / phpMyAdmin importando `1_schema.sql`, o bien **se inicializa automáticamente** la primera vez que se ejecutan los scripts de Python si la base de datos no estuviera creada.

### Paso 2: Ejecutar la Aplicación Web (Dashboard Gerencial en Flask)
Para interactuar con el panel visual gerencial completo:
```bash
python app.py
```
*Acceso en el navegador:* `http://127.0.0.1:5000`
- **Dashboard Principal (`/`):** Resumen operativo de las 100 consultas, KPIs y accesos rápidos.
- **Análisis Descriptivo (`/descriptiva`):** Tabla de medias, desvíos y Coeficiente de Variación (CV) por doctor y especialidad.
- **Regresión y Outliers (`/regresion`):** Coeficientes $r$, $R^2$, tabla de anomalías y visualización del gráfico de alta resolución.
- **Predictor de Turnos (`/prediccion`):** Simulador reactivo en tiempo real con control deslizante que dimensiona el turno y bloque de agenda según la edad.

### Paso 3: Ejecución Alternativa por Consola (CLI)
Si desea auditar las salidas directamente por consola de comandos:
- **Análisis Descriptivo:** `python 2_descriptiva.py`
- **Análisis Bivariado y Regresión:** `python 3_regresion.py`

---

## 7. Conclusiones y Valor Agregado

La implementación de este sistema demuestra que el modelado estadístico riguroso es una herramienta imprescindible para la ingeniería y administración de centros de salud:
1. **Reduce drásticamente los tiempos de gestión** al informatizar análisis complejos sobre muestras representativas ($n = 100$).
2. **Sustituye la intuición por evidencia matemática** para dimensionar los turnos según las características reales de los pacientes.
3. **Audita objetivamente la calidad del servicio** identificando inconsistencias operativas mediante el Coeficiente de Variación y el filtrado residual de anomalías.
