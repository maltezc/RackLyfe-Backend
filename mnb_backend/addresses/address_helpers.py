from mnb_backend.database import db
from mnb_backend.enums import StatesEnum
from mnb_backend.addresses.models import State, City, ZipCode, Address, Location

import random
from geopy.distance import geodesic

from mnb_backend.util_filters import geocode_address


# region geofuzzer
def fuzz_coordinates(y, x):
    """
    Fuzzes the coordinates of the location point by a random amount within a specified radius."""

    # Calculate a random angle and distance within the specified radius
    distance_in_meters = 200
    random_angle = random.uniform(0, 360)  # Random angle in degrees
    random_distance = random.uniform(0, distance_in_meters)

    # Calculate the destination point based on angle and distance using geodesic
    new_point = geodesic(kilometers=random_distance / 1000).destination((y, x), random_angle)

    return new_point.longitude, new_point.latitude


# endregion

# region address helpers
def retrieve_state(state_str):
    """ Given a state string, return the state object from the db """

    state_abbreviation = StatesEnum[state_str].value
    state_found_id = State.query.filter(State.state_abbreviation == state_abbreviation).first().id
    # USE ENUMS AS MUCH AS POSSIBLE TO CONTROL DATA IS ALWAYS CORRECT.
    state = State.query.get_or_404(state_found_id)

    return state


def set_retrieve_city(city_str, state):
    """ Given a city string, return the city object from the db """

    # TODO: write checker for city to confirm its actually a real city

    # with app.app_context():
    existing_city = City.query.filter(City.city_name == city_str).first()
    if existing_city is not None:
        city = existing_city
        return city
    else:
        try:
            new_city = City(city_name=city_str, state_uid=state.id)
            db.session.add(new_city)
            db.session.commit()
            city = new_city
            return city
        except Exception as error:
            print("Error", error)
            db.session.rollback()

    # return city


def set_retrieve_zipcode(zipcode_str):
    """ Given a zipcode string, return the zipcode object from the db """

    # TODO: write checker for zipcode to confirm its actually a real zipcode
    # with app.app_context():
    zipcode = str(zipcode_str)
    existing_zipcode = ZipCode.query.filter(ZipCode.code == zipcode).first()
    if existing_zipcode is not None:
        zipcode = existing_zipcode
    else:
        try:
            new_zipcode = ZipCode(code=zipcode)
            db.session.add(new_zipcode)
            db.session.commit()
            zipcode = new_zipcode
        except Exception as error:
            print("Error", error)
            db.session.rollback()
    return zipcode


def set_retrieve_address(user, address_str, city_str, state_str, zipcode_str):
    """ Given an address string, return the address object from the db """

    # TODO: write checker for address to confirm its actually a real address

    state = retrieve_state(state_str)
    city = set_retrieve_city(city_str, state)
    zipcode = set_retrieve_zipcode(zipcode_str)

    try:
        address = Address(
            street_address=address_str,
            city_uid=city.id,
            zipcode_uid=zipcode.id
        )
        user.address = address

        db.session.add(address)
        db.session.commit()
    except Exception as error:
        print("Error", error)
        db.session.rollback()
        raise error

        # EXCEPT

    address_string = f"{address.street_address} {city.city_name}, {state.state_abbreviation} {zipcode.code}"
    set_retrieve_location(address, address_string)

    return user, address, city, state, zipcode, address_string


def set_retrieve_location(address, full_address_str):
    """ Given a location string, return the location object from the db """

    # with app.app_context():
    geocoded_address = geocode_address(full_address_str)
    try:
        location = Location(point=f"POINT({geocoded_address[1]} {geocoded_address[0]})")
        db.session.add(location)
        db.session.commit()

        address = Address.query.get_or_404(address.id)
        address.location = location
        db.session.commit()
    except Exception as error:
        print("Error", error)
        db.session.rollback()
        raise error

    return location

# endregion
