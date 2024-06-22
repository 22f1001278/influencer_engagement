from flask import session
from model import User


def getUserInfo():
    if 'id' in session:
        current_user = User.query.filter_by(id = session['id']).first()
        email = current_user.email
        if current_user:
            if current_user.isAdmin:
                role = 'admin'
            elif current_user.isInfluencer:
                role = 'influencer'
            elif current_user.isSponsor:
                role = 'sponsor'
        return {'email':email, 'role':role}
    
    else:
        return {'role':''}