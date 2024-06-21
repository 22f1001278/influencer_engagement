## imports
from flask import Flask, render_template, url_for, request, redirect, flash
from datetime import timedelta
from model import db, User


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


user_type = {'user1': '', 'user2':'Influencer', 'user3':'Sponsor'}

@app.route("/")
def index():
    current_user = 'user1'
    return render_template('index.html', nav_type = user_type[current_user])


@app.route("/registration",methods = ['GET','POST'])
def registration():
    if request.method == 'GET':
        current_user = 'user1'
        return render_template('registration.html', nav_type = user_type[current_user])
    
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

        flash("Registration Successful. Please Login to continue!",'success')
        return redirect(url_for('registration'))  ## returning the same page temporarily 
    

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        current_user = 'user1'
        return render_template('index.html', nav_type = user_type[current_user])
    elif request.method == 'GET':
        current_user = 'user1'
        return render_template('index.html', nav_type = user_type[current_user])

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    return render_template('index.html')




if __name__ == "__main__": 
    app.run(host='0.0.0.0',debug =True)