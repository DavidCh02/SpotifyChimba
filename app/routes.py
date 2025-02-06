# app/routes.py

import os
from datetime import timedelta

from flask import Blueprint, render_template, request, redirect, url_for, flash, Response
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
import app
from app.models import Usuario, Playlist, Artista, Album, Cancion
from app import db
from functools import wraps
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3

main = Blueprint('main', __name__)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# app/routes.py

@main.route('/')
def index():
    canciones = Cancion.query.all()  # Obtener todas las canciones
    albumes = Album.query.all()  # Obtener todos los álbumes
    return render_template('index.html', canciones=canciones, albumes=albumes)

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = Usuario.query.filter_by(nombre_usuario=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Inicio de sesión exitoso', 'success')
            return redirect(url_for('main.index'))

        flash('Usuario o contraseña incorrectos', 'danger')

    return render_template('login.html')

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        hashed_password = generate_password_hash(password)
        new_user = Usuario(nombre_usuario=username, password=hashed_password)

        db.session.add(new_user)
        db.session.commit()
        flash('Usuario registrado correctamente', 'success')

        return redirect(url_for('main.login'))

    return render_template('register.html')

@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@main.route('/playlist/<int:id_playlist>')
@login_required
def playlist(id_playlist):
    playlist = Playlist.query.get_or_404(id_playlist)
    return render_template('playlist.html', playlist=playlist)

@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada correctamente', 'info')
    return redirect(url_for('main.index'))

def check_auth(username, password):
    """Verifica si el usuario y la contraseña son correctos."""
    return username == 'admin' and password == 'adminpassword'

def authenticate():
    """Envía una respuesta 401 para habilitar la autenticación básica."""
    return Response(
        'Debes ingresar con las credenciales correctas', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    """Decorador para requerir autenticación básica."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

# app/routes.py

# app/routes.py

# app/routes.py

@main.route('/admin', methods=['GET', 'POST'])
@requires_auth
def admin():
    if request.method == 'POST':
        if 'add_artist' in request.form:
            nombre = request.form.get('nombre')
            new_artist = Artista(nombre=nombre)
            db.session.add(new_artist)
            db.session.commit()
            flash('Artista agregado correctamente', 'success')
        elif 'add_album' in request.form:
            titulo = request.form.get('titulo')
            id_artista = request.form.get('id_artista')
            new_album = Album(titulo=titulo, id_artista=id_artista)
            db.session.add(new_album)
            db.session.commit()
            flash('Álbum agregado correctamente', 'success')

            # Agregar canciones después de crear el álbum
            canciones = request.files.getlist('canciones')  # Obtén las canciones subidas
            for cancion in canciones:
                filename = secure_filename(cancion.filename)
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                cancion.save(filepath)  # Guarda la canción en el servidor

                # Crea las canciones en la base de datos y asócialas con el álbum
                nueva_cancion = Cancion(
                    titulo=cancion.filename,
                    ruta_archivo=filename,
                    id_artista=id_artista,
                    id_album=new_album.id_album
                )
                db.session.add(nueva_cancion)
            db.session.commit()

        elif 'upload_song' in request.form:
            # Subir una canción adicional (si no se subió al crear el álbum)
            titulo = request.form['titulo']
            id_artista = request.form['id_artista']
            id_album = request.form['id_album']
            archivo = request.files['archivo']

            if not id_album:
                id_album = None  # Si no se selecciona un álbum, lo dejamos como None

            # Guardar el archivo de la canción
            filename = secure_filename(archivo.filename)
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            archivo.save(filepath)

            # Crear y guardar la canción en la base de datos
            nueva_cancion = Cancion(
                titulo=titulo,
                ruta_archivo=filename,
                id_artista=id_artista,
                id_album=id_album
            )
            db.session.add(nueva_cancion)
            db.session.commit()

            flash('Canción subida correctamente', 'success')
            return redirect(url_for('main.admin'))

    # Obtener los artistas y álbumes para el formulario
    artistas = Artista.query.all()
    albumes = Album.query.all()
    canciones = Cancion.query.all()

    return render_template('admin.html', artistas=artistas, albumes=albumes, canciones=canciones)


@main.route('/delete_song/<int:id_cancion>', methods=['POST'])
@requires_auth
def delete_song(id_cancion):
    song = Cancion.query.get_or_404(id_cancion)
    db.session.delete(song)
    db.session.commit()
    flash('Canción eliminada correctamente', 'success')
    return redirect(url_for('main.admin'))

@main.route('/edit_song/<int:id_cancion>', methods=['GET', 'POST'])
@requires_auth
def edit_song(id_cancion):
    song = Cancion.query.get_or_404(id_cancion)
    if request.method == 'POST':
        song.titulo = request.form.get('titulo')
        song.id_artista = request.form.get('id_artista')
        song.id_album = request.form.get('id_album')
        db.session.commit()
        flash('Canción editada correctamente', 'success')
        return redirect(url_for('main.admin'))
    artistas = Artista.query.all()
    albumes = Album.query.all()
    return render_template('edit_song.html', song=song, artistas=artistas, albumes=albumes)

# app/routes.py

@main.route('/songs')
@login_required
def songs():
    canciones = Cancion.query.all()
    return render_template('songs.html', canciones=canciones)

from flask import send_from_directory, current_app

@main.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

@main.route('/album/<int:id_album>')
@login_required
def album(id_album):
    album = Album.query.get_or_404(id_album)
    return render_template('album.html', album=album)
