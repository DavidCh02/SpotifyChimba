import os

class Config:
    # Clave secreta para la seguridad de la aplicación (debería ser más segura en producción)
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'root'

    # Configuración de la base de datos
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql+mysqlconnector://root:root@localhost:3307/musicwebdb'
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Desactiva el seguimiento de modificaciones para mejorar el rendimiento

    # Carpeta para subir archivos
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')

    # Límite máximo de tamaño para los archivos subidos (50 MB)
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024

    # Formatos de archivo permitidos
    ALLOWED_EXTENSIONS = {'mp3', 'wav', 'flac'}

    # Debug mode (solo para desarrollo)
    DEBUG = True

