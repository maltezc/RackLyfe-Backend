from models import User
from flask import abort
from flask_jwt_extended import get_jwt_identity
from functools import wraps


def admin_required(f):
    """
    Decorator to ensure user is admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        """
        Wrapper function to ensure user is admin"""

        current_user_id = get_jwt_identity()

        # user_id = g.user_id  # assuming g.user_id is the user ID of the logged-in user
        user = User.query.get(current_user_id)
        if not user or not user.is_admin:
            abort(403)  # raise a 403 Forbidden error if the user is not an admin
        return f(*args, **kwargs)

    return decorated_function

# def admin_login_required():
#     """
#     Decorator to ensure user is admin"""
#
#     def wrap(*args, **kwargs):
#         """
#         Wrapper function to ensure user is admin"""
#         # user is available from @login_required
#
#         current_user = get_jwt_identity()
#         user = User.query.get_or_404(current_user)
#
#         if not user.is_admin:
#             return "you need to be admin", 401
#         return f(*args, **kwargs)

        # if not g.user.is_admin:
        #     return "you need to be admin", 401
        # return f(*args, **kwargs)
