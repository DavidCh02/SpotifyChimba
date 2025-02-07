from app import db
from flask_login import UserMixin
from app import login_manager

# Cargar usuario para Flask-Login
@login_manager.user_loader
def load_user(id_usuario):
    return Usuario.query.get(int(id_usuario))

# Modelo Usuario
class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuario'
    id_usuario = db.Column(db.Integer, primary_key=True)
    nombre_usuario = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    # Relación con canciones favoritas
    favoritos_canciones = db.relationship(
        'FavoritoCancion',
        backref='usuario_fav',
        lazy=True
    )

    # Relación con álbumes favoritos
    favoritos_albumes = db.relationship(
        'FavoritoAlbum',
        backref='usuario_fav',
        lazy=True
    )

    # Implementa get_id() para Flask-Login
    def get_id(self):
        return str(self.id_usuario)

# Modelo Artista
class Artista(db.Model):
    __tablename__ = 'artista'
    id_artista = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    pais_origen = db.Column(db.String(50))
    fecha_inicio = db.Column(db.Date)

    # Relaciones
    albumes = db.relationship('Album', backref='artista', lazy=True)
    canciones = db.relationship('Cancion', backref='artista_relacionado', lazy=True)

# Modelo Album
class Album(db.Model):
    __tablename__ = 'album'
    id_album = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    fecha_lanzamiento = db.Column(db.Date)
    id_artista = db.Column(db.Integer, db.ForeignKey('artista.id_artista'), nullable=False)

    # Relación con FavoritoAlbum
    favoritos = db.relationship('FavoritoAlbum', backref='album', lazy=True)

# Modelo Cancion
class Cancion(db.Model):
    __tablename__ = 'cancion'
    id_cancion = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    duracion = db.Column(db.String(10))
    es_sencillo = db.Column(db.Boolean, default=False)
    id_artista = db.Column(db.Integer, db.ForeignKey('artista.id_artista'))
    id_album = db.Column(db.Integer, db.ForeignKey('album.id_album'))
    ruta_archivo = db.Column(db.String(200))
    tamanio = db.Column(db.Integer)
    formato = db.Column(db.String(10))

    # Relaciones
    favoritos = db.relationship('FavoritoCancion', backref='cancion', lazy=True)
    artista = db.relationship('Artista', backref='cancion_relacionada', lazy=True)
    album = db.relationship('Album', backref='canciones')  # Relación con Album

# Tabla intermedia para la relación muchos-a-muchos entre Playlist y Cancion
playlist_cancion = db.Table(
    'playlist_cancion',
    db.Column('id_playlist', db.Integer, db.ForeignKey('playlist.id_playlist'), primary_key=True),
    db.Column('id_cancion', db.Integer, db.ForeignKey('cancion.id_cancion'), primary_key=True)
)

# Modelo Playlist
class Playlist(db.Model):
    __tablename__ = 'playlist'
    id_playlist = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'), nullable=False)

    # Relación con el usuario
    usuario = db.relationship('Usuario', backref='playlists')

    # Relación con las canciones (tabla intermedia)
    canciones = db.relationship('Cancion', secondary=playlist_cancion, backref='playlists')

# Modelo FavoritoCancion
class FavoritoCancion(db.Model):
    __tablename__ = 'favorito_cancion'
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'), primary_key=True)
    id_cancion = db.Column(db.Integer, db.ForeignKey('cancion.id_cancion'), primary_key=True)

# Modelo FavoritoAlbum
class FavoritoAlbum(db.Model):
    __tablename__ = 'favorito_album'
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'), primary_key=True)
    id_album = db.Column(db.Integer, db.ForeignKey('album.id_album'), primary_key=True)