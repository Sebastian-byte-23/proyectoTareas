from flask_sqlalchemy import SQLAlchemy

# Instancia de SQLAlchemy
db = SQLAlchemy()

def init_app(app):
    """
    Inicializa la extensión SQLAlchemy con la aplicación Flask.
    """
    db.init_app(app)
