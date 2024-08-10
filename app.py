## imports
from flask import Flask, render_template, url_for, request, redirect, flash, session
from datetime import timedelta
from model import db, User, Influencer, Campaign
from helper import getUserInfo, influencerNeeded, sponsorNeeded
from datetime import datetime

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
    
    if current_user is None:
        return redirect(url_for('index_page'))
    else:
        ## not able to pass dictionary directly
        return redirect(url_for('home_page', user_email=current_user['email'], 
                                             isAdmin=current_user['isAdmin'], 
                                             isInfluencer=current_user['isInfluencer'], 
                                             isSponsor=current_user['isSponsor'],
                                             usr_id = current_user['usr_id']))

@app.route("/index")
def index_page():
    return render_template('index.html', nav_type=None)  # Render index.html without nav_type if no user

@app.route("/home")
def home_page():
    user_email = request.args.get('user_email')
    isAdmin = request.args.get('isAdmin')
    isInfluencer = request.args.get('isInfluencer')
    isSponsor = request.args.get('isSponsor')
    user_id = request.args.get('usr_id')

    nav_type = {
        'email': user_email,
        'isAdmin': int(isAdmin.lower() == 'true'),  # Convert string to boolean
        'isInfluencer': int(isInfluencer.lower() == 'true'),
        'isSponsor': int(isSponsor.lower() == 'true'),
        'id': user_id
    }
    return render_template('home.html', nav_type=nav_type)  # Render home.html with nav_type as current_user


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
def profile():
    user = getUserInfo()
    ## check the authorization
    if 'id' not in session:
        return redirect(url_for('login'))
    
    id = session['id']
    user = User.query.filter_by(id=id).first()
    if user.isInfluencer:
        return render_template('profile.html', nav_type=user)
    elif user.isSponsor:
        return render_template('profile.html', nav_type=user)
    elif user.isAdmin:
        return render_template('profile.html', nav_type=user)
    else:
        # If the user has no recognized role, handle accordingly
        flash("Unauthorized access.", "danger")
        return redirect(url_for('login'))
    

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



@app.route('/campaigns',methods =['GET','POST'])
def campaigns():
    user = getUserInfo()
    ## check the authorization
    if 'id' not in session:
        return redirect(url_for('login'))
    
    id = session['id']
    user = User.query.filter_by(id=id).first()
    if user is None or not user.isSponsor:
        return redirect(url_for('login'))
    
    campaigns = Campaign.query.filter_by(sponsor_id=user.id).all()
    
    return render_template('campaigns.html', nav_type=user, campaigns = campaigns)

@app.route('/viewActiveCampaigns')
def viewActiveCampaigns():
    user = getUserInfo()

    return render_template('activeCampaigns.html', nav_type= None)
    

@app.route('/createCampaign', methods = ['GET','POST'])
def createCampaign():
    user = getUserInfo()

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        budget = request.form.get('budget')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')

        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

        if not title or not description or not budget or not start_date or not end_date:
                flash('All fields are required.', 'danger')
                return redirect(url_for('createCampaign'))

        new_campaign = Campaign(
                sponsor_id=user['usr_id'], 
                title=title,
                description=description,
                budget=budget,
                start_date=start_date,
                end_date=end_date,
                status='Active' ## setting active as default
            )
        
        db.session.add(new_campaign)
        db.session.commit()
        
        flash('Campaign created successfully!', 'success')
        return redirect(url_for('campaigns'))

    return render_template('createCampaign.html', nav_type=user)


@app.route('/campaignManagment/<int:campaign_id>', methods = ['GET', 'POST'])
def campaignManagement(campaign_id):
    user = getUserInfo()
    ## check the authorization
    if 'id' not in session:
        return redirect(url_for('login'))
    
    id = session['id']
    user = User.query.filter_by(id=id).first()

    if user is None or not user.isSponsor:
        return redirect(url_for('login'))
    
    campaign = Campaign.query.filter_by(campaign_id=campaign_id, sponsor_id=user.id).first()

    if not campaign:
        flash("Campaign not found", "danger")
        return redirect(url_for('campaigns'))

    if request.method == 'POST':
        campaign.title = request.form.get('title')
        campaign.description = request.form.get('description')
        campaign.budget = request.form.get('budget')
        campaign.start_date = datetime.strptime(request.form.get('start_date'),'%Y-%m-%d').date()
        campaign.end_date = datetime.strptime(request.form.get('end_date'),'%Y-%m-%d').date()

        db.session.commit()

        flash('Campaign updated successfully!', 'success')
        return redirect(url_for('campaigns'))

    return render_template('campaignManagement.html', campaign=campaign, nav_type = user)

if __name__ == "__main__": 
    app.run(host='0.0.0.0',debug =True)

