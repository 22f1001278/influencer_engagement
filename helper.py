from flask import session, redirect, url_for, flash
from model import User
from functools import wraps


def getUserInfo():
    if 'id' in session:
        current_user = User.query.filter_by(id = session['id']).first()
        if current_user:
            usr_id = current_user.id
            email = current_user.email
            isAdmin = current_user.isAdmin
            isInfluencer = current_user.isInfluencer
            isSponsor = current_user.isSponsor
            return {'usr_id':usr_id, 'email':email, 'isAdmin':isAdmin, 'isInfluencer':isInfluencer, 'isSponsor':isSponsor}
        else:
            return None
        

def influencerNeeded():
    def wrapper(f):
        @wraps(f)
        def decorator(*args, **kwargs):
            user = getUserInfo()
            if user is None or 'isInfluencer' not in user or user['isInfluencer'] != 1:
                flash('Influencer only','danger')
                return redirect(url_for('logout'))
            return f(*args, **kwargs) 
        return decorator
    return wrapper

def sponsorNeeded():
    def wrapper(f):
        @wraps(f)
        def decorator(*args, **kwargs):
            user = getUserInfo()
            if not user['isSponsor']:
                flash('Sponsor only','danger')
                return redirect(url_for('logout'))
        return decorator
    return wrapper


def adminNeeded():
    def wrapper(f):
        @wraps(f)
        def decorator(*args, **kwargs):
            user = getUserInfo()
            if user['isAdmin'] != 1:
                flash('Admin only','danger')
                return redirect(url_for('logout'))
        return decorator
    return wrapper