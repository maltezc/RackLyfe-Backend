"""Routes for addresses blueprint."""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.exceptions import NotFound, abort

from mnb_backend.database import db

from mnb_backend.addresses.route_helpers import set_retrieve_address
from mnb_backend.addresses.models import Address
from mnb_backend.users.models import User

addresses_routes = Blueprint('addresses_routes', __name__)


# region Address Endpoints Start

@addresses_routes.post("/api/address")
@jwt_required()
def create_address():
    """ Adds address to the currently logged-in user
    Returns JSON like:
        {address: {address_uid, street, city, state, zipcode}}
    """

    current_user = get_jwt_identity()
    user = User.query.get_or_404(current_user)
    data = request.json

    # TODO: SET UP SCHEMA VALIDATOR
    address_in = data['address']
    city_in = data['city']
    state_in = data['state']
    zipcode_in = data['zipcode']
    user, address, city, state, zipcode, address_string = set_retrieve_address(user, address_in, city_in,
                                                                               state_in, zipcode_in)
    # TODO: VALIDATE ADDRESS USING GOOLGE MAPS OR SIM API

    return jsonify(
        user=user.serialize(),
        address=address.serialize(),
        state=state.serialize(),
        city=city.serialize(),
        zipcode=zipcode.serialize(),
    ), 201


@addresses_routes.get("/api/address/<int:address_id>")
def get_address(address_id):
    """ Returns JSON like:
        {address: {address_uid, street, city, state, zipcode}}
    """

    try:
        address = Address.query.get_or_404(address_id)
        return jsonify(address=address.serialize()), 200

    except NotFound:
        abort(404)

    except Exception as error:
        abort(500)


@addresses_routes.patch("/api/address/<int:address_id>")
@jwt_required()
def update_address(address_id):
    """ Returns JSON like:
        {address: {address_uid, street, city, state, zipcode}}
    """

    current_user = get_jwt_identity()
    user = User.query.get_or_404(current_user)
    address = Address.query.get_or_404(address_id)
    # TODO: IF DB IS RESEEDED, AND MOTIONS ARE DONE, USERID IS THE SAME.
    if user.id == address.user.id or user.is_admin:

        if address.location is not None:
            try:
                db.session.delete(address.location)
                db.session.delete(address)  # @Lucas: Should I be deleting the address here or should i just be changing it?
                db.session.commit()
            except Exception as error:
                abort(500, description="Failed to update address")

        address_in = request.json['address']
        city_in = request.json['city']
        state_in = request.json['state']
        zipcode_in = request.json['zipcode']
        user, address, city, state, zipcode, address_string = set_retrieve_address(user, address_in, city_in, state_in,
                                                                                   zipcode_in)

        # TODO: FE - control this on front end and have user use a drop down of selectable options only

        return jsonify(
            user=user.serialize(),
            state=state.serialize(),
            city=city.serialize(),
            zipcode=zipcode.serialize(),
        ), 200

    abort(500, description="Failed to update address")


@addresses_routes.delete("/api/address/<int:address_id>")
@jwt_required()
def delete_address(address_id):
    """ Returns JSON like:
        {address: {address_uid, street, city, state, zipcode}}
    """

    try:
        current_user = get_jwt_identity()
        user = User.query.get_or_404(current_user)
        address = Address.query.get_or_404(address_id)

        if user.id == address.user.id:
            db.session.delete(address)
            db.session.commit()

            return jsonify(user=user.serialize()), 200
        abort(401, description="Not authorized")

    except Exception as error:
        abort(500, description="Failed to delete address")

# endregion
