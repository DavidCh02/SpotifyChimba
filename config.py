import os

class Config:
    SECRET_KEY = 'root'
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:root@localhost:3307/musicwebdb'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')