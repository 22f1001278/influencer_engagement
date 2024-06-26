## imports
from flask import Flask, render_template, url_for, request, redirect, flash, session
from datetime import timedelta
from model import db, User
from helper import getUserInfo, influencerNeeded


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
# @user_needed
def index():
    current_user = getUserInfo() ## will return email and role
    return render_template('index.html', nav_type = current_user)


@app.route("/registration",methods = ['POST','GET'])
def registration():
    if request.method == 'POST':
        email = request.form.get('email') 
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        role = request.form.get('role')
        
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
        elif not role:
            flash('Role is required', 'danger')
            return redirect(url_for('registration'))
        elif User.query.filter_by(email=email).first():
            flash('User already exists', 'danger')
            return redirect(url_for('registration'))
        
        if role == 'influencer':
            user1 = User(email=email, password=password1, isInfluencer=1, isSponsor=0)
        elif role == 'sponsor':
            user1 = User(email=email, password=password1, isInfluencer=0, isSponsor=1)

        db.session.add(user1)
        db.session.commit()
        flash("Registration Successful. Please Login to continue!",'success')
        
        return render_template('registration.html', nav_type = user1)
    
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

            flash("Login Successful! ",'success')
            return render_template('index.html', nav_type = current_user)
    
    ## handling the GET method

    current_user = getUserInfo() ## will return email and role
    return render_template('login.html', nav_type=current_user )

@app.route('/logout', methods=['POST','GET'])
def logout():
    session.pop('id',None)
    flash('Logout Successful','success')
    return redirect(url_for('login'))


@app.route('/profile',methods =['GET','POST'])
@influencerNeeded()
def profile():
    user = getUserInfo()
    ## check the authorization
    if 'id' not in session:
        return redirect(url_for('login'))
    
    id = session['id']
    user = User.query.filter_by(id=id).first()
    if user is None or not user.isInfluencer:
        return redirect(url_for('login'))
    
    return render_template('profile.html', nav_type=user)

@app.route('/findSponsor',methods =['GET','POST'])
@influencerNeeded()
def findSponsor():
    user = getUserInfo()
    ## check the authorization
    if 'id' not in session:
        return redirect(url_for('login'))
    
    id = session['id']
    user = User.query.filter_by(id=id).first()
    if user is None or not user.isInfluencer:
        return redirect(url_for('login'))
    
    return render_template('findSponsor.html', nav_type=user)

if __name__ == "__main__": 
    app.run(host='0.0.0.0',debug =True)