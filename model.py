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

    def __init__(self, email, password, isInfluencer, isSponsor):
        self.email = email
        self.password = password
        self.isInfluencer = isInfluencer
        self.isSponsor = isSponsor


class Influencer(db.Model):
    influencer_id = db.Column(db.Integer, db.ForeignKey('user.id'),primary_key=True)
    ## one to one relationship with user table   
    category = db.Column(db.String, nullable=True, default = '')
    rating = db.Column(db.Float, default=50.0)
    user = db.relationship('User', backref=db.backref('influencer', uselist=False))

    def __init__(self, category, rating):
        self.category = category
        self.rating = rating


class Sponsor(db.Model):
    sponsor_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    industry = db.Column(db.String, nullable=True)
    user = db.relationship('User', backref=db.backref('sponsor', uselist=False))

    def __init__(self, industry):
        self.industry = industry

class Campaign(db.Model):
    campaign_id = db.Column(db.Integer, primary_key=True)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('sponsor.sponsor_id'), nullable=False)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.Text, nullable=False)
    budget = db.Column(db.Numeric(10, 2), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String, nullable=False)
    sponsor = db.relationship('Sponsor', backref=db.backref('campaigns', lazy=True))

    def __init__(self, sponsor_id, title, description, budget, start_date, end_date, status):
        self.sponsor_id = sponsor_id
        self.title = title
        self.description = description
        self.budget = budget
        self.start_date = start_date
        self.end_date = end_date
        self.status = status


class Request(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.campaign_id'), nullable=False)
    influencer_id = db.Column(db.Integer, db.ForeignKey('influencer.influencer_id'), nullable=False)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.Text, nullable=False)
    budget = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String, nullable=False)
    campaign = db.relationship('Campaign', backref=db.backref('requests', lazy=True))
    influencer = db.relationship('Influencer', backref=db.backref('requests', lazy=True))

    def __init__(self, campaign_id, influencer_id, title, description, budget, status):
        self.campaign_id = campaign_id
        self.influencer_id = influencer_id
        self.title = title
        self.description = description
        self.budget = budget
        self.status = status


influencer_campaign_association = db.Table('influencer_campaign_association',
    db.Column('influencer_id', db.Integer, db.ForeignKey('influencer.influencer_id'), primary_key=True),
    db.Column('campaign_id', db.Integer, db.ForeignKey('campaign.campaign_id'), primary_key=True)
)

 