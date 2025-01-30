from app import db
from flask_login import UserMixin
from app import login_manager


@login_manager.user_loader
def load_user(id_usuario):
    return Usuario.query.get(int(id_usuario))


class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuario'
    id_usuario = db.Column(db.Integer, primary_key=True)
    nombre_usuario = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    playlists = db.relationship('Playlist', backref='propietario', lazy=True)
    favoritos_canciones = db.relationship('FavoritoCancion', backref='usuario_fav', lazy=True)
    favoritos_albumes = db.relationship('FavoritoAlbum', backref='usuario_fav', lazy=True)

    # Implementa get_id() para Flask-Login
    def get_id(self):
        return str(self.id_usuario)

class Artista(db.Model):
    __tablename__ = 'artista'
    id_artista = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    pais_origen = db.Column(db.String(50))
    fecha_inicio = db.Column(db.Date)

    albumes = db.relationship('Album', backref='artista', lazy=True)
    canciones = db.relationship('Cancion', backref='artista', lazy=True)


class Album(db.Model):
    __tablename__ = 'album'
    id_album = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    fecha_lanzamiento = db.Column(db.Date)
    genero = db.Column(db.String(50))
    id_artista = db.Column(db.Integer, db.ForeignKey('artista.id_artista'), nullable=False)

    canciones = db.relationship('Cancion', backref='album', lazy=True)


class Cancion(db.Model):
    __tablename__ = 'cancion'
    id_cancion = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    duracion = db.Column(db.String(10))
    es_sencillo = db.Column(db.Boolean, default=False)
    id_artista = db.Column(db.Integer, db.ForeignKey('artista.id_artista'))
    id_album = db.Column(db.Integer, db.ForeignKey('album.id_album'))
    ruta_archivo = db.Column(db.String(200))


class Playlist(db.Model):
    __tablename__ = 'playlist'
    id_playlist = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    fecha_creacion = db.Column(db.Date, default=db.func.current_date())
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'), nullable=False)

    canciones = db.relationship('PlaylistCancion', backref='playlist', lazy=True)
    historial = db.relationship('Historial', backref='playlist', lazy=True)
    favoritos_canciones = db.relationship('FavoritoCancion', backref='playlist_fav', lazy=True)
    favoritos_albumes = db.relationship('FavoritoAlbum', backref='playlist_fav', lazy=True)


class PlaylistCancion(db.Model):
    __tablename__ = 'playlist_cancion'
    id_playlist = db.Column(db.Integer, db.ForeignKey('playlist.id_playlist'), primary_key=True)
    id_cancion = db.Column(db.Integer, db.ForeignKey('cancion.id_cancion'), primary_key=True)
    orden = db.Column(db.Integer)


class Historial(db.Model):
    __tablename__ = 'historial'
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'), primary_key=True)
    id_cancion = db.Column(db.Integer, db.ForeignKey('cancion.id_cancion'), primary_key=True)
    id_playlist = db.Column(db.Integer, db.ForeignKey('playlist.id_playlist'))
    fecha = db.Column(db.DateTime, default=db.func.current_timestamp())


class FavoritoCancion(db.Model):
    __tablename__ = 'favorito_cancion'
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'), primary_key=True)
    id_cancion = db.Column(db.Integer, db.ForeignKey('cancion.id_cancion'), primary_key=True)
    id_playlist = db.Column(db.Integer, db.ForeignKey('playlist.id_playlist'))


class FavoritoAlbum(db.Model):
    __tablename__ = 'favorito_album'
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'), primary_key=True)
    id_album = db.Column(db.Integer, db.ForeignKey('album.id_album'), primary_key=True)
    id_playlist = db.Column(db.Integer, db.ForeignKey('playlist.id_playlist'))
