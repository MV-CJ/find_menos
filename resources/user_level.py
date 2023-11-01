from functools import wraps
from models.usuario import UserModel
from flask_jwt_extended import create_access_token, jwt_required, get_jwt, get_jwt_identity

def role_required(*roles):
    def wrapper(fn):
        @wraps(fn)
        def decorated_function(*args, **kwargs):
            current_user_id = get_jwt_identity()
            user = UserModel.find_user(current_user_id)
            
            if user.tipo_usuario in roles:
                return fn(*args, **kwargs)
            else:
                return {'message': 'Unauthorized access for this user type'}, 403
        return decorated_function
    return wrapper
