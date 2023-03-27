# Importiert Module und Erweiterungen
from flask import render_template,url_for,redirect,flash,request,jsonify,abort,g
from werkzeug.urls import url_parse
from flask_login import current_user,login_user,logout_user,login_required
from app import app,db,auth
from app.models import User,Recipe,Ingredient
from app.forms import LoginForm,RegisterForm,CreateRecipeForm






# Hauptansicht für die Startseite (Anmeldung erforderlich)
@app.route('/')
@app.route('/index')
@login_required
def index():
    title = "Home"
    return render_template('index.html', title=title)


# Anmelderoute
@app.route('/login',methods=['POST','GET'])
def login():
    # Seitentitel
    title = 'Login'

    form = LoginForm()
    if current_user.is_authenticated: 
        return redirect(url_for('index'))

    if form.validate_on_submit():
        user = User.query.filter_by(username = form.username.data ).first()
        
        # Überürft ob ein Username vorhanden ist und ob das Passwort stimmt
        if user is None or not user.check_password(form.password.data):
            flash('Benutzer ist ungültig oder falsche Passwort',"alert alert-danger")
            return redirect(url_for('login'))
        
        login_user(user,remember=form.remember_me.data)
        
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)  
    
    return render_template('login.html',title = title , form = form )

# Abmeldung 
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

# Registrierung
@app.route('/register',methods=['POST','GET'])
def register():
    title = "Registrierung"
    if current_user.is_authenticated: 
        return redirect(url_for('index'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username = form.username.data) 
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        
        return redirect(url_for('login'))
    
    
    return render_template('register.html',form = form,title = title)

# Ansicht für die Anzeige der Rezepte des aktuellen Benutzers (Anmeldung erforderlich)
@app.route('/my_recipes',methods=['GET'])
@login_required
def my_recipes():
    title = 'Meine Rezepte'
    recipes = Recipe.query.filter_by( author = current_user)
    
    recipes = Recipe.serialize_list(recipes)
    
    return render_template('my_recipes.html',recipes=recipes,title = title)


# Ansicht zum Erstellen von Rezepten (Anmeldung erforderlich)
@app.route('/create_recipe',methods=['GET','POST'])
@login_required
def create_recipe():
    form = CreateRecipeForm()
    if form.validate_on_submit():
        #get info from form
        title = form.title.data
        preparation = form.preparation.data
        ingredients_names = form.ingredients.data
        
        #Teilt Zutaten in eine Liste auf
        ingredients_list = ingredients_names.split(",")

        #Erstellt ein neues Rezept
        new_recipe = Recipe( title = title , preparation = preparation , author = current_user)
        for ingredient in ingredients_list:
            ingredient = Ingredient( name = ingredient , recipe = new_recipe)
            new_recipe.ingredients.append(ingredient)

        db.session.add(new_recipe)
        db.session.commit()
        
        #Gibt eine Warnung in grün "erflogreich" aus
        flash('Rezept wurde erfolgreich erstellt',category='alert alert-success')

        return redirect(url_for('my_recipes'))

    title = "Erstelle dein Rezept"
    return render_template('create_recipe.html',form=form,title = title)



# Ansicht zum editieren eines spezifischen Rezeptes
@app.route('/edit_recipe/<int:recipe_id>',methods = ['GET','POST'])
@login_required
def edit_recipe(recipe_id):
    form = CreateRecipeForm()

    if form.validate_on_submit():
        
        recipe = Recipe.query.filter_by( id = recipe_id ).first()
        if not recipe:
            # Gibt eine Warunung in rot aus falls das Rezept nicht gefunden wird
            flash('Rezept nicht gefunden',"alert alert-danger")
            return render_template(url_for('my_recipes'))

        
        #get info from form
        title = form.title.data
        preparation = form.preparation.data
        ingredients_names = form.ingredients.data
        
        # Schreibt Zutaten in eine Liste (kommasepariert)
        ingredients_list = ingredients_names.split(",")
        #delete the old recipe from the data base
        db.session.delete(recipe)
        #create a recipe with the same id
        modified_recipe = Recipe ( title = title , preparation = preparation , id = recipe_id)
        for ingredient in ingredients_list:
            ingredient = Ingredient( name = ingredient , recipe = modified_recipe)
            modified_recipe.ingredients.append(ingredient)
        db.session.add(modified_recipe)
        db.session.commit()
        flash('Rezept wurde erfolgreich editiert',category='alert alert-success')
        return redirect(url_for('my_recipes'))
    
    recipe = Recipe.query.filter_by( id = recipe_id ).first()
    if not recipe:
        flash('Rezept nicht gefunden',"alert alert-danger")
        return render_template(url_for('my_recipes'))

    ingredients_list = [ingredient.name for ingredient in recipe.ingredients]

    form.ingredients.data = ",".join(ingredients_list)
    form.preparation.data = recipe.preparation
    title = 'Edit your recipe'
    recipe = Recipe.query.filter_by( id = recipe_id).first()
    recipe_info = recipe.serialize()
    return render_template('edit_recipe.html',recipe_info = recipe_info,title = title,form = form)


#Ansicht zum löschen von Rezepten
@app.route('/delete_recipe/<int:recipe_id>',methods=['GET'])
def remove_recipe(recipe_id):
    
    recipe = Recipe.query.filter_by( id = recipe_id ).first()
    if not recipe:
        flash('Rezept nicht gefunden',"alert alert-danger")
        return render_template(url_for('my_recipes'))
    
    db.session.delete(recipe)
    db.session.commit()
    flash('Rezept wurde erfolgreich gelöscht',"alert alert-success")
    return redirect(url_for('my_recipes'))




# Funktion zur Überprüfung der Passwörter für die Authentifizierung 
@auth.verify_password
def verify_password(username, password):
    user = User.query.filter_by(username = username).first()
    if not user or not user.check_password(password):
        return False
    g.user = user
    return True







#Definierung der API Methoden
#API neuer User erstellen (POST)
@app.route('/api/users', methods = ['POST'])
def new_user():
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        abort(400) # abbruch wenn ein Argument fehlt 
    if User.query.filter_by(username = username).first() is not None:
        abort(400) # abbruch wenn user bereits existiert
    user = User(username = username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify({ 'username': user.username }), 201, {'Location': url_for('get_user', user_id = user.id, _external = True)}



# API alle User abfragen  (GET) 
@app.route('/api/users',methods=['GET'])
def get_users():
    users = User.query.all() # Alle User aus Datenbank auslesen
    return jsonify(users = User.serialize_list(users))

# API spezifischer User per ID abfragen (GET) 
@app.route('/api/users/<int:user_id>',methods=['GET'])
def get_user(user_id):
    user = User.query.filter_by( id = user_id).first() # Nach Benutzer anhand ID suchen
    if user:
        return jsonify(user.serialize())
    return { 'message' : 'There is no user with this id '},404 # Fehlermeldung wenn UserID nicht existiert


# API Alle Rezepte von allen Usern anzeigen (GET)
@app.route('/api/recipes',methods=['GET'])
def get_recipes():
    recipes = Recipe.query.all() # Alle Rezepte aus Datenbank auslesen
    return jsonify(recipes = Recipe.serialize_list(recipes))

# API spezifisches Rezept aus Datenbank auslesen (GET)
@app.route('/api/recipes/<int:recipe_id>',methods=['GET'])
def get_recipe(recipe_id):
    recipe = Recipe.query.filter_by( id = recipe_id).first()
    if recipe:   
        return jsonify(recipe.serialize())
    return { 'message' : 'There is no recipe with this id'}

# API Alle Rezepte eines User anzeigen (GET)
@app.route('/api/users/<int:user_id>/recipes',methods=['GET'])
def get_user_recipes(user_id):
    if not User.query.filter_by( id = user_id).first():
        return { 'message' : 'There is no user with this id'},404
    
    recipes = Recipe.query.filter_by( user_id = user_id).all()
    return jsonify(recipes = Recipe.serialize_list(recipes))
    

# API Rezept einem spezifischen User hinzufügen (POST)
@app.route('/api/users/<int:user_id>/recipes',methods=['POST'])
@auth.login_required
def add_recipe(user_id):
    user = User.query.filter_by( id = user_id).first()
    if not user:
        return { 'message' : 'There is no user with this id'},404 # Fehlermeldung wenn user nicht existiert
    if g.user != user:
        return { 'message' : 'You are not authorized to make this action'},403 # Fehlermeldung wenn nicht als spezifischer User angemeldet
    title = request.json.get('title')
    preparation = request.json.get('preparation')
    ingredients = request.json.get('ingredients')
    
    new_recipe = Recipe( title = title , preparation = preparation , author = user)
    
    #add ingredients
    for ingredient in ingredients:
        new_ingredient = Ingredient( name = ingredient['name'] , recipe = new_recipe)
        new_recipe.ingredients.append(new_ingredient)

    db.session.add(new_recipe)
    db.session.commit()

    return { ' message' : 'New Recipe created successfully'},201

    
# API löschen eines Rezepts von einem spezifischen User (DELETE)
@app.route('/api/users/<int:user_id>/recipes/<int:recipe_id>',methods=['DELETE']) 
@auth.login_required
def delete_recipe(user_id,recipe_id):
    user = User.query.filter_by( id = user_id).first()
    if not user:
        return { 'message' : 'There is no user with this id'},404 # Fehlermeldung wenn user nicht existiert
    if g.user != user:
        return { 'message' : 'You are not authorized to make this action'},403 # Fehlermeldung wenn nicht als spezifischer User angemeldet
    recipe = Recipe.query.filter_by( id = recipe_id).first()
    if not recipe:
        return { 'message' : 'There is no recipe with this id'},404 # Fehlermeldung wenn rezept nicht existiert
    db.session.delete(recipe)
    db.session.commit()

    return { 'message' : 'Recipe was successfully deleted' },204   
    

# API Editieren eines spezifischen Rezeptes eines spezifischen Users (PUT)
@app.route('/api/users/<int:user_id>/recipes/<int:recipe_id>',methods = ['PUT'])
@auth.login_required
def update_recipe(user_id,recipe_id):
    user = User.query.filter_by( id = user_id ).first()
    if not user:
        return { 'message' : 'There is no user with this id'},404 # Fehlermeldung wenn user nicht existiert
    if g.user != user:
        return { ' message' : "You are not authorized to make this action "},403 # Fehlermeldung wenn nicht als spezifischer User angemeldet
    recipe = Recipe.query.filter_by( id = recipe_id).first()
    if not recipe:
        return { 'message ' : 'There is no recipe with this id'},404 # Fehlermeldung wenn rezept nicht existiert


    title = request.json.get('title')
    preparation = request.json.get('preparation')
    ingredients = request.json.get('ingredients')

    recipe.title = title
    recipe.preparation = preparation
    # löschen der geänderten Zutaten  
    for ingredient in recipe.ingredients:
        db.session.delete(ingredient)
    # Hinzufügen der neuer/geänderten Zutaten 
    for ingredient in ingredients:
        ingredient = Ingredient( name = ingredient['name'] , recipe = recipe )
        recipe.ingredients.append(ingredient)

    db.session.commit()
    return { 'message' : 'The recipe has been updated successfully'},200 # Meldung wenn Rezept erfolreich Editiert wurde


