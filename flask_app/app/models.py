# Importiert Module und Erweiterungen
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login
#from sqlalchemy.inspection import inspect

# Serializer Klasse, für die JSON-Konvertierung
# Der Serializer wird verwendet, um die Serialisierung (als Dictionary darstellen) von SQLAlchemy-Objekten in JSON-Format zu ermöglichen. Damit dies für die API verwendet werden kann.
class Serializer(object):

# Methode zum Serialisieren einer Liste von Objekte
    @staticmethod
    def serialize_list(l):
        return [m.serialize() for m in l]

#User Klasse 
class User(UserMixin, db.Model, Serializer):
    # Datenbank-Tabellenspalten für den User
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    hashed_password = db.Column(db.String(128))
    # Beziehung zwischen User und Recipe
    recipes = db.relationship("Recipe", backref="author")
    # Methode zum Serialisieren eines User-Objekts
    def serialize(self):
        return {
            'id': self.id,
            'user_name': self.username
        }
    # Methode zum Serialisieren einer Liste von User-Objekten
    @staticmethod
    def serialize_list(l):
        return [m.serialize() for m in l]
    # Repräsentation eines User-Objekt
    def __repr__(self):
        return f"<User {self.username}>"
    # Methode zum Setzen des Passworts (Hash)
    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)
    # Methode zum Überprüfen des Passworts (Hash)
    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

# Recipe Klasse
class Recipe(db.Model, Serializer):
    # Datenbank-Tabellenspalten für das Recipe
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64))
    preparation = db.Column(db.String(400))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    # Beziehung zwischen Recipe und Ingredient
    ingredients = db.relationship('Ingredient', backref='recipe', cascade="all, delete-orphan")
    # Methode zum Serialisieren eines Recipe-Objekt
    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'preparation': self.preparation,
            'author': self.author.username,
            'ingredients': [ingredient.serialize() for ingredient in self.ingredients]

        }

# Ingredient Klasse
class Ingredient(db.Model, Serializer):
    # Datenbank-Tabellenspalten für das Ingredient
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))

    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'))
    # Methode zum Serialisieren eines Ingredient-Objekts
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'recipe_id': self.recipe_id
        }

# User-Loader-Funktion für Flask-Login
@login.user_loader
def load_user(id):
    return User.query.get(int(id))
