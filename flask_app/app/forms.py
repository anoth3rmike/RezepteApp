# Importiert Module und Erweiterungen
from flask_wtf import FlaskForm
from wtforms import StringField,BooleanField,PasswordField,SubmitField,TextAreaField
from wtforms.validators import DataRequired,EqualTo,ValidationError,Length
from .models import User

# Form für die Benutzerauthentifizierung
class LoginForm(FlaskForm):
    username = StringField('Benutzername oder Email',validators=[DataRequired('Feld darf nicht leer sein'),Length(max=64)])
    password = PasswordField('Passwort',validators=[DataRequired('Feld darf nicht leer sein')])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Anmelden')

# Form für die Benutzerregistrierung (überprfüft falsche Passworteingabe)
class RegisterForm(FlaskForm):
    username = StringField('Benutzername oder Email',validators=[DataRequired('Feld darf nicht leer sein'),Length(max=64)])
    password = PasswordField('Passwort',validators=[DataRequired('Feld darf nicht leer sein')])
    confirm_password = PasswordField('Passwort bestätigen',validators=[DataRequired('Feld darf nicht leer sein'),EqualTo('password','Passwort stimmt nicht überein.')])
    submit  =SubmitField('Registrierung')


    # Funktion, um einen Fehler auszulösen, wenn ein Benutzername bereits verwendet wird
    def validate_username(self,given_username):
        user = User.query.filter_by(username = given_username.data).first()
        if user is not None:
            raise ValidationError('Benutzername bereits registriert')

# Form für die Erstellung von Rezepten
class CreateRecipeForm(FlaskForm):
    title = StringField('Titel :',validators=[DataRequired('Feld darf nicht leer sein'),Length(max=64)])
    preparation = TextAreaField('Zubereitung:',validators=[DataRequired('Feld darf nicht leer sein'),Length(max=400)])
    ingredients = TextAreaField('Zutaten: Bitte geben Sie Ihre Zutaten ein (Komma getrennt)',validators=[DataRequired('Feld darf nicht leer sein')])
    