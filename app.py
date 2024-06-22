## imports
from flask import Flask, render_template, url_for, request, redirect, flash, session
from datetime import timedelta
from model import db, User
from helper import getUserInfo


## object of flask
app = Flask(__name__)

## database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ief_db.sqlite3'

## set the secret key
app.config['SECRET_KEY'] = '12345'
app.config['PERMENANT_SESSION_LIFETIME'] = timedelta(minutes=5)

## initialize the app with model
db.init_app(app)             ## connection between app and model
app.app_context().push()      ## enables operation
db.create_all()                ## creates the schema


@app.route("/")
def index():
    current_user = getUserInfo() ## will return email and role
    return render_template('index.html', nav_type = current_user)


@app.route("/registration",methods = ['POST','GET'])
def registration():
    if request.method == 'POST':
        email = request.form.get('email') 
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        
        if not email:
            flash('Please check your email!','danger')
            return redirect(url_for('registration'))
        elif not password1:
            flash('Please enter your password!','danger')
            return redirect(url_for('registration'))
        elif password1 != password2:
            flash('Please check your password!','danger')
            return redirect(url_for('registration'))
        elif User.query.filter_by(email=email).first():
            flash('User already exists','danger')
            return redirect(url_for('registration'))

        user1 = User(email = email, password=password1)
        db.session.add(user1)
        db.session.commit()

        nav_type = ''
        if user1:
            if user1.isAdmin:
                nav_type = 'admin'
            elif user1.isInfluencer:
                nav_type = 'influencer'
            elif user1.isSponsor:
                nav_type = 'sponsor'

        flash("Registration Successful. Please Login to continue!",'success')
        
        return render_template('login.html', nav_type = nav_type)
    
    if request.method == 'GET':
        current_user = getUserInfo()
        return render_template('registration.html', nav_type=current_user)

@app.route('/login', methods=['POST','GET'])
def login():
    if request.method == 'POST':

        ## get the email and password from the form
        email = request.form.get('email') 
        password = request.form.get('password')

        if not email or not password:
            flash("Please provide email and password correctly","danger")
            return redirect(url_for("login"))

        ## check the user email and password are correct
        current_user = User.query.filter_by(email=email).first()

        if (not current_user) or (not current_user.password == password):
            flash("The username and password you entered is incorrect","danger")
            return redirect(url_for("login"))
        elif current_user:
            session['id'] = current_user.id

            nav_type = ''
            if current_user:
                if current_user.isAdmin:
                    role = 'admin'
                elif current_user.isInfluencer:
                    role = 'influencer'
                elif current_user.isSponsor:
                    role = 'sponsor'
            flash("Login Successful! ",'success')
            return render_template('index.html', nav_type = {'role':role, 'email':current_user.email})
    
    ## handling the GET method

    current_user = getUserInfo() ## will return email and role
    return render_template('login.html', nav_type=current_user )

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('id',None)
    flash('Logout Successful','success')
    return redirect(url_for('index'))


if __name__ == "__main__": 
    app.run(host='0.0.0.0',debug =True)