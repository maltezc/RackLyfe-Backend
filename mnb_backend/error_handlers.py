from flask import Blueprint, jsonify

error_handlers_bp = Blueprint('error_handlers', __name__)


@error_handlers_bp.app_errorhandler(401)
def handle_401(error):
    """
    Error handler for 401 errors"""
    return jsonify(error="Not Authorized"), 401


@error_handlers_bp.app_errorhandler(403)
def handle_403(error):
    """
    Error handler for 403 errors"""
    return jsonify(error="Not Authorized"), 403


@error_handlers_bp.app_errorhandler(404)
def handle_404(error):
    """
    Error handler for 404 errors"""
    return jsonify(error="Not found"), 404


@error_handlers_bp.app_errorhandler(500)
def handle_500(error):
    """
    Error handler for 500 errors"""
    return jsonify(error="Internal server error"), 500

# add other error handlers as needed
