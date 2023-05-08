from enums import StatesEnum
from models import State, City, ZipCode, Address, Location
from util_filters import geocode_address


# region address helpers
def retrieve_state(state_str):
    """ Given a state string, return the state object from the db """
    try:
        # state = data['state']
        state_abbreviation = StatesEnum[state_str].value
        state_found_id = State.query.filter(State.state_abbreviation == state_abbreviation).first().id
        # USE ENUMS AS MUCH AS POSSIBLE TO CONTROL DATA IS ALWAYS CORRECT.
        state = State.query.get_or_404(state_found_id)

        return state
    except Exception as error:
        print("Error", error)


def retrieve_city(db, city_str, state):
    """ Given a city string, return the city object from the db """

    # TODO: write checker for city to confirm its actually a real city

    try:
        existing_city = City.query.filter(City.city_name == city_str).first()
        if existing_city is not None:
            city = existing_city
        else:
            new_city = City(city_name=city_str, state_uid=state.id)
            db.session.add(new_city)
            db.session.commit()
            city = new_city

        return city
    except Exception as error:
        print("Error", error)


def retrieve_zipcode(db, zipcode_str):
    """ Given a zipcode string, return the zipcode object from the db """

    # TODO: write checker for zipcode to confirm its actually a real zipcode
    try:
        zipcode = str(zipcode_str)
        existing_zipcode = ZipCode.query.filter(ZipCode.code == zipcode).first()
        if existing_zipcode is not None:
            zipcode = existing_zipcode
        else:
            new_zipcode = ZipCode(code=zipcode)
            db.session.add(new_zipcode)
            db.session.commit()
            zipcode = new_zipcode

        return zipcode
    except Exception as error:
        print("Error", error)


def retrieve_address(db, user, address_str, city, state, zipcode):
    """ Given a address string, return the address object from the db """

    # TODO: write checker for address to confirm its actually a real address

    try:
        address = Address(
            user_id=user.user_uid,
            street_address=address_str,
            city_uid=city.id,
            zipcode_uid=zipcode.id
        )
        db.session.add(address)
        db.session.commit()

        user.address_uid = address.address_uid
        db.session.commit()

        return address, city, state, zipcode
    except Exception as error:
        print("Error", error)


def retrieve_location(db, address, full_address_str):
    """ Given a location string, return the location object from the db """

    try:
        # address_string = f"{address.street_address} {city.city_name}, {state.state_abbreviation} {zipcode.code}"
        geocoded_address = geocode_address(full_address_str)
        location = Location(address_id=address.address_uid, point=f"POINT({geocoded_address[1]} {geocoded_address[0]})")
        db.session.add(location)
        db.session.commit()

        db.flush()
        address.latlong_uid = location.id
        db.session.commit()

        return location
    except Exception as error:
        print("Error", error)



# endregion
