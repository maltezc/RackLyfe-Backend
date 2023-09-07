from flask import Blueprint, jsonify

error_handlers_bp = Blueprint('error_handlers', __name__)


# can get description of abort.description property with: error.description.
# abort(403, description="You do not have permission to perform this action.") <- used in routes typically
# ex: return jsonify(error=error.description), 403

def basic_error_handler(default_message, description, status_code):
    """Basic error handler"""

    message = description or default_message
    return jsonify(error=message), status_code


@error_handlers_bp.app_errorhandler(400)
def handle_400(error):
    """
    Error handler for 400 errors"""

    return basic_error_handler("Bad Request", error.description, 400)
    # if error.description:
    #     return jsonify(error=f"Bad Request. {error.description}"), 400
    # return jsonify(error="Bad Request."), 400


@error_handlers_bp.app_errorhandler(401)
def handle_401(error):
    """
    Error handler for 401 errors"""
    return basic_error_handler("Not Authorized", error.description, 401)
    # return jsonify(error="Not Authorized"), 401


@error_handlers_bp.app_errorhandler(403)
def handle_403(error):
    """
    Error handler for 403 errors"""
    return basic_error_handler("Forbidden", error.description, 403)
    # return jsonify(error="Forbidden"), 403


@error_handlers_bp.app_errorhandler(404)
def handle_404(error):
    """
    Error handler for 404 errors"""
    return basic_error_handler("Not found", error.description, 404)
    # return jsonify(error="Not found"), 404


@error_handlers_bp.app_errorhandler(409)
def handle_409(error):
    """
    Error handler for 409 errors"""
    return basic_error_handler("Conflict", error.description, 409)
    # return jsonify(error="Not found"), 404


@error_handlers_bp.app_errorhandler(500)
def handle_500(error):
    """
    Error handler for 500 errors"""
    return basic_error_handler("Internal server error", error.description, 500)
    # return jsonify(error="Internal server error"), 500

# add other error handlers as needed
