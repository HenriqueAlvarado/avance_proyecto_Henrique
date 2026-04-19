# Dockerfile para Plataforma de Hábitos
FROM python:3.9-slim

# Establecer directorio de trabajo
WORKDIR /app

# Copiar archivos de requisitos
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY app.py .

# Exponer el puerto de la aplicación
EXPOSE 5000

# Variables de entorno (se sobrescribirán al correr el contenedor)
ENV DB_HOST=db-actividad.cjbbd4mntf9v.us-east-1.rds.amazonaws.com
ENV DB_PORT=3306
ENV DB_USER=admin
ENV DB_NAME=habbitos_db

# Comando para ejecutar la aplicación
CMD ["python", "app.py"]
