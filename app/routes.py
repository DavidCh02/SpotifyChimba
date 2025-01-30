# app/routes.py

import os
from datetime import timedelta

from flask import Blueprint, render_template, request, redirect, url_for, flash, Response
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
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
    canciones = Cancion.query.all()
    return render_template('index.html', canciones=canciones)
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
        elif 'upload_song' in request.form:
            titulo = request.form.get('titulo')
            id_artista = request.form.get('id_artista')
            id_album = request.form.get('id_album')
            archivo = request.files['archivo']
            archivo_path = os.path.join(UPLOAD_FOLDER, archivo.filename)
            archivo.save(archivo_path)

            # Usando Mutagen para obtener la duración de la canción
            audio = MP3(archivo_path, ID3=EasyID3)
            duracion_segundos = int(audio.info.length)  # Duración en segundos

            # Convertir segundos a formato hh:mm:ss
            duracion_timedelta = str(timedelta(seconds=duracion_segundos))

            # Ahora puedes guardar la duración en formato TIME
            new_song = Cancion(
                titulo=titulo,
                id_artista=id_artista,
                id_album=id_album,
                ruta_archivo=archivo.filename,
                duracion=duracion_timedelta  # Guardamos la duración como tiempo
            )
            db.session.add(new_song)
            db.session.commit()
            flash('Canción subida correctamente', 'success')

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
