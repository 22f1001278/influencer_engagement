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
            isBlacklist = current_user.isBlacklist
            return {'usr_id':usr_id, 'email':email, 'isAdmin':isAdmin, 'isInfluencer':isInfluencer, 'isSponsor':isSponsor,'isBlacklist':isBlacklist}
        else:
            return None
        

