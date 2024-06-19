## imports
from flask import Flask, render_template, url_for, request, redirect
from model import db, User


## object of flask
app = Flask(__name__)

## database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ief_db.sqlite3'
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
        return render_template('registration.html')
    
    if request.method == 'POST':
        email = request.form.get('email') 
        password = request.form.get('password')

        user1 = User(email = email, password=password)
        db.session.add(user1)
        db.session.commit()
        return redirect(url_for('login'))
    

@app.route("/login")
def login():
    current_user = 'user1'
    return render_template('login.html', nav_type = user_type[current_user])



if __name__ == "__main__": 
    app.run(host='0.0.0.0',debug =True)