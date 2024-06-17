## imports
from flask import Flask, render_template, url_for

## object of flask
app = Flask(__name__)

user_type = {'user1': 'Admin', 'user2':'Influencer', 'user3':'Sponsor'}

@app.route("/")
def index():
    current_user = 'user3'
    return render_template('index.html', nav_type = user_type[current_user])


@app.route("/login")
def login():
    return render_template('login.html')



if __name__ == "__main__": 
    app.run(host='0.0.0.0',debug =True)