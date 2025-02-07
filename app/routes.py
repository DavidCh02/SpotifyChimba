# app/routes.py

import os
from datetime import timedelta

from flask import Blueprint, render_template, request, redirect, url_for, flash, Response
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
import app
from app.models import Usuario, Artista, Album, Cancion, FavoritoAlbum, FavoritoCancion
from app import db
from app.models import Playlist
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
    # Obtener las playlists del usuario actual
    playlists = Playlist.query.filter_by(id_usuario=current_user.id_usuario).all()

    # Obtener todas las canciones disponibles (para agregar a playlists)
    canciones = Cancion.query.all()

    return render_template('profile.html', playlists=playlists, canciones=canciones)

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

from mutagen.mp3 import MP3
from werkzeug.utils import secure_filename

@main.route('/admin', methods=['GET', 'POST'])
@requires_auth  # Requiere autenticación para acceder al panel de administración
def admin():
    if request.method == 'POST':
        # Agregar un artista
        if 'add_artist' in request.form:
            # Obtener todos los datos del formulario
            nombre = request.form.get('nombre')
            descripcion = request.form.get('descripcion')
            pais_origen = request.form.get('pais_origen')
            fecha_inicio = request.form.get('fecha_inicio')

            # Validar que el campo "nombre" no esté vacío
            if not nombre:
                flash("El nombre del artista es obligatorio.", "danger")
                return redirect(url_for('main.admin'))

            # Crear un nuevo artista
            new_artist = Artista(
                nombre=nombre,
                descripcion=descripcion,
                pais_origen=pais_origen,
                fecha_inicio=fecha_inicio
            )
            try:
                db.session.add(new_artist)
                db.session.commit()
                flash('Artista agregado correctamente', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f"Error al agregar el artista: {str(e)}", "danger")

        # Agregar un álbum
        elif 'add_album' in request.form:
            titulo = request.form.get('titulo')
            id_artista = request.form.get('id_artista')

            # Validar que el campo "título" y "id_artista" no estén vacíos
            if not titulo or not id_artista:
                flash("El título del álbum y el artista son obligatorios.", "danger")
                return redirect(url_for('main.admin'))

            # Crear un nuevo álbum
            new_album = Album(titulo=titulo, id_artista=id_artista)
            try:
                db.session.add(new_album)
                db.session.flush()  # Guarda temporalmente para obtener el ID del álbum
                # Subir canciones asociadas al álbum
                canciones = request.files.getlist('canciones')  # Obtener las canciones subidas
                for cancion in canciones:
                    if cancion.filename:  # Verificar que el archivo no esté vacío
                        filename = secure_filename(cancion.filename)
                        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                        cancion.save(filepath)  # Guardar la canción en el servidor

                        # Obtener metadatos del archivo
                        tamaño = os.path.getsize(filepath)
                        formato = filename.split('.')[-1].lower()
                        audio = MP3(filepath)
                        duracion_segundos = int(audio.info.length)
                        minutos = duracion_segundos // 60
                        segundos = duracion_segundos % 60
                        duracion = f"{minutos}:{segundos:02d}"

                        # Crear la canción en la base de datos y asociarla con el álbum
                        nueva_cancion = Cancion(
                            titulo=filename,
                            duracion=duracion,
                            es_sencillo=False,
                            id_artista=id_artista,
                            id_album=new_album.id_album,
                            ruta_archivo=filename,
                            tamanio=tamaño,
                            formato=formato
                        )
                        db.session.add(nueva_cancion)
                db.session.commit()
                flash('Álbum agregado correctamente', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f"Error al agregar el álbum: {str(e)}", "danger")

        # Subir una canción adicional
        elif 'upload_song' in request.form:
            titulo = request.form.get('titulo')
            id_artista = request.form.get('id_artista')
            id_album = request.form.get('id_album')
            archivo = request.files.get('archivo')

            # Validar que el campo "título", "id_artista" y el archivo no estén vacíos
            if not titulo or not id_artista or not archivo:
                flash("El título, el artista y el archivo de la canción son obligatorios.", "danger")
                return redirect(url_for('main.admin'))

            # Guardar el archivo de la canción
            filename = secure_filename(archivo.filename)
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            archivo.save(filepath)

            # Obtener el tamaño del archivo
            tamaño = os.path.getsize(filepath)

            # Obtener el formato del archivo
            formato = filename.split('.')[-1].lower()

            # Obtener la duración del archivo usando Mutagen
            try:
                audio = MP3(filepath)
                duracion_segundos = int(audio.info.length)
                minutos = duracion_segundos // 60
                segundos = duracion_segundos % 60
                duracion = f"{minutos}:{segundos:02d}"
            except Exception as e:
                flash(f"Error al leer los metadatos del archivo: {str(e)}", "danger")
                return redirect(url_for('main.admin'))

            # Crear la canción en la base de datos
            nueva_cancion = Cancion(
                titulo=titulo,
                duracion=duracion,
                es_sencillo=(id_album is None),
                id_artista=id_artista,
                id_album=id_album if id_album else None,  # Si no se selecciona un álbum, dejarlo como None
                ruta_archivo=filename,
                tamanio=tamaño,  # Usar "tamanio" en lugar de "tamaño"
                formato=formato
            )
            try:
                db.session.add(nueva_cancion)
                db.session.commit()
                flash('Canción subida correctamente', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f"Error al subir la canción: {str(e)}", "danger")
            return redirect(url_for('main.admin'))

    # Obtener los artistas, álbumes y canciones para mostrar en el formulario
    artistas = Artista.query.all()
    albumes = Album.query.all()
    canciones = Cancion.query.all()
    return render_template('admin.html', artistas=artistas, albumes=albumes, canciones=canciones)


@main.route('/delete_song/<int:id_cancion>', methods=['POST'])
@login_required
def delete_song(id_cancion):
    cancion = Cancion.query.get_or_404(id_cancion)

    try:
        db.session.delete(cancion)
        db.session.commit()
        flash('Canción eliminada correctamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f"Error al eliminar la canción: {str(e)}", "danger")

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


# Marcar/Desmarcar una canción como favorita
@main.route('/toggle_favorite_song/<int:id_cancion>', methods=['POST'])
@login_required
def toggle_favorite_song(id_cancion):
    # Verificar si la canción ya está marcada como favorita
    favorito = FavoritoCancion.query.filter_by(id_usuario=current_user.id_usuario, id_cancion=id_cancion).first()
    if favorito:
        # Si ya es favorita, eliminarla
        db.session.delete(favorito)
        mensaje = "Canción eliminada de favoritos."
    else:
        # Si no es favorita, agregarla
        nuevo_favorito = FavoritoCancion(id_usuario=current_user.id_usuario, id_cancion=id_cancion)
        db.session.add(nuevo_favorito)
        mensaje = "Canción agregada a favoritos."

    db.session.commit()
    flash(mensaje, 'success')
    return redirect(request.referrer)


# Marcar/Desmarcar un álbum como favorito
@main.route('/toggle_favorite_album/<int:id_album>', methods=['POST'])
@login_required
def toggle_favorite_album(id_album):
    # Verificar si el álbum ya está marcado como favorito
    favorito = FavoritoAlbum.query.filter_by(id_usuario=current_user.id_usuario, id_album=id_album).first()
    if favorito:
        # Si ya es favorito, eliminarlo
        db.session.delete(favorito)
        mensaje = "Álbum eliminado de favoritos."
    else:
        # Si no es favorito, agregarlo
        nuevo_favorito = FavoritoAlbum(id_usuario=current_user.id_usuario, id_album=id_album)
        db.session.add(nuevo_favorito)
        mensaje = "Álbum agregado a favoritos."

    db.session.commit()
    flash(mensaje, 'success')
    return redirect(request.referrer)

@main.route('/edit_album/<int:id_album>', methods=['GET', 'POST'])
@requires_auth
def edit_album(id_album):
    # Obtener el álbum por su ID
    album = Album.query.get_or_404(id_album)

    if request.method == 'POST':
        # Actualizar los datos del álbum
        album.titulo = request.form.get('titulo')
        album.id_artista = request.form.get('id_artista')
        try:
            db.session.commit()
            flash('Álbum actualizado correctamente', 'success')
            return redirect(url_for('main.admin'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error al actualizar el álbum: {str(e)}", "danger")

    # Obtener los artistas para el menú desplegable
    artistas = Artista.query.all()
    return render_template('edit_album.html', album=album, artistas=artistas)

@main.route('/delete_album/<int:id_album>', methods=['POST'])
@requires_auth
def delete_album(id_album):
    album = Album.query.get_or_404(id_album)
    try:
        # Eliminar todas las canciones asociadas al álbum
        for cancion in album.canciones:
            db.session.delete(cancion)
        # Eliminar el álbum
        db.session.delete(album)
        db.session.commit()
        flash('Álbum eliminado correctamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f"Error al eliminar el álbum: {str(e)}", "danger")
    return redirect(url_for('main.admin'))

@main.route('/create_playlist', methods=['POST'])
@login_required
def create_playlist():
    nombre = request.form.get('nombre')
    if not nombre:
        flash("El nombre de la playlist es obligatorio.", "danger")
        return redirect(url_for('main.profile'))

    nueva_playlist = Playlist(nombre=nombre, id_usuario=current_user.id_usuario)
    try:
        db.session.add(nueva_playlist)
        db.session.commit()
        flash("Playlist creada correctamente.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error al crear la playlist: {str(e)}", "danger")

    return redirect(url_for('main.profile'))
@main.route('/add_to_playlist/<int:id_cancion>', methods=['POST'])
@login_required
def add_to_playlist(id_cancion):
    id_playlist = request.form.get('id_playlist')  # Obtener el ID de la playlist desde el formulario
    if not id_playlist:
        flash("Selecciona una playlist válida.", "danger")
        return redirect(url_for('main.profile'))

    playlist = Playlist.query.get_or_404(id_playlist)
    cancion = Cancion.query.get_or_404(id_cancion)

    if playlist.id_usuario != current_user.id_usuario:
        flash("No tienes permiso para modificar esta playlist.", "danger")
        return redirect(url_for('main.profile'))

    if cancion in playlist.canciones:
        flash("La canción ya está en la playlist.", "warning")
    else:
        playlist.canciones.append(cancion)
        try:
            db.session.commit()
            flash("Canción agregada a la playlist correctamente.", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Error al agregar la canción: {str(e)}", "danger")

    return redirect(url_for('main.profile'))
@main.route('/delete_playlist/<int:id_playlist>', methods=['POST'])
@login_required
def delete_playlist(id_playlist):
    playlist = Playlist.query.get_or_404(id_playlist)

    if playlist.id_usuario != current_user.id_usuario:
        flash("No tienes permiso para eliminar esta playlist.", "danger")
        return redirect(url_for('main.profile'))

    try:
        db.session.delete(playlist)
        db.session.commit()
        flash("Playlist eliminada correctamente.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error al eliminar la playlist: {str(e)}", "danger")

    return redirect(url_for('main.profile'))