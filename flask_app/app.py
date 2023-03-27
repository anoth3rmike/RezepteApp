from app import app,db
from app.models import User,Recipe,Ingredient

# Dekoriert die Funktion `make_shell_context` mit dem `shell_context_processor`-Dekorator,
# damit sie automatisch aufgerufen wird, wenn die Flask-Shell gestartet wird
@app.shell_context_processor
def make_shell_context():
     # Gibt ein Wörterbuch zurück, das die in der Flask-Shell verfügbaren Variablen und ihre zugehörigen Objekte definiert
    return {'db':db,'User':User,'Recipe':Recipe,'Ingredient':Ingredient}

