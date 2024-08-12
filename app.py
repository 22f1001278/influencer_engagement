## imports
from flask import Flask, render_template, url_for, request, redirect, flash, session
from datetime import timedelta
from model import db, User, Influencer, Campaign, Request, Sponsor, BlacklistRequest
from helper import getUserInfo
from datetime import datetime
import plotly.express as px


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


################### INDEX &&& HOME ROUTES ####################################################

@app.route("/")
# @user_needed ## wrapper not working properly better use the dictionary here
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
    # print(isAdmin)
    nav_type = {
        'email': user_email,
        'isAdmin': int(isAdmin == 'True'),  
        'isInfluencer': int(isInfluencer == 'True'),
        'isSponsor': int(isSponsor == 'True'),
        'id': user_id
    }

    # Getting additional statistics for the admin statistics page
    if nav_type['isAdmin']:
        total_users = User.query.count()
        total_campaigns = Campaign.query.count()
        active_campaigns = Campaign.query.filter_by(status='Active').count()
        flagged_users = User.query.filter_by(isBlacklist=True).count()

        total_influencers = User.query.filter_by(isInfluencer=True).count()
        total_sponsors = User.query.filter_by(isSponsor=True).count()

        fig = px.bar( x=['Influencers', 'Sponsors'], y=[total_influencers, total_sponsors], 
                        labels={'x':'User Type', 'y':'Count'}, title='Influencers vs Sponsors')

        plot_html = fig.to_html(full_html=False)

        return render_template('home.html', nav_type=nav_type, 
                               total_users=total_users, 
                               total_campaigns=total_campaigns, 
                               active_campaigns=active_campaigns, 
                               flagged_users=flagged_users, img_data=plot_html)
    return render_template('home.html', nav_type=nav_type)



#############  REGISTRATION && LOGIN ##########################################################
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
        db.session.flush()
        
        if role == 'influencer':
            inf1 = Influencer(influencer_id=user1.id, category='', rating=50.0)
            db.session.add(inf1)
        elif role == 'sponsor':
            spon1 = Sponsor(sponsor_id=user1.id, industry='')
            db.session.add(spon1)
        
        db.session.commit()
        flash("Registration Successful. Please Login to continue!",'success')
        
        return render_template('registration.html', nav_type = None)
    
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



############################# PROFILE = INFLUENCER &&& SPONSOR #############################################
@app.route('/profile',methods =['GET','POST'])
def profile():
    user = getUserInfo()
    ## Not allowing the blacklisted user
    if user['isBlacklist']:
        flash("You have been blacklisted and cannot access this page.", "danger")
        return redirect(url_for('home_page',user_email=user['email'], 
                            isAdmin=user['isAdmin'], 
                            isInfluencer=user['isInfluencer'], 
                            isSponsor=user['isSponsor'], 
                            usr_id=user['usr_id']))
    
    ## check the authorization
    if 'id' not in session:
        return redirect(url_for('login'))
    
    id = session['id']
    user = User.query.filter_by(id=id).first()
    if user.isInfluencer:
        approved_requests = Request.query.filter_by(
            influencer_id=user.influencer.influencer_id,
            status='Approved'
        ).all()

        active_campaigns = [req.campaign for req in approved_requests]

        new_requests = Request.query.filter_by(influencer_id=user.influencer.influencer_id,
                                                status='Pending',sponsor_approved=True,influencer_approved=None).all()

        # Fetch rejected requests
        rejected_requests = Request.query.filter_by( influencer_id=user.influencer.influencer_id, status='Rejected').all()

        # Fetch pending requests where the sponsor has not yet approved
        pending_requests = Request.query.filter_by(influencer_id=user.influencer.influencer_id,
                                                    status='Pending',
                                                    sponsor_approved=None).all()

        total_earnings = sum(req.campaign.budget for req in approved_requests)

        return render_template('profile.html',  nav_type=user, approved_requests=approved_requests, 
                                                new_requests=new_requests, pending_requests=pending_requests,
                                                rejected_requests=rejected_requests, total_earnings= total_earnings)
                                            
    elif user.isSponsor:
        active_campaigns = Campaign.query.filter_by(sponsor_id=user.sponsor.sponsor_id,
                                                    status='Active').all()

        past_campaigns = Campaign.query.filter_by(sponsor_id=user.sponsor.sponsor_id,
                                                    status='Inactive').all()

        new_requests = Request.query.join(Campaign).filter(Campaign.sponsor_id == user.sponsor.sponsor_id,
                                                            Request.sponsor_approved == None).all()

        pending_requests = Request.query.filter_by(sponsor_approved=True, influencer_approved=None).join(Campaign).filter(
                                                    Campaign.sponsor_id == user.sponsor.sponsor_id).all()

        rejected_requests = Request.query.filter_by(influencer_approved=False).join(Campaign).filter(Campaign.sponsor_id == user.sponsor.sponsor_id).all()
        
        total_spend = sum(campaign.budget for campaign in active_campaigns)
        approved_influencers = {}
        for campaign in active_campaigns:
            approved_influencers[campaign.campaign_id] = Request.query.filter_by(campaign_id=campaign.campaign_id, status='Approved').count()
        return render_template('profile.html',nav_type=user,active_campaigns=active_campaigns,
                                                past_campaigns=past_campaigns,new_requests=new_requests,
                                                pending_requests=pending_requests,rejected_requests=rejected_requests, total_spend=total_spend, 
                                                approved_influencers=approved_influencers)

    elif user.isAdmin:
        return render_template('profile.html', nav_type=user)
    else:
        # If the user has no recognized role, handle accordingly
        flash("Unauthorized access.", "danger")
        return redirect(url_for('login'))
    


############################## Find Camapigns for the influencer #################################################################################
@app.route('/findCampaigns',methods =['GET','POST'])
def findCampaigns():
    user = getUserInfo()

    if user['isBlacklist']:
        flash("You have been blacklisted and cannot access this page.", "danger")
        return redirect(url_for('home_page',user_email=user['email'], 
                                            isAdmin=user['isAdmin'], 
                                            isInfluencer=user['isInfluencer'], 
                                            isSponsor=user['isSponsor'], 
                                            usr_id=user['usr_id']))


    if 'id' not in session:
        return redirect(url_for('login'))
    
    id = session['id']
    user = User.query.filter_by(id=id).first()
    if user is None or not user.isInfluencer:
        flash("You do not have permission to view campaigns.", "danger")
        return redirect(url_for('login'))
    
    activeCampaigns = Campaign.query.filter_by(status='Active').all()
    return render_template('findCampaigns.html', nav_type=user, activeCampaigns = activeCampaigns)


@app.route('/campaignDetails/<int:campaign_id>')
def campaignDetails(campaign_id):
    
    if 'id' not in session:
        return redirect(url_for('login'))
    
    campaign = Campaign.query.get(campaign_id)
    if not campaign:
        flash("Campaign not found.", "danger")
        return redirect(url_for('availableCampaigns'))
    
    approved_influencers = db.session.query(Influencer).join(Request).filter(Request.campaign_id == campaign_id, Request.influencer_approved == True).all()

    total_spend = len(approved_influencers) * float(campaign.budget)

    return render_template('campaignDetails.html', campaign=campaign, approved_influencers=approved_influencers, total_spend= total_spend)



############################## campaigns Sponsor ######################################################################################
@app.route('/campaigns',methods =['GET','POST'])
def campaigns():
    user = getUserInfo()

    if user['isBlacklist']:
        flash("You have been blacklisted and cannot access this page.", "danger")
        return redirect(url_for('home_page',user_email=user['email'], 
                            isAdmin=user['isAdmin'], 
                            isInfluencer=user['isInfluencer'], 
                            isSponsor=user['isSponsor'], 
                            usr_id=user['usr_id']))

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
    
    if user['isBlacklist']:
        flash("You have been blacklisted and cannot access this page.", "danger")
        return redirect(url_for('home_page',user_email=user['email'], 
                            isAdmin=user['isAdmin'], 
                            isInfluencer=user['isInfluencer'], 
                            isSponsor=user['isSponsor'], 
                            usr_id=user['usr_id']))

    return render_template('activeCampaigns.html', nav_type= None)
    

@app.route('/createCampaign', methods = ['GET','POST'])
def createCampaign():
    user = getUserInfo()

    if user['isBlacklist']:
        flash("You have been blacklisted and cannot access this page.", "danger")
        return redirect(url_for('home_page',user_email=user['email'], 
                            isAdmin=user['isAdmin'], 
                            isInfluencer=user['isInfluencer'], 
                            isSponsor=user['isSponsor'], 
                            usr_id=user['usr_id']))

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        budget = request.form.get('budget')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        niche = request.form.get('niche')

        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

        if not title or not description or not budget or not start_date or not end_date:
                flash('All fields are required.', 'danger')
                return redirect(url_for('createCampaign'))

        new_campaign = Campaign(sponsor_id=user['usr_id'], title=title,description=description,
                                budget=budget,start_date=start_date,end_date=end_date,
                                status='Active', #### setting active as default
                                niche= niche)
        
        db.session.add(new_campaign)
        db.session.commit()
        
        flash('Campaign created successfully!', 'success')
        return redirect(url_for('campaigns'))

    return render_template('createCampaign.html', nav_type=user)


@app.route('/deleteCampaign/<int:campaign_id>', methods=['POST'])
def sponsorDeleteCampaign(campaign_id):
    if 'id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['id']
    user = User.query.filter_by(id=user_id).first()

    # Check if the user is a sponsor and owns the campaign
    campaign = Campaign.query.filter_by(campaign_id=campaign_id, sponsor_id=user.sponsor.sponsor_id).first()

    if not campaign:
        flash("You don't have permission to delete this campaign or it doesn't exist.", "danger")
        return redirect(url_for('campaigns'))

    #### Delete the campaign
    db.session.delete(campaign)
    db.session.commit()

    flash("Campaign deleted successfully.", "success")
    return redirect(url_for('campaigns'))


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

        ##### Resolved the inactive campaigns issue
        if campaign.end_date < datetime.today().date():
            campaign.status = 'Inactive'
        else:
            campaign.status = 'Active' 

        db.session.commit()

        flash('Campaign updated successfully!', 'success')
        return redirect(url_for('campaigns'))

    return render_template('campaignManagement.html', campaign=campaign, nav_type = user)



@app.route('/createRequest/<int:campaign_id>', methods = ['GET','POST'])
def createRequest(campaign_id):
    if 'id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['id']
    user = User.query.filter_by(id = user_id).first()

    if user is None or (not user.isSponsor and not user.isInfluencer):
        flash("None Type, You dont have permission here", "danger")
        return redirect(url_for('login'))
    
    campaign = Campaign.query.filter_by(campaign_id=campaign_id).first()
    # print(campaign)
    if not campaign:
        flash("Campaign not found ", "danger")
        if user.isInfluencer:
            return redirect(url_for('findCampaigns'))
        else:
            return redirect(url_for('campaigns'))
    
    print(user.isInfluencer)
    if user.isInfluencer:
        existing_request = Request.query.filter_by(campaign_id=campaign_id, influencer_id=user.influencer.influencer_id).first()
        if existing_request:
            flash("You have already requested participation in this campaign.", "danger")
            return redirect(url_for('findCampaigns'))
        # print('outsidePost')
        if request.method == 'GET':
            print('insidePost')
            new_request = Request(campaign_id=campaign_id, influencer_id=user.influencer.influencer_id, initiated_by_influencer=True,
                                    influencer_approved = True, status='Pending')
            db.session.add(new_request)
            db.session.commit()

            flash("Request to join the campaign created successfully!", "success")
            return redirect(url_for('findCampaigns'))

    elif user.isSponsor:
        available_influencers = Influencer.query.all()
        requested_influencers = [r.influencer for r in Request.query.filter_by(campaign_id=campaign_id).all()]

        if request.method == 'POST':
            influencer_id = request.form.get('influencer_id')
            existing_request = Request.query.filter_by(campaign_id=campaign_id, influencer_id=influencer_id).first()
            if existing_request:
                flash("You have already requested this influencer for this campaign.", "danger")
                return redirect(url_for('createRequest', campaign_id=campaign_id))

            new_request = Request(campaign_id=campaign_id, influencer_id=influencer_id, initiated_by_influencer=False,
                                    sponsor_approved = True,status='Pending')
            db.session.add(new_request)
            db.session.commit()

            flash("Request for the influencer created successfully!", "success")
            return redirect(url_for('createRequest', campaign_id=campaign_id))
        
        return render_template('createRequest.html', campaign=campaign, influencers=available_influencers, nav_type=user, requested_influencers=requested_influencers)

    
    flash("Invalid action.", "danger")
    return redirect(url_for('campaigns'))

@app.route('/approveRequest/<int:request_id>', methods=['POST'])
def approveRequest(request_id):
    user = getUserInfo()
    
    if 'id' not in session:
        return redirect(url_for('login'))
    
    request = Request.query.get(request_id)
    
    if not request:
        flash("Request not found.", "danger")
        return redirect(url_for('home_page'))

    if user['isSponsor'] and request.campaign.sponsor_id == user['usr_id']:
        request.sponsor_approved = True
    elif user['isInfluencer'] and request.influencer_id == user['usr_id']:
        request.influencer_approved = True
    else:
        flash("You do not have permission to approve this request.", "danger")
        return redirect(url_for('home_page'))

    # Update request status based on approvals
    if request.sponsor_approved and request.influencer_approved:
        request.status = 'Approved'
    elif request.sponsor_approved is False or request.influencer_approved is False:
        request.status = 'Rejected'

    db.session.commit()
    flash("Request approved successfully!", "success")
    return redirect(url_for('profile'))

@app.route('/rejectRequest/<int:request_id>', methods=['POST'])
def rejectRequest(request_id):
    user = getUserInfo()
    
    if 'id' not in session:
        return redirect(url_for('login'))
    request = Request.query.get(request_id)
    
    if not request:
        flash("Request not found.", "danger")
        return redirect(url_for('home_page'))

    if user['isSponsor'] and request.campaign.sponsor_id == user['usr_id']:
        request.sponsor_approved = False
    elif user['isInfluencer'] and request.influencer_id == user['usr_id']:
        request.influencer_approved = False
    else:
        flash("You do not have permission to reject this request.", "danger")
        return redirect(url_for('home_page'))

    # Update request status based on rejections
    request.status = 'Rejected'
    db.session.commit()

    flash("Request rejected successfully.", "success")
    return redirect(url_for('profile'))

@app.route('/findInfluencer', methods=['GET', 'POST'])
def findInfluencer():
    user = getUserInfo()
    if user['isBlacklist']:
        flash("You have been blacklisted and cannot access this page.", "danger")
        return redirect(url_for('home_page',user_email=user['email'], isAdmin=user['isAdmin'], 
                                                                    isInfluencer=user['isInfluencer'], 
                                                                    isSponsor=user['isSponsor'], usr_id=user['usr_id']))

    if 'id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.filter_by(id=session['id']).first()

    if user is None or not user.isSponsor:
        flash("You do not have permission to access this page.", "danger")
        return redirect(url_for('home_page'))
    
    influencers = Influencer.query.all()
    return render_template('findInfluencer.html', influencers=influencers, nav_type=user)

###################### requestBlacklist Functionality Pending #####################################################
@app.route('/requestBlacklist/<int:influencer_id>', methods=['POST'])
def requestBlacklist(influencer_id):
    if 'id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.filter_by(id=session['id']).first()

    if user is None or not user.isSponsor:
        flash("You do not have permission to perform this action.", "danger")
        return redirect(url_for('home_page'))

    influencer = Influencer.query.filter_by(influencer_id=influencer_id).first()

    if not influencer:
        flash("Influencer not found.", "danger")
        return redirect(url_for('findInfluencers'))

    # Create a request for the admin to approve
    new_request = BlacklistRequest(influencer_id=influencer_id, sponsor_id=user.id)
    db.session.add(new_request)
    db.session.commit()

    flash("Blacklist request sent successfully!", "success")
    return redirect(url_for('findInfluencer'))


############################################## ADMIN ##########################################################
@app.route('/admin/manageUsers', methods=['GET', 'POST'])
def adminManageUsers():
    if 'id' not in session:
        return redirect(url_for('login'))

    user = User.query.filter_by(id=session['id']).first()

    if user is None or not user.isAdmin:
        flash("You do not have permission to access this page.", "danger")
        return redirect(url_for('home_page'))

    users = User.query.all()
    return render_template('adminManageUsers.html', users=users, nav_type=user)


@app.route('/admin/blacklistUser/<int:user_id>', methods=['POST'])
def blacklistUser(user_id):
    if 'id' not in session:
        return redirect(url_for('login'))

    user = User.query.filter_by(id=session['id']).first()

    if user is None or not user.isAdmin:
        flash("You do not have permission to perform this action.", "danger")
        return redirect(url_for('home_page'))

    user_to_blacklist = User.query.filter_by(id=user_id).first()

    if user_to_blacklist:
        user_to_blacklist.isBlacklist = True
        db.session.commit()
        flash("User has been blacklisted.", "success")
    else:
        flash("User not found.", "danger")

    return redirect(url_for('adminManageUsers'))


@app.route('/admin/deleteUser/<int:user_id>', methods=['POST'])
def deleteUser(user_id):
    if 'id' not in session:
        return redirect(url_for('login'))

    user = User.query.filter_by(id=session['id']).first()

    if user is None or not user.isAdmin:
        flash("You do not have permission to perform this action.", "danger")
        return redirect(url_for('home_page'))

    user_to_delete = User.query.filter_by(id=user_id).first()

    if user_to_delete:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash("User has been deleted.", "success")
    else:
        flash("User not found.", "danger")

    return redirect(url_for('adminManageUsers'))

@app.route('/admin/manageCampaigns', methods=['GET', 'POST'])
def adminManageCampaigns():
    if 'id' not in session:
        return redirect(url_for('login'))

    user = User.query.filter_by(id=session['id']).first()

    if user is None or not user.isAdmin:
        flash("You do not have permission to access this page.", "danger")
        return redirect(url_for('home_page'))

    campaigns = Campaign.query.all()
    return render_template('adminManageCampaigns.html', campaigns=campaigns, nav_type=user)


@app.route('/admin/deleteCampaign/<int:campaign_id>', methods=['POST'])
def adminDeleteCampaign(campaign_id):
    if 'id' not in session:
        return redirect(url_for('login'))

    user = User.query.filter_by(id=session['id']).first()

    if user is None or not user.isAdmin:
        flash("You do not have permission to perform this action.", "danger")
        return redirect(url_for('home_page'))

    campaign_to_delete = Campaign.query.filter_by(campaign_id=campaign_id).first()

    if campaign_to_delete:
        db.session.delete(campaign_to_delete)
        db.session.commit()
        flash("Campaign has been deleted.", "success")
    else:
        flash("Campaign not found.", "danger")

    return redirect(url_for('adminManageCampaigns'))


@app.route('/admin/deactivateCampaign/<int:campaign_id>', methods=['POST'])
def deactivateCampaign(campaign_id):
    if 'id' not in session:
        return redirect(url_for('login'))

    user = User.query.filter_by(id=session['id']).first()

    if user is None or not user.isAdmin:
        flash("You do not have permission to perform this action.", "danger")
        return redirect(url_for('home_page'))

    campaign_to_deactivate = Campaign.query.filter_by(campaign_id=campaign_id).first()

    if campaign_to_deactivate:
        campaign_to_deactivate.status = 'Inactive'
        db.session.commit()
        flash("Campaign has been deactivated.", "success")
    else:
        flash("Campaign not found.", "danger")

    return redirect(url_for('adminManageCampaigns'))

## whitelist functionality added done- working
@app.route('/admin/whiteListUser/<int:user_id>', methods=['POST'])
def whiteListUser(user_id):
    if 'id' not in session:
        return redirect(url_for('login'))

    user = User.query.filter_by(id=session['id']).first()

    if user is None or not user.isAdmin:
        flash("You do not have permission to perform this action.", "danger")
        return redirect(url_for('home_page'))

    userToWhitelist = User.query.filter_by(id=user_id).first()

    if userToWhitelist:
        userToWhitelist.isBlacklist = False
        db.session.commit()
        flash("User has been WhiteListed.", "success")
    else:
        flash("User not found.", "danger")
    return redirect(url_for('adminManageUsers'))

@app.route('/inactivateCampaign/<int:campaign_id>', methods=['POST'])
def inactivateCampaign(campaign_id):
    if 'id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['id']
    user = User.query.filter_by(id=user_id).first()

    # Check if the user is a sponsor and owns the campaign
    campaign = Campaign.query.filter_by(campaign_id=campaign_id, sponsor_id=user.sponsor.sponsor_id).first()

    if not campaign:
        flash("You don't have permission to inactivate this campaign or it doesn't exist.", "danger")
        return redirect(url_for('campaigns'))

    # Inactivate the campaign
    campaign.status = 'Inactive'
    db.session.commit()

    flash("Campaign inactivated successfully.", "success")
    return redirect(url_for('campaigns'))

##################################### PROFILE EDITS ##################################################################
@app.route('/edit_influencer_profile', methods=['POST'])
def edit_influencer_profile():
    if 'id' not in session:
        return redirect(url_for('login'))

    user_id = session['id']
    user = User.query.filter_by(id=user_id).first()

    if user and user.isInfluencer:
        name = request.form.get('name')
        category = request.form.get('category')

        user.name = name
        user.influencer.category = category
        db.session.commit()

        flash("Profile updated successfully!", "success")
        return redirect(url_for('profile'))
    
    flash("Unauthorized access.", "danger")
    return redirect(url_for('login'))


@app.route('/edit_sponsor_profile', methods=['POST'])
def edit_sponsor_profile():
    if 'id' not in session:
        flash("Please login, you must be logged in", "danger")
        return redirect(url_for('login'))

    user_id = session['id']
    user = User.query.filter_by(id=user_id).first()
    print(user)
    if user and user.isSponsor:
        name = request.form.get('name')
        industry = request.form.get('industry')
        user.name = name
        user.sponsor.industry = industry
        db.session.commit()

        flash("Profile updated successfully!", "success")
        return redirect(url_for('profile'))
    
    flash("Unauthorized access.", "danger")
    return redirect(url_for('login'))


if __name__ == "__main__": 
    app.run(host='0.0.0.0',debug =True)

