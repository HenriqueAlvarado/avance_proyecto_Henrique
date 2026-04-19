"""
Plataforma de Seguimiento de Hábitos
Equipo: Henrique
Aplicación Flask con conexión a RDS MySQL
"""

from flask import Flask, request, render_template_string, jsonify
import mysql.connector
from mysql.connector import Error
import os
import time
from datetime import datetime, timedelta

app = Flask(__name__)

# Configuración de base de datos desde variables de entorno
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'db-actividad.cjbbd4mntf9v.us-east-1.rds.amazonaws.com'),
    'port': int(os.environ.get('DB_PORT', 3306)),
    'user': os.environ.get('DB_USER', 'admin'),
    'password': os.environ.get('DB_PASSWORD'),
    'database': os.environ.get('DB_NAME', 'habbitos_db')
}

# HTML template para la interfaz
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Plataforma de Hábitos</title>
    <style>
        body { font-family: Arial; margin: 20px; }
        .container { max-width: 800px; margin: auto; }
        .form-group { margin-bottom: 15px; }
        label { display: inline-block; width: 120px; }
        input, select { padding: 5px; width: 200px; }
        button { padding: 8px 15px; background: #4CAF50; color: white; border: none; cursor: pointer; }
        .section { border: 1px solid #ddd; padding: 15px; margin-bottom: 20px; border-radius: 5px; }
        h2 { color: #333; }
        .success { color: green; }
        .error { color: red; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #4CAF50; color: white; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Plataforma de Seguimiento de Hábitos</h1>
        
        <div class="section">
            <h2>1. Crear Nuevo Hábito</h2>
            <form action="/habito" method="post">
                <div class="form-group">
                    <label>Nombre:</label>
                    <input type="text" name="nombre" required>
                </div>
                <div class="form-group">
                    <label>Frecuencia:</label>
                    <select name="frecuencia">
                        <option value="diaria">Diaria</option>
                        <option value="semanal">Semanal</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Meta:</label>
                    <input type="number" name="meta" value="1" required>
                </div>
                <button type="submit">Crear Hábito</button>
            </form>
        </div>

        <div class="section">
            <h2>2. Registrar Cumplimiento</h2>
            <form action="/cumplimiento" method="post">
                <div class="form-group">
                    <label>ID del Hábito:</label>
                    <input type="number" name="habito_id" required>
                </div>
                <div class="form-group">
                    <label>Fecha (YYYY-MM-DD):</label>
                    <input type="date" name="fecha" value="{{ fecha_actual }}">
                </div>
                <button type="submit">Registrar (tarda ~5s)</button>
            </form>
        </div>

        <div class="section">
            <h2>3. Consultar Historial</h2>
            <form action="/historial" method="get">
                <div class="form-group">
                    <label>ID del Hábito:</label>
                    <input type="number" name="habito_id" required>
                </div>
                <button type="submit">Ver Historial</button>
            </form>
        </div>

        <div class="section">
            <h2>4. Resumen del Día</h2>
            <form action="/resumen" method="get">
                <button type="submit">Ver Resumen</button>
            </form>
        </div>

        <div class="section">
            <h2>5. Listar Todos los Hábitos</h2>
            <form action="/habitos" method="get">
                <button type="submit">Ver Hábitos</button>
            </form>
        </div>

        {% if mensaje %}
        <div class="{{ 'success' if success else 'error' }}">
            <strong>{{ mensaje }}</strong>
        </div>
        {% endif %}

        {% if datos %}
        <div class="section">
            <h2>Resultados:</h2>
            {{ datos|safe }}
        </div>
        {% endif %}
    </div>
</body>
</html>
'''

def get_db_connection():
    """Función para obtener conexión a la base de datos"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Error conectando a MySQL: {e}")
        return None

def calcular_racha(habito_id, fecha_registro):
    """
    TAREA PESADA: Calcula la racha actual del hábito
    Simula proceso costoso con time.sleep(5)
    """
    print(f"Iniciando cálculo de racha para hábito {habito_id}...")
    time.sleep(5)  # Simula tarea pesada de 5 segundos
    
    connection = get_db_connection()
    if not connection:
        return 0
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Obtener último registro de racha
        cursor.execute("SELECT racha_actual, ultima_fecha FROM rachas WHERE habito_id = %s", (habito_id,))
        racha_actual = cursor.fetchone()
        
        # Obtener registros de cumplimiento de los últimos 30 días
        cursor.execute("""
            SELECT fecha, cumplido FROM registros 
            WHERE habito_id = %s AND fecha >= DATE_SUB(%s, INTERVAL 30 DAY)
            ORDER BY fecha DESC
        """, (habito_id, fecha_registro))
        
        registros = cursor.fetchall()
        
        # Calcular nueva racha
        nueva_racha = 1
        fecha_esperada = datetime.strptime(str(fecha_registro), '%Y-%m-%d').date() - timedelta(days=1)
        
        for registro in registros:
            if registro['cumplido'] and registro['fecha'] == fecha_esperada:
                nueva_racha += 1
                fecha_esperada -= timedelta(days=1)
            else:
                break
        
        # Actualizar racha en la base de datos
        if racha_actual:
            racha_maxima = max(racha_actual['racha_maxima'], nueva_racha)
            cursor.execute("""
                UPDATE rachas 
                SET racha_actual = %s, racha_maxima = %s, ultima_fecha = %s
                WHERE habito_id = %s
            """, (nueva_racha, racha_maxima, fecha_registro, habito_id))
        else:
            cursor.execute("""
                INSERT INTO rachas (habito_id, racha_actual, racha_maxima, ultima_fecha)
                VALUES (%s, %s, %s, %s)
            """, (habito_id, nueva_racha, nueva_racha, fecha_registro))
        
        connection.commit()
        print(f"Racha calculada: {nueva_racha} días")
        
    except Error as e:
        print(f"Error calculando racha: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
    
    return nueva_racha

@app.route('/')
def index():
    """Ruta principal - Interfaz HTML"""
    fecha_actual = datetime.now().strftime('%Y-%m-%d')
    return render_template_string(HTML_TEMPLATE, mensaje=None, datos=None, fecha_actual=fecha_actual, success=False)

@app.route('/habito', methods=['POST'])
def crear_habito():
    """Crear un nuevo hábito"""
    try:
        nombre = request.form.get('nombre')
        frecuencia = request.form.get('frecuencia')
        meta = request.form.get('meta')
        
        if not nombre or not frecuencia or not meta:
            return render_template_string(HTML_TEMPLATE, mensaje="Faltan datos requeridos", 
                                        datos=None, fecha_actual=datetime.now().strftime('%Y-%m-%d'), success=False)
        
        connection = get_db_connection()
        if not connection:
            return render_template_string(HTML_TEMPLATE, mensaje="Error de conexión a BD", 
                                        datos=None, fecha_actual=datetime.now().strftime('%Y-%m-%d'), success=False)
        
        try:
            cursor = connection.cursor()
            query = "INSERT INTO habitos (nombre, frecuencia, meta) VALUES (%s, %s, %s)"
            cursor.execute(query, (nombre, frecuencia, meta))
            connection.commit()
            
            habito_id = cursor.lastrowid
            
            # Inicializar racha para este hábito
            cursor.execute("INSERT INTO rachas (habito_id, racha_actual, racha_maxima) VALUES (%s, 0, 0)", (habito_id,))
            connection.commit()
            
            mensaje = f"Hábito '{nombre}' creado exitosamente con ID: {habito_id}"
            return render_template_string(HTML_TEMPLATE, mensaje=mensaje, datos=None, 
                                        fecha_actual=datetime.now().strftime('%Y-%m-%d'), success=True)
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
                
    except Error as e:
        return render_template_string(HTML_TEMPLATE, mensaje=f"Error en BD: {str(e)}", 
                                    datos=None, fecha_actual=datetime.now().strftime('%Y-%m-%d'), success=False)
    except Exception as e:
        return render_template_string(HTML_TEMPLATE, mensaje=f"Error inesperado: {str(e)}", 
                                    datos=None, fecha_actual=datetime.now().strftime('%Y-%m-%d'), success=False)

@app.route('/cumplimiento', methods=['POST'])
def registrar_cumplimiento():
    """Registrar cumplimiento de hábito con tarea pesada"""
    try:
        habito_id = request.form.get('habito_id')
        fecha = request.form.get('fecha')
        
        if not habito_id or not fecha:
            return render_template_string(HTML_TEMPLATE, mensaje="Faltan datos requeridos", 
                                        datos=None, fecha_actual=datetime.now().strftime('%Y-%m-%d'), success=False)
        
        connection = get_db_connection()
        if not connection:
            return render_template_string(HTML_TEMPLATE, mensaje="Error de conexión a BD", 
                                        datos=None, fecha_actual=datetime.now().strftime('%Y-%m-%d'), success=False)
        
        try:
            cursor = connection.cursor()
            
            # Verificar si ya existe registro para esa fecha
            cursor.execute("SELECT id FROM registros WHERE habito_id = %s AND fecha = %s", (habito_id, fecha))
            if cursor.fetchone():
                return render_template_string(HTML_TEMPLATE, mensaje="Ya existe un registro para esta fecha", 
                                            datos=None, fecha_actual=datetime.now().strftime('%Y-%m-%d'), success=False)
            
            # Insertar registro de cumplimiento
            query = "INSERT INTO registros (habito_id, fecha, cumplido) VALUES (%s, %s, TRUE)"
            cursor.execute(query, (habito_id, fecha))
            connection.commit()
            
            # TAREA PESADA: Calcular racha (time.sleep de 5 segundos)
            racha = calcular_racha(int(habito_id), fecha)
            
            mensaje = f"Cumplimiento registrado exitosamente para fecha {fecha}. Racha actual: {racha} días"
            return render_template_string(HTML_TEMPLATE, mensaje=mensaje, datos=None, 
                                        fecha_actual=datetime.now().strftime('%Y-%m-%d'), success=True)
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
                
    except Error as e:
        return render_template_string(HTML_TEMPLATE, mensaje=f"Error en BD: {str(e)}", 
                                    datos=None, fecha_actual=datetime.now().strftime('%Y-%m-%d'), success=False)
    except Exception as e:
        return render_template_string(HTML_TEMPLATE, mensaje=f"Error inesperado: {str(e)}", 
                                    datos=None, fecha_actual=datetime.now().strftime('%Y-%m-%d'), success=False)

@app.route('/historial')
def consultar_historial():
    """Consultar historial de cumplimiento de un hábito"""
    try:
        habito_id = request.args.get('habito_id')
        
        if not habito_id:
            return render_template_string(HTML_TEMPLATE, mensaje="Se requiere ID del hábito", 
                                        datos=None, fecha_actual=datetime.now().strftime('%Y-%m-%d'), success=False)
        
        connection = get_db_connection()
        if not connection:
            return render_template_string(HTML_TEMPLATE, mensaje="Error de conexión a BD", 
                                        datos=None, fecha_actual=datetime.now().strftime('%Y-%m-%d'), success=False)
        
        try:
            cursor = connection.cursor(dictionary=True)
            
            # Obtener información del hábito
            cursor.execute("SELECT nombre, frecuencia, meta FROM habitos WHERE id = %s", (habito_id,))
            habito = cursor.fetchone()
            
            if not habito:
                return render_template_string(HTML_TEMPLATE, mensaje="Hábito no encontrado", 
                                            datos=None, fecha_actual=datetime.now().strftime('%Y-%m-%d'), success=False)
            
            # Obtener registros de cumplimiento
            cursor.execute("""
                SELECT fecha, cumplido, registrado_en 
                FROM registros 
                WHERE habito_id = %s 
                ORDER BY fecha DESC 
                LIMIT 30
            """, (habito_id,))
            
            registros = cursor.fetchall()
            
            # Obtener racha actual
            cursor.execute("SELECT racha_actual, racha_maxima FROM rachas WHERE habito_id = %s", (habito_id,))
            racha = cursor.fetchone()
            
            # Generar tabla HTML
            html = f"<h3>Historial de '{habito['nombre']}'</h3>"
            html += f"<p><strong>Frecuencia:</strong> {habito['frecuencia']} | <strong>Meta:</strong> {habito['meta']}</p>"
            if racha:
                html += f"<p><strong>Racha actual:</strong> {racha['racha_actual']} días | <strong>Racha máxima:</strong> {racha['racha_maxima']} días</p>"
            html += "<table><tr><th>Fecha</th><th>Cumplido</th><th>Registrado</th></tr>"
            
            for reg in registros:
                cumplido_texto = "✅ Sí" if reg['cumplido'] else "❌ No"
                html += f"<tr><td>{reg['fecha']}</td><td>{cumplido_texto}</td><td>{reg['registrado_en']}</td></tr>"
            
            html += "</table>"
            
            return render_template_string(HTML_TEMPLATE, mensaje=None, datos=html, 
                                        fecha_actual=datetime.now().strftime('%Y-%m-%d'), success=True)
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
                
    except Exception as e:
        return render_template_string(HTML_TEMPLATE, mensaje=f"Error: {str(e)}", 
                                    datos=None, fecha_actual=datetime.now().strftime('%Y-%m-%d'), success=False)

@app.route('/resumen')
def resumen_dia():
    """Ver resumen de hábitos cumplidos vs pendientes del día"""
    try:
        fecha_hoy = datetime.now().strftime('%Y-%m-%d')
        
        connection = get_db_connection()
        if not connection:
            return render_template_string(HTML_TEMPLATE, mensaje="Error de conexión a BD", 
                                        datos=None, fecha_actual=fecha_hoy, success=False)
        
        try:
            cursor = connection.cursor(dictionary=True)
            
            # Total de hábitos
            cursor.execute("SELECT COUNT(*) as total FROM habitos")
            total_habitos = cursor.fetchone()['total']
            
            # Cumplimientos de hoy
            cursor.execute("""
                SELECT COUNT(*) as cumplidos FROM registros 
                WHERE fecha = %s AND cumplido = TRUE
            """, (fecha_hoy,))
            cumplidos_hoy = cursor.fetchone()['cumplidos']
            
            # Lista de hábitos y si se cumplieron hoy
            cursor.execute("""
                SELECT h.id, h.nombre, 
                    CASE WHEN r.id IS NOT NULL THEN '✅ Cumplido' ELSE '⏳ Pendiente' END as estado
                FROM habitos h
                LEFT JOIN registros r ON h.id = r.habito_id AND r.fecha = %s
                ORDER BY h.nombre
            """, (fecha_hoy,))
            
            habitos_estado = cursor.fetchall()
            
            pendientes = total_habitos - cumplidos_hoy
            
            # Generar HTML
            html = f"<h3>Resumen del día {fecha_hoy}</h3>"
            html += f"<p><strong>✅ Cumplidos hoy:</strong> {cumplidos_hoy}</p>"
            html += f"<p><strong>⏳ Pendientes hoy:</strong> {pendientes}</p>"
            html += f"<p><strong>📊 Total de hábitos:</strong> {total_habitos}</p>"
            html += "<table><tr><th>Hábito</th><th>Estado</th></tr>"
            
            for hab in habitos_estado:
                html += f"<tr><td>{hab['nombre']}</td><td>{hab['estado']}</td></tr>"
            
            html += "</table>"
            
            return render_template_string(HTML_TEMPLATE, mensaje=None, datos=html, 
                                        fecha_actual=fecha_hoy, success=True)
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
                
    except Exception as e:
        return render_template_string(HTML_TEMPLATE, mensaje=f"Error: {str(e)}", 
                                    datos=None, fecha_actual=datetime.now().strftime('%Y-%m-%d'), success=False)

@app.route('/habitos')
def listar_habitos():
    """Listar todos los hábitos (consulta que retorna datos guardados)"""
    try:
        connection = get_db_connection()
        if not connection:
            return render_template_string(HTML_TEMPLATE, mensaje="Error de conexión a BD", 
                                        datos=None, fecha_actual=datetime.now().strftime('%Y-%m-%d'), success=False)
        
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT id, nombre, frecuencia, meta, creado_en FROM habitos ORDER BY id")
            habitos = cursor.fetchall()
            
            if not habitos:
                html = "<p>No hay hábitos registrados. Crea uno usando el formulario.</p>"
            else:
                html = "<h3>Lista de Hábitos Registrados</h3>"
                html += "<table><tr><th>ID</th><th>Nombre</th><th>Frecuencia</th><th>Meta</th><th>Creado</th></tr>"
                for hab in habitos:
                    html += f"<tr><td>{hab['id']}</td><td>{hab['nombre']}</td><td>{hab['frecuencia']}</td><td>{hab['meta']}</td><td>{hab['creado_en']}</td></tr>"
                html += "</table>"
            
            return render_template_string(HTML_TEMPLATE, mensaje=None, datos=html, 
                                        fecha_actual=datetime.now().strftime('%Y-%m-%d'), success=True)
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
                
    except Exception as e:
        return render_template_string(HTML_TEMPLATE, mensaje=f"Error: {str(e)}", 
                                    datos=None, fecha_actual=datetime.now().strftime('%Y-%m-%d'), success=False)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
