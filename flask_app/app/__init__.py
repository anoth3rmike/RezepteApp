# Importiert Module und Erweiterungen
from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_httpauth import HTTPBasicAuth

# Erstellt eine Flask-Instanz für die Webanwendung
app = Flask(__name__)

# Lädt die Konfiguration aus der Config-Klasse
app.config.from_object(Config)

# Erstellt eine SQLAlchemy-Instanz für die Datenbankverbindung
db = SQLAlchemy(app)

# Erstellt eine Migrate-Instanz für die Datenbankmigrationen
migrate = Migrate(app, db)

# Erstellt eine LoginManager-Instanz für die Benutzerauthentifizierung und -verwaltung
login = LoginManager(app)

# Erstellt eine HTTPBasicAuth-Instanz für die HTTP-Authentifizierung
auth = HTTPBasicAuth()

# Definieren der Login-Seite
login.login_view = 'login'


# Importiert die Routen und Modelle für die Anwendung
from . import routes, models 
# Durch das Importieren am Ende des Codes soll sichergestellt werden, dass die Anwendungsrouten und Modelle richtig registriert und initialisiert werden, nachdem alle erforderlichen Erweiterungen und Instanzen erstellt wurden.
