# Usa una imagen base oficial de Python
FROM python:3.10-slim

# Establece la variable de entorno que asegura que la salida de Python se envía directamente al terminal (sin buffer)
ENV PYTHONUNBUFFERED 1

# Establece el directorio de trabajo en el contenedor
WORKDIR /code

# Copia el archivo de requisitos en el directorio de trabajo
COPY requirements.txt /code/

# Instala las dependencias del proyecto
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código del proyecto en el directorio de trabajo
COPY . /code/

# Establece la variable de entorno para el módulo de configuración de Django
ENV DJANGO_SETTINGS_MODULE=myproject.settings

# Ejecuta collectstatic para recopilar archivos estáticos
RUN python manage.py collectstatic --noinput

# Exponer el puerto 8000 para el servidor
EXPOSE 8000

# Comando por defecto para ejecutar la aplicación, incluyendo la creación del superusuario
CMD sh -c "python manage.py migrate && python manage.py shell < create_superuser.py && gunicorn --bind 0.0.0.0:8000 --limit-request-line 15000 myproject.wsgi:application"
