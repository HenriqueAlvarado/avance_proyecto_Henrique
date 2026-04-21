# Plataforma de Seguimiento de Hábitos

**Equipo:** Henrique  
**Dominio:** Plataforma de Seguimiento de Hábitos  
**Fecha:** Abril 2026

---

## ¿Qué problema resuelve?

El sistema permite a los usuarios registrar y dar seguimiento a sus hábitos diarios y semanales, ayudándoles a mantener la consistencia en actividades como meditar, hacer ejercicio o leer. Automatiza el cálculo de rachas de cumplimiento, motivando a los usuarios a no romper su progreso y proporcionando visibilidad clara de su historial y metas pendientes.

---

## Estructura de la Base de Datos

| Tabla | Descripción | Relación |
|-------|-------------|----------|
| habitos | Almacena los hábitos creados (nombre, frecuencia, meta) | Tabla principal, relacionada con registros y rachas |
| registros | Guarda el cumplimiento diario/semanal de cada hábito | Muchos a uno con habitos (FK: habito_id) |
| rachas | Mantiene la racha actual y máxima de cada hábito | Uno a uno con habitos (FK: habito_id único) |

**Relaciones detalladas:**
- `registros.habito_id` → `habitos.id` (CASCADE: si se elimina un hábito, se eliminan sus registros)
- `rachas.habito_id` → `habitos.id` (CASCADE: si se elimina un hábito, se elimina su racha)

---

## Rutas de la API

| Método | Ruta | Qué hace |
|--------|------|----------|
| GET | / | Interfaz principal HTML |
| POST | /habito | Crear un nuevo hábito (nombre, frecuencia, meta) |
| POST | /cumplimiento | Registrar cumplimiento de un hábito en una fecha (con tarea pesada de 5s) |
| GET | /historial | Consultar historial de cumplimiento de un hábito específico |
| GET | /resumen | Ver resumen del día: hábitos cumplidos vs pendientes |
| GET | /habitos | Listar todos los hábitos registrados |

---

## ¿Cuál es la tarea pesada y por qué bloquea el sistema?

**Ubicación de la tarea pesada:** En la función `calcular_racha()` dentro de `app.py`, línea que contiene `time.sleep(5)`.

**Qué simula:** Un proceso costoso como enviar una notificación push, actualizar un sistema de analytics, o procesar una recompensa por la racha alcanzada.

**Por qué bloquea el sistema:** Cuando un usuario registra un cumplimiento, el servidor Flask se queda "dormido" por 5 segundos antes de responder. Si múltiples usuarios hacen solicitudes simultáneas, cada una espera en cola porque Flask por defecto maneja una solicitud a la vez. Esto significa que el 4to usuario esperaría 15-20 segundos para recibir respuesta, degradando severamente la experiencia.

**Solución potencial en producción:** Mover esta tarea a una cola de mensajes (RabbitMQ, SQS) o un worker en segundo plano (Celery, Redis Queue) para que el usuario reciba respuesta inmediata mientras la tarea pesada se procesa asíncronamente.

---

## Cómo levantar el proyecto

```bash
# 1. Clonar el repositorio
git clone [URL_DEL_REPOSITORIO]
cd avance_proyecto_Henrique

# 2. Crear las tablas en RDS
mysql -h db-actividad.cjbbd4mntf9v.us-east-1.rds.amazonaws.com -P 3306 -u admin -p < schema.sql
# Ingresar contraseña: hola12345

# 3. Construir la imagen Docker
docker build -t habbitos-app .

# 4. Correr el contenedor
docker run -d -p 5000:5000 \
  -e DB_HOST=db-actividad.cjbbd4mntf9v.us-east-1.rds.amazonaws.com \
  -e DB_PORT=3306 \
  -e DB_USER=admin \
  -e DB_PASSWORD=hola12345 \
  -e DB_NAME=habbitos_db \
  --name habbitos-app \
  habbitos-app

# 5. Verificar que el contenedor está corriendo
docker ps

# 6. Abrir en navegador
http://http://10.0.1.207/:5000

<img width="1044" height="258" alt="image" src="https://github.com/user-attachments/assets/6892dbac-c34e-4224-8f76-144dd5391024" />
