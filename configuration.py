import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Configuration(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOADS_DEFAULT_DEST = os.environ.get('UPLOADS_DEFAULT_DEST') or \
                           r'C:\Users\yqk\Desktop\AD\ANUNCIOS\PracticaExploratoria\app\static'
    UPLOADS_DEFAULT_URL = os.environ.get('UPLOADS_DEFAULT_URL') or \
                          'http://localhost:5000/static/'

    UPLOADED_IMAGE_DEST = os.environ.get('UPLOADED_IMAGE_DEST') or \
                          r'C:\Users\yqk\Desktop\AD\ANUNCIOS\PracticaExploratoria\app\static'
    UPLOADED_IMAGE_URL = os.environ.get('UPLOADED_IMAGE_URL') or \
                         'http://localhost:5000/static/'