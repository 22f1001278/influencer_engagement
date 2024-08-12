## implement orm
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

## lets define the tables

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String, unique = False, nullable = True, default=lambda: '')
    email = db.Column(db.String, unique = True, nullable = False)
    password = db.Column(db.String, nullable = False) 
    isAdmin = db.Column(db.Boolean, default = False)
    isInfluencer = db.Column(db.Boolean, default = False)
    isSponsor = db.Column(db.Boolean, default = False)
    isBlacklist = db.Column(db.Boolean, default = False)
    # isFlag = db.Column(db.Boolean, default = False)
    # influencer_id = db.Column(db.Integer, db.ForeignKey('influencer.id'), nullable=True)

    influencer = db.relationship('Influencer', back_populates='user', cascade="all, delete-orphan", uselist=False)
    sponsor = db.relationship('Sponsor', back_populates='user', cascade="all, delete-orphan", uselist=False)


class Influencer(db.Model):
    influencer_id = db.Column(db.Integer, db.ForeignKey('user.id'),primary_key=True)
    ## one to one relationship with user table   
    category = db.Column(db.String, nullable=True, default = '')
    rating = db.Column(db.Float, default=50.0)
    
    user = db.relationship('User', back_populates='influencer')
    requests = db.relationship('Request', back_populates='influencer', cascade="all, delete-orphan")
    blacklist_requests = db.relationship('BlacklistRequest', back_populates='influencer', cascade="all, delete-orphan")


class Sponsor(db.Model):
    sponsor_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    industry = db.Column(db.String, nullable=True)
    
    user = db.relationship('User', back_populates='sponsor')
    campaigns = db.relationship('Campaign', back_populates='sponsor', cascade="all, delete-orphan")
    blacklist_requests = db.relationship('BlacklistRequest', back_populates='sponsor', cascade="all, delete-orphan")



class Campaign(db.Model):
    campaign_id = db.Column(db.Integer, primary_key=True)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('sponsor.sponsor_id'), nullable=False)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.Text, nullable=False)
    budget = db.Column(db.Numeric(10, 2), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String, nullable=False)
    niche = db.Column(db.String, nullable=False)
    isBlacklist = db.Column(db.Boolean, default=False)

    sponsor = db.relationship('Sponsor', back_populates='campaigns')
    requests = db.relationship('Request', back_populates='campaign', cascade="all, delete-orphan")



class Request(db.Model):
    request_id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.campaign_id'), nullable=False)
    influencer_id = db.Column(db.Integer, db.ForeignKey('influencer.influencer_id'), nullable=False)
    initiated_by_influencer = db.Column(db.Boolean, nullable=False)
    influencer_approved = db.Column(db.Boolean, nullable=True)  
    sponsor_approved = db.Column(db.Boolean, nullable=True)  
    status = db.Column(db.String, nullable=False, default='Pending')  

    campaign = db.relationship('Campaign', back_populates='requests')
    influencer = db.relationship('Influencer', back_populates='requests')
    __table_args__ = (db.UniqueConstraint('campaign_id', 'influencer_id', name='unique_camp_inf_req'),)


class BlacklistRequest(db.Model):
    request_id = db.Column(db.Integer, primary_key=True)
    influencer_id = db.Column(db.Integer, db.ForeignKey('influencer.influencer_id'), nullable=False)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('sponsor.sponsor_id'), nullable=False)
    approved = db.Column(db.Boolean, default=None) 
    
    influencer = db.relationship('Influencer', back_populates='blacklist_requests')
    sponsor = db.relationship('Sponsor', back_populates='blacklist_requests')



## references
 #https://stackoverflow.com/questions/10059345/sqlalchemy-unique-across-multiple-columns