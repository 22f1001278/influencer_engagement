from flask import session, redirect, url_for
from model import User
from functools import wraps


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
    


# def user_needed(f):
#     @wraps(f) ## changes the name of the function returned to the name of the function passed
#     def decorated_function(*args, **kwargs):
#         user = getUserInfo()
#         if user['role'] not in ['isInfluencer', 'isSponsor', 'isAdmin']:
#             flash('user only','danger')
#             return redirect(url_for('logout'))
#         return f(*args, **kwargs)
#     return decorated_function